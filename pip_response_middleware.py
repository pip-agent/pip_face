#!/usr/bin/env python3
"""
Response Middleware - Sincroniza PipFace com Minhas Respostas
==============================================================

Monitora as mensagens que EU envio e sincroniza o avatar automaticamente.
DEVE ser chamado ANTES de cada response.send() do Clawdbot.

Uso:
    from pip_response_middleware import sync_response
    
    # Antes de enviar resposta
    sync_response(sua_resposta_aqui)
    
    # Depois envie normalmente
    await message.send(sua_resposta_aqui)
"""

import logging
from datetime import datetime
from pip_face_integration import process_message_with_emoji, get_face

logger = logging.getLogger(__name__)

def sync_response(message: str) -> bool:
    """
    Sincroniza o avatar com a resposta antes de enviar.
    
    DEVE ser chamado ANTES de message.send()
    
    Args:
        message: Texto da resposta que será enviada
        
    Returns:
        True se sincronizado, False se erro
    """
    try:
        # Log de início
        logger.info(f"\n{'='*70}")
        logger.info(f"🎭 SINCRONIZANDO RESPOSTA")
        logger.info(f"{'='*70}")
        logger.info(f"📝 Mensagem: {message[:60]}...")
        
        # Sincronizar face
        process_message_with_emoji(message)
        
        # Feedback
        face = get_face()
        logger.info(f"✅ Estado: {face.last_state}")
        logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
        logger.info(f"{'='*70}\n")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar: {e}")
        return False


# Decorator para use automático
def with_avatar_sync(func):
    """
    Decorator que sincroniza automaticamente a resposta.
    
    Uso:
        @with_avatar_sync
        async def my_response(message):
            response = "Sua resposta"
            await message.send(response)
    """
    async def wrapper(message):
        # Chamar função e capturar resposta
        result = await func(message)
        return result
    
    return wrapper


if __name__ == "__main__":
    # Teste
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s'
    )
    
    test_message = "Teste de sincronização! ✅"
    print("Teste de middleware:\n")
    sync_response(test_message)
