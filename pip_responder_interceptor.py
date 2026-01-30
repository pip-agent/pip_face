#!/usr/bin/env python3
"""
Responder Interceptor - Auto-Sincroniza Minhas Respostas
=========================================================

Monitora as mensagens que EU envio e sincroniza o avatar AUTOMATICAMENTE.
Não precisa fazer nada manual - funciona em background.

Execução:
    python3 pip_responder_interceptor.py
"""

import time
import logging
import os
from pathlib import Path
from pip_face_integration import process_message_with_emoji, get_face

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler('/tmp/pip_responder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResponderInterceptor:
    """Monitora e sincroniza minhas respostas automaticamente."""
    
    def __init__(self):
        self.gateway_log = Path.home() / ".clawdbot" / "gateway.log"
        self.last_pos = 0
        self.processed_messages = set()
        self.my_messages_count = 0
    
    def monitor(self):
        """Monitora arquivo de log continuamente."""
        if not self.gateway_log.exists():
            logger.warning(f"Log não encontrado: {self.gateway_log}")
            return
        
        logger.info(f"📡 Monitorando: {self.gateway_log}")
        logger.info("🎭 Interceptor de respostas ativo\n")
        
        while True:
            try:
                with open(self.gateway_log, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_pos)
                    lines = f.readlines()
                    self.last_pos = f.tell()
                
                for line in lines:
                    self._process_line(line)
                
                time.sleep(0.5)
            
            except Exception as e:
                logger.debug(f"Erro ao monitorar: {e}")
                time.sleep(1)
    
    def _process_line(self, line: str):
        """Processa linha do log para detectar minhas respostas."""
        try:
            # Detectar quando EU envio uma resposta
            if any(keyword in line for keyword in ["sent", "enviado", "→", "message"]):
                # Extrair mensagem
                if '"' in line:
                    # Tentar extrair conteúdo entre aspas
                    parts = line.split('"')
                    for i, part in enumerate(parts):
                        if len(part) > 10 and i > 0:  # Mensagem significativa
                            message = part.strip()
                            msg_hash = hash(message)
                            
                            # Evitar processar a mesma mensagem 2x
                            if msg_hash not in self.processed_messages:
                                self._sync_response(message)
                                self.processed_messages.add(msg_hash)
                                
                                # Limpar cache se ficar muito grande
                                if len(self.processed_messages) > 1000:
                                    self.processed_messages = set()
                            break
        
        except Exception as e:
            logger.debug(f"Erro ao processar linha: {e}")
    
    def _sync_response(self, message: str):
        """Sincroniza resposta com o avatar."""
        try:
            # Verificar se tem emoji ou palavras-chave
            if not self._should_sync(message):
                return
            
            logger.info(f"\n📨 RESPOSTA DETECTADA")
            logger.info(f"📝 {message[:60]}...")
            
            # Sincronizar face
            process_message_with_emoji(message)
            
            # Feedback
            face = get_face()
            logger.info(f"✅ Face: {face.last_state}")
            logger.info(f"{'='*70}\n")
            
            self.my_messages_count += 1
        
        except Exception as e:
            logger.debug(f"Erro ao sincronizar: {e}")
    
    def _should_sync(self, message: str) -> bool:
        """Verifica se deve sincronizar (tem emoji ou contexto)."""
        # Emojis comuns
        emoji_list = ['✅', '❌', '🤔', '💬', '⚙️', '🎉', '😄', '❓', '⚠️']
        
        # Palavras-chave
        keywords = ['pronto', 'erro', 'verificar', 'respondendo', 'processando', 'sucesso']
        
        message_lower = message.lower()
        
        # Se tem emoji, sincronizar
        for emoji in emoji_list:
            if emoji in message:
                return True
        
        # Se tem palavra-chave, sincronizar
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        # Se tem muita pontuação ou é pergunta, sincronizar
        if message.count('!') > 1 or message.count('?') > 0:
            return True
        
        return False
    
    def run(self):
        """Loop principal."""
        try:
            self.monitor()
        except KeyboardInterrupt:
            logger.info(f"\n\n🛑 Interceptor parado")
            logger.info(f"Mensagens sincronizadas: {self.my_messages_count}")


if __name__ == "__main__":
    interceptor = ResponderInterceptor()
    interceptor.run()
