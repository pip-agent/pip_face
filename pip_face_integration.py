#!/usr/bin/env python3
"""
Integração Completa do PipFace com Clawdbot
=============================================

Sistema de controle automático do avatar Pip durante processamento de mensagens.
Implementa hooks e callbacks para sincronizar expressões com atividades.

Uso:
    from pip_face_integration import PipFaceControl, get_face, setup_hooks
    
    # Inicializar
    face = get_face()
    setup_hooks()  # Configurar observadores automáticos
    
    # Usar manualmente
    face.thinking()      # Processando
    face.speaking()      # Respondendo
    face.happy()         # Sucesso
    face.error()         # Erro
    face.idle()          # Normal
"""

import socket
import json
import logging
import asyncio
import time
import threading
from typing import Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class PipFaceControl:
    """Interface de controle do PipFace com sincronização automática."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5555, auto_idle_timeout: int = 30):
        """
        Inicializa o controlador do PipFace.
        
        Args:
            host: Endereço do servidor PipFace
            port: Porta UDP
            auto_idle_timeout: Segundos para retornar a idle após atividade
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.auto_idle_timeout = auto_idle_timeout
        self.last_state = "idle"
        self.last_activity = time.time()
        self._auto_idle_task = None
        self._idle_timer = None
        
        logger.info(f"PipFaceControl inicializado (porta {port})")
    
    def send(self, **kwargs) -> bool:
        """Envia comando para PipFace via UDP."""
        try:
            cmd = json.dumps(kwargs)
            self.sock.sendto(cmd.encode("utf-8"), (self.host, self.port))
            self.last_state = kwargs.get("state", self.last_state)
            self.last_activity = time.time()
            logger.debug(f"PipFace: {cmd}")
            return True
        except Exception as e:
            logger.warning(f"Erro ao enviar comando PipFace: {e}")
            return False
    
    # =========================================================================
    # Estados Principais
    # =========================================================================
    
    def idle(self):
        """Face em repouso (cancela qualquer timer pendente)."""
        # Cancelar timer se existir
        if self._idle_timer is not None:
            self._idle_timer.cancel()
            self._idle_timer = None
        self.send(state="idle")
    
    def thinking(self, duration: int = 2):
        """Face pensando (processando input - volta ao idle após duration)."""
        self.send(state="thinking")
        self._schedule_idle(duration)
    
    def speaking(self, amplitude: float = 0.0, duration: int = 1):
        """Face falando (volta ao idle após duration)."""
        self.send(state="speaking", amplitude=amplitude)
        self._schedule_idle(duration)
    
    def working(self, duration: int = 2):
        """Face em trabalho longo (volta ao idle após duration)."""
        self.send(state="working")
        self._schedule_idle(duration)
    
    def happy(self, duration: int = 2):
        """Face feliz com duração automática."""
        self.send(state="happy", particle="heart")
        self._schedule_idle(duration)
    
    def error(self, duration: int = 3):
        """Face com erro."""
        self.send(state="error")
        self._schedule_idle(duration)
    
    def sleeping(self):
        """Face dormindo."""
        self.send(state="sleeping")
    
    def particle(self, particle_type: str):
        """Emitir partícula."""
        self.send(particle=particle_type)
    
    # =========================================================================
    # Utilidades
    # =========================================================================
    
    def _schedule_idle(self, delay: int):
        """Agenda retorno a idle após delay (usa threading, não async)."""
        # Cancelar timer anterior se existir
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        
        def return_to_idle():
            logger.debug(f"⏰ Timer disparou após {delay}s, estado atual: {self.last_state}")
            if self.last_state != "idle":
                logger.info(f"⏰ Retornando ao idle (era {self.last_state})...")
                self.idle()
            else:
                logger.debug("⏰ Já estava em idle, nada a fazer")
        
        # Criar thread de timer - NÃO usar time.sleep aqui!
        self._idle_timer = threading.Timer(delay, return_to_idle)
        self._idle_timer.daemon = True
        self._idle_timer.start()
        logger.debug(f"⏰ Timer agendado para {delay}s")
    
    def reset(self):
        """Resetar ao estado idle."""
        self.idle()


# Instância global
_face_instance = None


def get_face() -> PipFaceControl:
    """Retorna a instância global."""
    global _face_instance
    if _face_instance is None:
        _face_instance = PipFaceControl()
    return _face_instance


# =========================================================================
# Sistema de Hooks - Automação
# =========================================================================

class PipFaceHooks:
    """Sistema de callbacks para automação do avatar."""
    
    def __init__(self, face: PipFaceControl):
        self.face = face
        self.message_handlers = []
        self.response_handlers = []
        self.error_handlers = []
    
    def on_message_received(self, callback: Callable):
        """Registrar callback quando mensagem é recebida."""
        self.message_handlers.append(callback)
        return callback
    
    def on_response_start(self, callback: Callable):
        """Registrar callback quando resposta inicia."""
        self.response_handlers.append(callback)
        return callback
    
    def on_error(self, callback: Callable):
        """Registrar callback ao erro."""
        self.error_handlers.append(callback)
        return callback
    
    async def trigger_message_received(self):
        """Dispara callbacks de mensagem recebida."""
        self.face.thinking()
        for handler in self.message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Erro em message handler: {e}")
    
    async def trigger_response_start(self):
        """Dispara callbacks de início de resposta."""
        self.face.speaking()
        for handler in self.response_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Erro em response handler: {e}")
    
    async def trigger_error(self, error: Exception):
        """Dispara callbacks de erro."""
        self.face.error()
        for handler in self.error_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error)
                else:
                    handler(error)
            except Exception as e:
                logger.error(f"Erro em error handler: {e}")


# Instância global de hooks
_hooks_instance = None


def get_hooks() -> PipFaceHooks:
    """Retorna sistema de hooks."""
    global _hooks_instance
    if _hooks_instance is None:
        _hooks_instance = PipFaceHooks(get_face())
    return _hooks_instance


def setup_hooks():
    """Configurar hooks padrão automáticos."""
    hooks = get_hooks()
    
    # Hook padrão: idle após resposta
    @hooks.on_response_start()
    async def auto_idle_after_response():
        await asyncio.sleep(2)
        get_face().idle()
    
    logger.info("PipFace hooks configurados")


# =========================================================================
# Decoradores para Automação
# =========================================================================

def track_thinking(func: Callable) -> Callable:
    """Decorator: mostra thinking enquanto executa."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        face = get_face()
        face.thinking()
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            return result
        except Exception as e:
            face.error()
            raise
    return wrapper


def track_working(func: Callable) -> Callable:
    """Decorator: mostra working enquanto executa."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        face = get_face()
        face.working()
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            face.happy()
            return result
        except Exception as e:
            face.error()
            raise
    return wrapper


# =========================================================================
# Teste
# =========================================================================

def process_message_with_emoji(message: str) -> None:
    """
    Processa mensagem e sincroniza face com emojis.
    
    Deve ser chamado ANTES de enviar qualquer resposta.
    """
    from pip_message_hook import process_message
    process_message(message)


if __name__ == "__main__":
    import time
    
    face = get_face()
    
    print("Testando integração PipFace...")
    
    face.thinking()
    time.sleep(2)
    
    face.speaking(amplitude=0.5)
    time.sleep(2)
    
    face.happy(duration=2)
    time.sleep(3)
    
    face.idle()
    print("✅ Integração funcionando!")
