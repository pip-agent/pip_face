#!/usr/bin/env python3
"""
Message Hook - Sincroniza Face com Mensagens
==============================================

Intercepta mensagens que o Pip envia e sincroniza a face automaticamente.
Mapeia emojis para expressões faciais.

Integração automática com o pipeline de mensagens.
"""

from pip_face_integration import get_face
import re
from typing import Optional

# Mapeamento de emojis → estados da face
EMOJI_TO_FACE = {
    "😄": "happy",
    "😊": "happy",
    "🎉": "happy",
    "❤️": "happy",
    "💪": "happy",
    "✅": "happy",
    "🎭": "thinking",
    "🤔": "thinking",
    "💭": "thinking",
    "⚙️": "working",
    "🔄": "working",
    "🛠️": "working",
    "❌": "error",
    "😢": "error",
    "⚠️": "error",
    "😴": "sleeping",
    "🧘": "idle",
    "😐": "idle",
    "😕": "confused",
    "🤨": "confused",
    "😮": "surprised",
    "🎯": "speaking",
    "💬": "speaking",
    "📢": "speaking",
}

class MessageHook:
    """Hook para sincronizar mensagens com avatar."""
    
    def __init__(self):
        self.face = get_face()
        self.last_emoji = None
    
    def process_message(self, message: str) -> None:
        """
        Processa mensagem e sincroniza face.
        
        Args:
            message: Texto da mensagem
        """
        # Encontrar emoji na mensagem
        for emoji, face_state in EMOJI_TO_FACE.items():
            if emoji in message:
                self._apply_face_state(face_state, emoji)
                return
        
        # Se não encontrou emoji, usar heurística de contexto
        self._apply_smart_state(message)
    
    def _apply_face_state(self, state: str, emoji: str) -> None:
        """Aplica estado da face com base em emoji."""
        face = get_face()
        
        if state == "happy":
            face.happy(duration=1.5)
        elif state == "thinking":
            face.thinking(duration=2)
        elif state == "working":
            face.working(duration=2)
        elif state == "error":
            face.error(duration=1.5)
        elif state == "sleeping":
            face.sleeping()
        elif state == "idle":
            face.idle()
        elif state == "confused":
            face.send(state="confused")
            face._schedule_idle(1.5)
        elif state == "surprised":
            face.send(state="surprised")
            face._schedule_idle(1.5)
        elif state == "speaking":
            face.speaking(duration=1.5)
        
        self.last_emoji = emoji
    
    def _apply_smart_state(self, message: str) -> None:
        """Aplica estado inteligente baseado no conteúdo."""
        message_lower = message.lower()
        
        # Erros
        if any(word in message_lower for word in ["erro", "falha", "problema", "não", "nope", "failed"]):
            self.face.error(duration=1.5)
        
        # Sucesso/Felicidade
        elif any(word in message_lower for word in ["sucesso", "pronto", "concluído", "feito", "ok", "perfeito", "ótimo"]):
            self.face.happy(duration=1.5)
        
        # Trabalhando/Processando
        elif any(word in message_lower for word in ["processando", "aguarde", "carregando", "executando", "rodando"]):
            self.face.working(duration=2)
        
        # Pensando
        elif any(word in message_lower for word in ["deixa", "vou", "verificar", "analisando", "testando"]):
            self.face.thinking(duration=2)
        
        # Confuso
        elif any(word in message_lower for word in ["confuso", "não entendi", "?", "o quê"]):
            self.face.send(state="confused")
            self.face._schedule_idle(1.5)
        
        # Default: speaking
        else:
            self.face.speaking(duration=1.5)


# Instância global
_hook = None

def get_hook() -> MessageHook:
    """Retorna a instância global do hook."""
    global _hook
    if _hook is None:
        _hook = MessageHook()
    return _hook

def process_message(message: str) -> None:
    """Processa uma mensagem e sincroniza a face."""
    hook = get_hook()
    hook.process_message(message)


if __name__ == "__main__":
    # Teste
    hook = get_hook()
    
    test_messages = [
        "Sucesso! ✅",
        "Deu erro ❌",
        "Deixa eu verificar isso 🤔",
        "Pronto! 🎉",
        "Processando dados... ⚙️",
        "Não entendi a pergunta 😕",
    ]
    
    import time
    for msg in test_messages:
        print(f"Testando: {msg}")
        hook.process_message(msg)
        time.sleep(2)
    
    print("✅ Teste concluído!")
