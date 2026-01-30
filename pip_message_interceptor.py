#!/usr/bin/env python3
"""
Message Interceptor - Middleware de Integração
===============================================

Intercepta mensagens sendo enviadas e sincroniza o PipFace automaticamente.
Funciona monitorando logs e ativando expressões em tempo real.

Execução:
    python3 pip_message_interceptor.py
"""

import time
import re
import logging
from pathlib import Path
from pip_face_integration import get_face
from pip_message_hook import process_message

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class MessageInterceptor:
    """Intercepta e processa mensagens em tempo real."""
    
    def __init__(self):
        self.face = get_face()
        self.last_processed = 0
        self.processed_messages = set()
    
    def monitor_responses(self):
        """Monitora respostas siendo enviadas."""
        workspace = Path("/home/nl3mos/clawd")
        
        # Procurar por arquivos de log relevantes
        log_files = [
            Path.home() / ".clawdbot" / "gateway.log",
            Path.home() / ".clawdbot" / "agents" / "main" / "messages.log",
        ]
        
        for log_file in log_files:
            if log_file.exists():
                self._monitor_file(log_file)
    
    def _monitor_file(self, log_file: Path):
        """Monitora mudanças em um arquivo de log."""
        try:
            current_mtime = log_file.stat().st_mtime
            
            # Se arquivo foi modificado nos últimos 5 segundos
            if current_mtime > (time.time() - 5):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                    for line in reversed(lines[-50:]):  # Últimas 50 linhas
                        self._process_line(line)
        
        except Exception as e:
            logger.debug(f"Erro ao monitorar {log_file}: {e}")
    
    def _process_line(self, line: str):
        """Processa uma linha de log."""
        try:
            # Detectar respostas sendo enviadas
            if any(keyword in line.lower() for keyword in ["sent", "enviado", "response", "resposta"]):
                # Extrair mensagem
                message = self._extract_message(line)
                if message and len(message) > 5:
                    msg_hash = hash(message)
                    if msg_hash not in self.processed_messages:
                        logger.info(f"📨 Resposta detectada: {message[:50]}...")
                        process_message(message)
                        self.processed_messages.add(msg_hash)
        
        except Exception as e:
            logger.debug(f"Erro ao processar linha: {e}")
    
    def _extract_message(self, line: str) -> str:
        """Extrai mensagem de uma linha de log."""
        # Remover timestamps e formatação
        message = re.sub(r'^\[.*?\]\s*', '', line)
        message = re.sub(r'[^\w\s\d\:\-\.\,\!\?\'\"\✅❌😄🎉⚙️👍]', '', message)
        return message.strip()
    
    def run(self):
        """Loop principal do interceptor."""
        logger.info("🔗 Message Interceptor iniciado")
        logger.info("Monitorando respostas em tempo real...")
        
        try:
            while True:
                self.monitor_responses()
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Interceptor interrompido")
            self.face.idle()


if __name__ == "__main__":
    interceptor = MessageInterceptor()
    interceptor.run()
