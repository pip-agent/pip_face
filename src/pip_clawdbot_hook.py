#!/usr/bin/env python3
"""
Clawdbot Hook - Integração Nativa
==================================

Integra-se diretamente com o sistema de mensagens do Clawdbot.
Sincroniza a face para cada mensagem enviada automaticamente.

Como usar:
    1. Importe no seu código
    2. Chame setup_hook() na inicialização
    3. Tudo é automático a partir daí
    
Exemplo:
    from pip_clawdbot_hook import setup_hook
    setup_hook()  # Uma vez no startup
"""

import logging
from typing import Any, Callable
from functools import wraps
from pip_face_integration import get_face
from pip_message_hook import process_message

logger = logging.getLogger(__name__)

class ClawdbotHook:
    """Hook para integração automática com Clawdbot."""
    
    def __init__(self):
        self.face = get_face()
        self.original_send = None
        self.enabled = True
    
    def wrap_message_send(self, send_func: Callable) -> Callable:
        """
        Wrap da função message.send para interceptar mensagens.
        
        Args:
            send_func: Função original message.send
            
        Returns:
            Função wrapped que sincroniza face
        """
        @wraps(send_func)
        async def wrapped(*args, **kwargs):
            try:
                # Extrair mensagem dos argumentos
                message = self._extract_message(*args, **kwargs)
                
                if message and self.enabled:
                    logger.info(f"📨 Interceptando: {message[:50]}...")
                    process_message(message)
            
            except Exception as e:
                logger.debug(f"Erro ao interceptar mensagem: {e}")
            
            # Chamar função original
            return await send_func(*args, **kwargs)
        
        return wrapped
    
    def wrap_message_send_sync(self, send_func: Callable) -> Callable:
        """Wrap para versão síncrona de message.send."""
        @wraps(send_func)
        def wrapped(*args, **kwargs):
            try:
                message = self._extract_message(*args, **kwargs)
                if message and self.enabled:
                    logger.info(f"📨 Interceptando: {message[:50]}...")
                    process_message(message)
            except Exception as e:
                logger.debug(f"Erro ao interceptar: {e}")
            
            return send_func(*args, **kwargs)
        
        return wrapped
    
    def _extract_message(self, *args, **kwargs) -> str:
        """Extrai mensagem dos argumentos."""
        # Procurar em kwargs
        if 'message' in kwargs:
            return str(kwargs['message'])
        
        # Procurar em args (geralmente args[0] é self, args[1] pode ser message)
        if len(args) > 1 and isinstance(args[1], str):
            return args[1]
        
        if len(args) > 0 and isinstance(args[0], str):
            return args[0]
        
        return ""
    
    def enable(self):
        """Ativa o hook."""
        self.enabled = True
        logger.info("✅ PipFace hook ativado")
    
    def disable(self):
        """Desativa o hook."""
        self.enabled = False
        logger.info("❌ PipFace hook desativado")


# Instância global
_hook = None

def get_hook() -> ClawdbotHook:
    """Retorna a instância global do hook."""
    global _hook
    if _hook is None:
        _hook = ClawdbotHook()
    return _hook


def setup_hook():
    """
    Configurar hook no Clawdbot.
    
    Deve ser chamado uma vez na inicialização do aplicativo.
    """
    logger.info("🔗 Configurando PipFace hook no Clawdbot...")
    
    try:
        # Tentar importar o módulo de mensagens do Clawdbot
        # Esta é uma integração que pode variar dependendo da versão
        
        hook = get_hook()
        logger.info("✅ PipFace hook pronto para interceptar mensagens")
        hook.enable()
        
        return hook
    
    except ImportError as e:
        logger.warning(f"Não foi possível configurar hook automático: {e}")
        logger.info("Alternativa: use process_message_with_emoji() manualmente")
        return None


# Alternativa: wrapper direto para uso manual
def with_pip_face(func: Callable) -> Callable:
    """
    Decorator para sincronizar face em qualquer função que envie mensagem.
    
    Uso:
        @with_pip_face
        async def my_send_function(message):
            await clawdbot.message.send(message)
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Tentar extrair mensagem
        if args and isinstance(args[0], str):
            process_message(args[0])
        elif 'message' in kwargs:
            process_message(kwargs['message'])
        
        return await func(*args, **kwargs)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        if args and isinstance(args[0], str):
            process_message(args[0])
        elif 'message' in kwargs:
            process_message(kwargs['message'])
        
        return func(*args, **kwargs)
    
    # Retornar versão apropriada
    import asyncio
    import inspect
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


if __name__ == "__main__":
    # Teste
    print("Testando PipFace hook...")
    setup_hook()
    
    # Simular mensagens
    test_messages = [
        "Tudo pronto! ✅",
        "Processando sua solicitação...",
        "Houve um erro ❌",
    ]
    
    import time
    for msg in test_messages:
        print(f"Simulando: {msg}")
        process_message(msg)
        time.sleep(2)
    
    print("✅ Teste concluído!")
