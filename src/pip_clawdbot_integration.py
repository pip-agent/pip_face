#!/usr/bin/env python3
"""
Integração Profunda com Clawdbot
=================================

Intercepta message.send() para sincronizar automaticamente o PipFace.
Deve ser importado NO INÍCIO do código principal do Clawdbot.

Uso:
    import pip_clawdbot_integration
    pip_clawdbot_integration.setup()
"""

import logging
from pip_face_integration import process_message_with_emoji

logger = logging.getLogger(__name__)

# Armazenar função original
_original_send = None

def setup():
    """Configurar hook no Clawdbot."""
    global _original_send
    
    logger.info("🔗 Configurando integração PipFace com Clawdbot...")
    
    # Função wrapper que sincroniza ANTES de enviar
    def send_with_face_sync(*args, **kwargs):
        """Wrapper que sincroniza face ANTES de enviar mensagem."""
        try:
            # Extrair mensagem dos argumentos
            message = _extract_message(*args, **kwargs)
            
            if message:
                logger.info(f"🎭 Sincronizando face: {message[:50]}...")
                process_message_with_emoji(message)
        
        except Exception as e:
            logger.debug(f"Erro ao sincronizar: {e}")
        
        # Chamar função original
        return _original_send(*args, **kwargs)
    
    # Aplicar wrapper
    try:
        # Tentar interceptar via importação dinâmica
        import sys
        
        # Procurar pelo módulo de message do Clawdbot
        for module_name in list(sys.modules.keys()):
            if 'message' in module_name and 'clawdbot' in module_name:
                module = sys.modules[module_name]
                if hasattr(module, 'send'):
                    _original_send = module.send
                    module.send = send_with_face_sync
                    logger.info(f"✅ Hook instalado em {module_name}")
                    return True
        
        logger.warning("⚠️ Módulo de message do Clawdbot não encontrado")
        logger.info("Alternativa: chame process_message_with_emoji() manualmente antes de message.send()")
        return False
    
    except Exception as e:
        logger.error(f"Erro ao instalar hook: {e}")
        return False

def _extract_message(*args, **kwargs) -> str:
    """Extrai mensagem dos argumentos."""
    # Procurar em kwargs
    if 'message' in kwargs:
        return str(kwargs['message'])
    
    # Procurar em args
    for arg in args:
        if isinstance(arg, str):
            return arg
    
    return ""

if __name__ == "__main__":
    # Teste de setup
    logger.basicConfig(level=logging.INFO)
    setup()
    print("✅ Integração pronta para usar!")
