#!/usr/bin/env python3
"""
Pip Face Monitor v7 - Thinking + Speaking 3s
=============================================

- new=processing → THINKING
- tool start → THINKING  
- run_completed → SPEAKING (3s) → IDLE
- 300s em IDLE → SLEEPING
"""

import subprocess
import socket
import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[logging.FileHandler('/tmp/pip_monitor.log')]
)
log = logging.getLogger(__name__)

# Config
SLEEP_TIMEOUT = 300
SPEAKING_DURATION = 3
PIPFACE_PORT = 5555
LOG_DIR = Path("/tmp/clawdbot")


def get_today_log() -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"clawdbot-{today}.log"


def send_state(state: str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps({"state": state}).encode(), ("127.0.0.1", PIPFACE_PORT))
        sock.close()
    except Exception as e:
        log.error(f"Erro: {e}")


class Monitor:
    def __init__(self):
        self.state = "idle"
        self.idle_start = time.time()
        self.speaking_timer = None
    
    def set_state(self, new_state: str):
        if new_state != self.state:
            log.info(f"{self.state}→{new_state}")
            send_state(new_state)
            self.state = new_state
            
            if new_state == "idle":
                self.idle_start = time.time()
    
    def speak_then_idle(self):
        """Muda pra speaking, espera 3s, volta pra idle."""
        # Cancelar timer anterior se existir
        if self.speaking_timer:
            self.speaking_timer.cancel()
        
        self.set_state("speaking")
        
        def go_idle():
            self.set_state("idle")
        
        self.speaking_timer = threading.Timer(SPEAKING_DURATION, go_idle)
        self.speaking_timer.start()
    
    def check_sleep(self):
        if self.state == "idle" and self.idle_start:
            elapsed = time.time() - self.idle_start
            if elapsed >= SLEEP_TIMEOUT:
                self.set_state("sleeping")
                self.idle_start = None
    
    def run(self):
        log.info("=" * 50)
        log.info("🤖 PIP FACE MONITOR v7")
        log.info("thinking → speaking(3s) → idle")
        log.info("=" * 50)
        
        send_state("idle")
        log.info("Estado inicial: idle")
        
        log_file = get_today_log()
        log.info(f"Monitorando: {log_file}")
        
        process = subprocess.Popen(
            ["tail", "-f", "-n", "0", str(log_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            for line in process.stdout:
                # Início de processamento → THINKING
                if "new=processing" in line or "totalActive=1" in line:
                    if self.speaking_timer:
                        self.speaking_timer.cancel()
                    self.set_state("thinking")
                
                # Tool start → THINKING (reforça)
                elif "tool start:" in line:
                    if self.state != "thinking":
                        self.set_state("thinking")
                
                # Run completed → SPEAKING por 3s → IDLE
                elif "run_completed" in line or "totalActive=0" in line:
                    self.speak_then_idle()
                
                # Acordar de sleeping
                elif self.state == "sleeping" and ("new=processing" in line):
                    self.set_state("idle")
                
                # Verificar timeout de sleep
                self.check_sleep()
        
        except KeyboardInterrupt:
            log.info("🛑 Parado")
        finally:
            if self.speaking_timer:
                self.speaking_timer.cancel()
            process.terminate()


if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
