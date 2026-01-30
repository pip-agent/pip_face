#!/usr/bin/env python3
"""
PipFace Debug System - Feedback em Tempo Real
==============================================

Sistema bidirecional que envia comandos E recebe confirmação.
Permite que o Pip "veja" o que está acontecendo.

Fluxo:
1. Pip envia comando → PipFace na porta 5555
2. PipFace executa animação
3. PipFace envia resposta → Pip na porta 5556
4. Pip recebe feedback e registra
"""

import socket
import json
import threading
import time
import logging
from datetime import datetime

# Setup logging com timestamp detalhado
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/tmp/pip_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PipFaceDebug:
    """Sistema de debug com feedback real."""
    
    def __init__(self):
        self.command_port = 5555
        self.feedback_port = 5556
        self.feedback_listener = None
        self.last_state = "idle"
        self.last_animation = None
        
        # Iniciar listener de feedback
        self._start_feedback_listener()
    
    def _start_feedback_listener(self):
        """Inicia listener para feedback do PipFace."""
        def listen():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("127.0.0.1", self.feedback_port))
            sock.settimeout(1.0)
            
            logger.info(f"📡 Listener de feedback iniciado na porta {self.feedback_port}")
            
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    feedback = json.loads(data.decode('utf-8'))
                    self._process_feedback(feedback)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"Erro no listener: {e}")
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        self.feedback_listener = thread
    
    def _process_feedback(self, feedback: dict):
        """Processa feedback recebido do PipFace."""
        status = feedback.get("status")
        state = feedback.get("state")
        timestamp = feedback.get("timestamp")
        
        logger.info(f"✅ FEEDBACK: {status} | Estado: {state}")
        self.last_state = state
        self.last_animation = timestamp
    
    def send_command(self, state: str, **kwargs) -> bool:
        """Envia comando e aguarda feedback."""
        cmd = {"state": state, "timestamp": datetime.now().isoformat()}
        cmd.update(kwargs)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(json.dumps(cmd).encode(), ("127.0.0.1", self.command_port))
            sock.close()
            
            logger.info(f"📤 COMANDO ENVIADO: {state}")
            self.last_state = state
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao enviar comando: {e}")
            return False
    
    def log_session(self):
        """Registra estado atual da sessão."""
        logger.info("=" * 60)
        logger.info("📊 STATUS DA SESSÃO")
        logger.info("=" * 60)
        logger.info(f"Estado Atual: {self.last_state}")
        logger.info(f"Última Animação: {self.last_animation}")
        logger.info("=" * 60)
    
    def test_sequence(self):
        """Executa sequência de teste com debug completo."""
        logger.info("\n🧪 INICIANDO SEQUÊNCIA DE TESTE\n")
        
        tests = [
            ("speaking", "Falando"),
            ("thinking", "Pensando"),
            ("happy", "Feliz"),
            ("error", "Erro"),
            ("idle", "Repouso"),
        ]
        
        for state, label in tests:
            logger.info(f"\n▶️ Testando: {label}")
            self.send_command(state)
            time.sleep(2)
            self.log_session()
        
        logger.info("\n✅ Sequência concluída!\n")


if __name__ == "__main__":
    debug = PipFaceDebug()
    
    logger.info("🎭 PipFace Debug System ATIVO")
    logger.info("Recebendo feedback em tempo real na porta 5556\n")
    
    # Testar
    debug.test_sequence()
    
    # Manter listener ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Debug system parado")
