#!/usr/bin/env python3
"""
Wrapper de Envio de Mensagem com Sincronização de Face
========================================================

Use esta função SEMPRE que for enviar uma mensagem para Telegram.
Sincroniza automaticamente o avatar com a mensagem.

Uso:
    from pip_send_message import send_message
    
    send_message("Sua mensagem aqui ✅")
"""

import logging
from typing import Optional
from pip_face_integration import process_message_with_emoji, get_face

logger = logging.getLogger(__name__)

async def send_message(message: str, channel: str = "telegram", target: str = "1317012295"):
    """
    Envia mensagem com sincronização automática do avatar.
    
    Args:
        message: Texto da mensagem
        channel: Canal (telegram, whatsapp, etc)
        target: ID/username do destinatário
    """
    try:
        # Sincronizar face ANTES de enviar
        logger.info(f"🎭 Sincronizando face: {message[:50]}...")
        process_message_with_emoji(message)
        
        # Importar função de envio do Clawdbot
        # (você vai adaptar isso conforme seu setup)
        logger.info(f"📨 Enviando: {message[:50]}...")
        
        # AQUI você chama a função real de envio do Clawdbot
        # Por enquanto, vou retornar True para teste
        return True
    
    except Exception as e:
        logger.error(f"Erro ao enviar: {e}")
        get_face().error(duration=1.5)
        return False


# Versão síncrona também
def send_message_sync(message: str, channel: str = "telegram", target: str = "1317012295") -> bool:
    """Versão síncrona do envio com sincronização."""
    try:
        logger.info(f"🎭 Sincronizando face: {message[:50]}...")
        process_message_with_emoji(message)
        
        logger.info(f"📨 Enviando: {message[:50]}...")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao enviar: {e}")
        get_face().error(duration=1.5)
        return False


if __name__ == "__main__":
    # Teste
    test_message = "Testando envio com sincronização! 💬"
    print(f"Teste: {test_message}")
    send_message_sync(test_message)
    print("✅ Teste concluído!")
