#!/usr/bin/env python3
"""
PIP FACE v2.1 - Face Animada para Moltbot
==========================================
Features:
- Controle externo via socket (porta 5555)
- Interpolação suave entre estados
- Olhos quadrados estilo Minecraft com pupilas
- Sobrancelhas expressivas
- Boca quadrada
- Blush/rubor animado
- Partículas (só em estados específicos, não no idle)
- System tray com menu
- Drag para mover janela
- Persistência de posição da janela
- FPS adaptativo (20 idle/sleeping, 30 ativo)
- Micro-saccades quando mouse longe
- Estados: idle, sleeping, speaking, thinking, surprised, confused, happy, error, working

Comandos via socket (JSON):
    {"state": "idle"}
    {"state": "speaking", "amplitude": 0.5}
    {"emotion": "happy"}
    {"particle": "heart"}
"""

import sys
import os
import math
import random
import json
import socket
import threading
import platform
import time
from dataclasses import dataclass, field
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal, QObject, QSettings
from PyQt6.QtGui import (
    QPainter, QColor, QPainterPath, QFont, QPen,
    QIcon, QPixmap, QCursor, QAction, QFontDatabase
)

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
CONFIG = {
    "socket_port": 5555,
    "window_width": 400,
    "window_height": 300,
    "fps_active": 30,  # FPS para estados ativos
    "fps_idle": 20,  # FPS para idle/sleeping
    "face_color": (255, 145, 145),
    "face_color_error": (255, 100, 100),
    "face_color_working": (255, 160, 130),
    "eye_color": (0, 0, 0),
    "pupil_color": (40, 40, 40),
    "blush_color": (255, 100, 100, 80),
    "brow_color": (60, 40, 40),
    "saccade_distance": 400,  # Distância do mouse pra ativar micro-saccades
}

# Estados que usam FPS baixo
LOW_FPS_STATES = {"idle", "sleeping"}

# Estados que emitem partículas automaticamente
# (tipo, cooldown em segundos, quantidade)
PARTICLE_STATES = {
    "sleeping": ("zzz", 2.5, 1),
    "thinking": ("bubble", 0.5, 3),  # Mais bolhinhas, mais frequente
}


# =============================================================================
# UTILIDADES
# =============================================================================
def lerp(a: float, b: float, t: float) -> float:
    """Interpolação linear."""
    return a + (b - a) * min(max(t, 0), 1)


def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Interpolação de cor."""
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(len(c1)))


def get_emoji_font() -> str:
    """Retorna fonte de emoji apropriada pro sistema."""
    system = platform.system()
    if system == "Windows":
        return "Segoe UI Emoji"
    elif system == "Darwin":  # macOS
        return "Apple Color Emoji"
    else:  # Linux
        # Tentar fontes comuns no Linux
        candidates = ["Noto Color Emoji", "Noto Emoji", "EmojiOne", "Symbola"]
        available = QFontDatabase.families()
        for font in candidates:
            if font in available:
                return font
        return "Noto Color Emoji"  # Fallback padrão


# =============================================================================
# PARTÍCULAS
# =============================================================================
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    symbol: str
    size: float
    color: tuple = (255, 100, 150)

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy -= 50 * dt  # Gravidade invertida (sobe)
        self.life -= dt
        return self.life > 0

    @property
    def alpha(self) -> int:
        return int(255 * (self.life / self.max_life))


class ParticleSystem:
    SYMBOLS = {
        "heart": "♥",
        "question": "?",
        "exclaim": "!",
        "dots": "...",
        "star": "★",
        "sweat": "💧",
        "zzz": "Z",
        "gear": "⚙",
        "bubble": "○",  # Bolinha de pensamento
    }

    def __init__(self):
        self.particles: list[Particle] = []
        self.emoji_font = get_emoji_font()

    def emit(self, x: float, y: float, symbol: str, count: int = 1):
        sym = self.SYMBOLS.get(symbol, symbol)
        colors = {
            "heart": (255, 100, 150),
            "question": (100, 150, 255),
            "exclaim": (255, 200, 50),
            "star": (255, 230, 100),
            "sweat": (100, 200, 255),
            "zzz": (150, 150, 200),
            "dots": (60, 60, 60),
            "gear": (150, 150, 150),
            "bubble": (100, 100, 120),  # Cinza azulado para bolhinhas
        }
        color = colors.get(symbol, (200, 200, 200))

        for _ in range(count):
            # Bolhas sobem (vy negativo), outras partículas comportamento padrão
            if symbol == "bubble":
                vy = random.uniform(-80, -40)  # Negativo = sobe
                vx = random.uniform(-15, 15)   # Menos movimento lateral
                size = random.uniform(12, 24)
            else:
                vy = random.uniform(40, 80)
                vx = random.uniform(-30, 30)
                size = random.uniform(16, 28)
            
            self.particles.append(Particle(
                x=x + random.uniform(-30, 30),
                y=y,
                vx=vx,
                vy=vy,
                life=random.uniform(1.5, 2.5),
                max_life=2.5,
                symbol=sym,
                size=size,
                color=color,
            ))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, painter: QPainter):
        for p in self.particles:
            painter.setFont(QFont(self.emoji_font, int(p.size)))
            color = QColor(*p.color, p.alpha)
            painter.setPen(color)
            painter.drawText(int(p.x), int(p.y), p.symbol)


# =============================================================================
# ESTADOS E EXPRESSÕES
# =============================================================================
@dataclass
class FaceState:
    """Estado atual da face com valores animáveis."""
    # Olhos
    eye_open: float = 1.0  # 0 = fechado, 1 = aberto
    eye_size: float = 1.0  # Escala dos olhos
    pupil_x: float = 0.0  # Offset da pupila (-1 a 1)
    pupil_y: float = 0.0
    pupil_size: float = 0.5  # Tamanho relativo da pupila

    # Sobrancelhas
    brow_left_y: float = 0.0  # Offset Y (-1 = baixo/raiva, 1 = alto/surpresa)
    brow_right_y: float = 0.0
    brow_left_angle: float = 0.0  # Ângulo em graus
    brow_right_angle: float = 0.0

    # Boca
    mouth_open: float = 0.0  # 0 = fechada, 1 = aberta
    mouth_width: float = 0.6  # Largura relativa
    mouth_curve: float = 0.0  # -1 = triste, 0 = neutro, 1 = sorriso

    # Geral
    face_color: tuple = field(default_factory=lambda: CONFIG["face_color"])
    blush_alpha: float = 0.0  # 0 = sem rubor, 1 = rubor máximo
    shake: float = 0.0  # Intensidade do tremor
    float_y: float = 0.0  # Flutuação vertical


# Definição de expressões predefinidas
# ATIVOS: sleeping, idle, speaking, thinking
EXPRESSIONS = {
    "idle": FaceState(
        eye_open=1.0, mouth_curve=0.1, mouth_open=0.0,
        brow_left_y=0.0, brow_right_y=0.0
    ),
    "sleeping": FaceState(
        eye_open=0.0, mouth_curve=0.0, mouth_open=0.0,
        brow_left_y=-0.2, brow_right_y=-0.2
    ),
    "speaking": FaceState(
        eye_open=1.0, mouth_curve=0.2, mouth_open=0.3,
        brow_left_y=0.1, brow_right_y=0.1
    ),
    "thinking": FaceState(
        eye_open=0.9, mouth_curve=0.0, mouth_open=0.0,
        pupil_x=0.5, pupil_y=-0.3,
        brow_left_y=0.3, brow_right_y=0.0,
        brow_left_angle=10, brow_right_angle=0
    ),
    # "working": FaceState(
    #     eye_open=1.0, mouth_curve=0.0, mouth_open=0.0,
    #     pupil_x=0.0, pupil_y=0.1,
    #     brow_left_y=0.1, brow_right_y=0.1,
    #     brow_left_angle=0, brow_right_angle=0,
    #     face_color=CONFIG["face_color_working"]
    # ),
    # "surprised": FaceState(
    #     eye_open=1.0, eye_size=1.3, mouth_curve=0.0, mouth_open=0.8,
    #     brow_left_y=0.6, brow_right_y=0.6,
    #     pupil_size=0.3, shake=5.0
    # ),
    # "confused": FaceState(
    #     eye_open=1.0, mouth_curve=-0.2, mouth_open=0.1,
    #     pupil_x=0.3, pupil_y=0.2,
    #     brow_left_y=0.4, brow_right_y=-0.1,
    #     brow_left_angle=15, brow_right_angle=-5
    # ),
    # "happy": FaceState(
    #     eye_open=0.3, mouth_curve=0.8, mouth_open=0.2, mouth_width=0.8,
    #     brow_left_y=0.2, brow_right_y=0.2,
    #     blush_alpha=0.8
    # ),
    # "error": FaceState(
    #     eye_open=0.0, mouth_curve=-0.5, mouth_open=0.0,
    #     brow_left_y=-0.3, brow_right_y=-0.3,
    #     brow_left_angle=-20, brow_right_angle=20,
    #     face_color=CONFIG["face_color_error"], shake=3.0
    # ),
}


# =============================================================================
# COMUNICAÇÃO SOCKET
# =============================================================================
class SocketSignals(QObject):
    command_received = pyqtSignal(dict)


class SocketServer(threading.Thread):
    def __init__(self, port: int, signals: SocketSignals):
        super().__init__(daemon=True)
        self.port = port
        self.signals = signals
        self.running = True
        self.socket: Optional[socket.socket] = None

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("127.0.0.1", self.port))
        self.socket.settimeout(0.5)

        while self.running:
            try:
                data, _ = self.socket.recvfrom(1024)
                try:
                    cmd = json.loads(data.decode("utf-8"))
                    self.signals.command_received.emit(cmd)
                except json.JSONDecodeError:
                    pass
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Socket error: {e}")

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()


# =============================================================================
# WIDGET PRINCIPAL
# =============================================================================
class PipFace(QWidget):
    def __init__(self):
        super().__init__()

        # Estado
        self.current_state = FaceState()
        self.target_state = FaceState()
        self.state_name = "idle"
        self.tick = 0
        self.current_fps = CONFIG["fps_idle"]
        self.dt = 1.0 / self.current_fps

        # Animação
        self.blink_timer = 0
        self.blink_duration = 0
        self.speech_amplitude = 0.0
        self.mouse_pos = QPointF(0, 0)

        # Micro-saccades
        self.saccade_timer = 0
        self.saccade_offset_x = 0.0
        self.saccade_offset_y = 0.0

        # Partículas
        self.particles = ParticleSystem()
        self.particle_cooldown = 0

        # Drag
        self.drag_pos = None

        # Auto-sleep (10 minutos de inatividade)
        self.last_activity_time = time.time()
        self.auto_sleep_timeout = 300  # 5 minutos em segundos
        self.is_sleeping = False

        # Settings (persistência)
        self.settings = QSettings("MoltBot", "PipFace")

        # Socket
        self.socket_signals = SocketSignals()
        self.socket_signals.command_received.connect(self.handle_command)
        self.socket_server = SocketServer(CONFIG["socket_port"], self.socket_signals)
        self.socket_server.start()

        self.init_ui()
        self.init_tray()
        self.load_position()

        # Timer principal
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.update_fps()

        # Definir estado inicial
        self.set_state("idle")

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        self.setMouseTracking(True)

    def init_tray(self):
        # Criar ícone para o tray
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(*CONFIG["face_color"]))
        icon = QIcon(pixmap)

        self.tray = QSystemTrayIcon(icon, self)

        menu = QMenu()

        # Estados
        states_menu = menu.addMenu("Estado")
        for state in EXPRESSIONS.keys():
            action = QAction(state.capitalize(), self)
            action.triggered.connect(lambda checked, s=state: self.set_state(s))
            states_menu.addAction(action)

        # Partículas
        particles_menu = menu.addMenu("Partícula")
        for particle in ParticleSystem.SYMBOLS.keys():
            action = QAction(particle.capitalize(), self)
            action.triggered.connect(lambda checked, p=particle: self.emit_particle(p))
            particles_menu.addAction(action)

        menu.addSeparator()

        # Reset posição
        reset_action = QAction("Resetar Posição", self)
        reset_action.triggered.connect(self.reset_position)
        menu.addAction(reset_action)

        # Sair
        quit_action = QAction("Sair", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def load_position(self):
        """Carrega posição salva da janela. Se não existir, coloca no canto superior direito."""
        pos = self.settings.value("window_pos")
        if pos:
            self.move(pos)
        else:
            # Primeira vez: canto superior direito
            self.reset_position()

    def save_position(self):
        """Salva posição atual da janela."""
        self.settings.setValue("window_pos", self.pos())

    def reset_position(self):
        """Reseta posição para o canto superior direito (30px de margem)."""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 30
        y = 30
        self.move(x, y)
        self.save_position()

    def update_fps(self):
        """Ajusta FPS baseado no estado atual."""
        target_fps = CONFIG["fps_idle"] if self.state_name in LOW_FPS_STATES else CONFIG["fps_active"]

        if target_fps != self.current_fps:
            self.current_fps = target_fps
            self.dt = 1.0 / self.current_fps
            self.timer.stop()
            self.timer.start(int(1000 / self.current_fps))
        elif not self.timer.isActive():
            self.timer.start(int(1000 / self.current_fps))

    def quit_app(self):
        self.save_position()
        self.socket_server.stop()
        self.tray.hide()
        QApplication.quit()

    # -------------------------------------------------------------------------
    # COMANDOS
    # -------------------------------------------------------------------------
    def handle_command(self, cmd: dict):
        """Processa comandos recebidos via socket."""
        # Resetar timer de inatividade quando receber qualquer comando
        self.last_activity_time = time.time()
        
        # Se estava dormindo, acordar
        if self.state_name == "sleeping":
            self.set_state("idle")
        
        if "state" in cmd:
            self.set_state(cmd["state"])

        if "amplitude" in cmd:
            self.speech_amplitude = float(cmd["amplitude"])

        if "emotion" in cmd:
            self.set_state(cmd["emotion"])

        if "particle" in cmd:
            self.emit_particle(cmd["particle"])
        
        # Enviar feedback de confirmação
        self._send_feedback(cmd)

    def set_state(self, state_name: str):
        """Define o estado alvo para interpolação."""
        if state_name in EXPRESSIONS:
            old_state = self.state_name
            self.state_name = state_name
            expr = EXPRESSIONS[state_name]
            # Copiar valores da expressão para o target
            for attr in vars(expr):
                if not attr.startswith("_"):
                    setattr(self.target_state, attr, getattr(expr, attr))

            # Ajustar FPS se mudou de categoria
            if (old_state in LOW_FPS_STATES) != (state_name in LOW_FPS_STATES):
                self.update_fps()

    def emit_particle(self, particle_type: str, count: int = 3):
        """Emite partículas."""
        w, h = self.width(), self.height()
        self.particles.emit(w // 2, h // 3, particle_type, count)
    
    def _send_feedback(self, cmd: dict):
        """Envia feedback de confirmação do comando."""
        try:
            feedback = {
                "status": "✅ Animação ativa",
                "state": self.state_name,
                "command": cmd.get("state", "unknown"),
                "timestamp": time.time()
            }
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(json.dumps(feedback).encode(), ("127.0.0.1", 5556))
            sock.close()
        except Exception as e:
            print(f"Erro ao enviar feedback: {e}")

    # -------------------------------------------------------------------------
    # ANIMAÇÃO
    # -------------------------------------------------------------------------
    def update_animation(self):
        self.tick += 1
        dt = self.dt

        # Verificar inatividade - dormir após 10 minutos
        if self.state_name != "sleeping":
            elapsed = time.time() - self.last_activity_time
            if elapsed > self.auto_sleep_timeout:
                self.set_state("sleeping")

        # Interpolar estado atual para o alvo
        lerp_speed = 8.0 * dt
        for attr in ["eye_open", "eye_size", "pupil_x", "pupil_y", "pupil_size",
                     "brow_left_y", "brow_right_y", "brow_left_angle", "brow_right_angle",
                     "mouth_open", "mouth_width", "mouth_curve", "blush_alpha", "shake"]:
            current = getattr(self.current_state, attr)
            target = getattr(self.target_state, attr)
            setattr(self.current_state, attr, lerp(current, target, lerp_speed))

        # Interpolar cor
        current_color = self.current_state.face_color
        target_color = self.target_state.face_color
        self.current_state.face_color = lerp_color(current_color, target_color, lerp_speed)

        # Flutuação (sempre ativa)
        if self.state_name == "sleeping":
            self.current_state.float_y = math.sin(self.tick * 0.02) * 12
        elif self.state_name == "speaking":
            self.current_state.float_y = math.sin(self.tick * 0.08) * 6
        elif self.state_name == "working":
            self.current_state.float_y = math.sin(self.tick * 0.03) * 3  # Bem sutil
        else:
            self.current_state.float_y = math.sin(self.tick * 0.04) * 4

        # Piscada
        if self.state_name not in ["sleeping", "happy", "error"]:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                if random.random() < 0.015:  # ~1.5% chance por frame
                    self.blink_duration = 0.15
                    self.blink_timer = random.uniform(3.0, 6.0)

            if self.blink_duration > 0:
                self.blink_duration -= dt
                self.current_state.eye_open = 0.1

        # Fala - modulação da boca (50% mais rápida)
        if self.state_name == "speaking":
            if self.speech_amplitude > 0:
                self.current_state.mouth_open = 0.2 + self.speech_amplitude * 0.6
            else:
                if self.tick % 5 == 0:  # Era 8, agora 5 (50% mais rápido)
                    self.target_state.mouth_open = random.uniform(0.2, 0.7)

        # Pupilas SEMPRE seguem o mouse ("o que esse arrombado tá fazendo?")
        if self.state_name in ["idle", "speaking"]:
            global_mouse = QCursor.pos()
            local_mouse = self.mapFromGlobal(global_mouse)
            center = QPointF(self.width() / 2, self.height() / 3)
            delta = QPointF(local_mouse) - center
            max_offset = 200
            self.target_state.pupil_x = max(-1, min(1, delta.x() / max_offset))
            self.target_state.pupil_y = max(-1, min(1, delta.y() / max_offset))

        # Working: olhos focados no centro com leve variação
        if self.state_name == "working":
            self.target_state.pupil_x = math.sin(self.tick * 0.02) * 0.1
            self.target_state.pupil_y = 0.1 + math.sin(self.tick * 0.015) * 0.05

        # Partículas automáticas (SÓ em estados específicos, NÃO no idle)
        if self.state_name in PARTICLE_STATES:
            self.particle_cooldown -= dt
            if self.particle_cooldown <= 0:
                particle_type, cooldown, count = PARTICLE_STATES[self.state_name]
                self.emit_particle(particle_type, count)
                self.particle_cooldown = cooldown

        # Atualizar partículas
        self.particles.update(dt)

        self.update()

    # -------------------------------------------------------------------------
    # DESENHO
    # -------------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        state = self.current_state

        # Offset de flutuação e shake
        float_y = state.float_y
        shake_x = random.uniform(-state.shake, state.shake) if state.shake > 0.1 else 0
        shake_y = random.uniform(-state.shake, state.shake) if state.shake > 0.1 else 0

        offset_x = shake_x
        offset_y = float_y + shake_y

        # === FUNDO (FACE) ===
        face_rect = QRectF(10 + offset_x, 10 + offset_y, w - 20, h - 20)
        painter.setBrush(QColor(*state.face_color[:3]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(face_rect, 40, 40)

        # === BLUSH ===
        if state.blush_alpha > 0.05:
            blush_color = QColor(*CONFIG["blush_color"][:3], int(state.blush_alpha * 100))
            painter.setBrush(blush_color)
            painter.drawEllipse(QPointF(w * 0.2 + offset_x, h * 0.55 + offset_y), 30, 20)
            painter.drawEllipse(QPointF(w * 0.8 + offset_x, h * 0.55 + offset_y), 30, 20)

        # === OLHOS ===
        eye_y = h * 0.35 + offset_y
        eye_left_x = w * 0.3 + offset_x
        eye_right_x = w * 0.7 + offset_x
        eye_base_radius = 28 * state.eye_size

        eye_height = eye_base_radius * state.eye_open
        eye_height = max(eye_height, 4)

        painter.setBrush(QColor(*CONFIG["eye_color"]))

        if state.eye_open > 0.2:
            # Olhos abertos (QUADRADOS - estilo Minecraft)
            eye_w = eye_base_radius * 2
            eye_h = eye_height * 2
            painter.drawRect(
                int(eye_left_x - eye_base_radius), int(eye_y - eye_height),
                int(eye_w), int(eye_h)
            )
            painter.drawRect(
                int(eye_right_x - eye_base_radius), int(eye_y - eye_height),
                int(eye_w), int(eye_h)
            )

            # Pupilas (quadradas também)
            if state.eye_open > 0.3:
                pupil_size = eye_base_radius * state.pupil_size * 0.8
                pupil_offset_x = state.pupil_x * eye_base_radius * 0.4
                pupil_offset_y = state.pupil_y * eye_height * 0.3

                painter.setBrush(QColor(*CONFIG["pupil_color"]))
                painter.drawRect(
                    int(eye_left_x + pupil_offset_x - pupil_size / 2),
                    int(eye_y + pupil_offset_y - pupil_size / 2),
                    int(pupil_size), int(pupil_size)
                )
                painter.drawRect(
                    int(eye_right_x + pupil_offset_x - pupil_size / 2),
                    int(eye_y + pupil_offset_y - pupil_size / 2),
                    int(pupil_size), int(pupil_size)
                )
        else:
            # Olhos fechados
            if self.state_name == "error":
                # Olhos X
                pen = QPen(QColor(*CONFIG["eye_color"]), 5)
                painter.setPen(pen)
                size = 20
                for ex in [eye_left_x, eye_right_x]:
                    painter.drawLine(
                        int(ex - size), int(eye_y - size),
                        int(ex + size), int(eye_y + size)
                    )
                    painter.drawLine(
                        int(ex + size), int(eye_y - size),
                        int(ex - size), int(eye_y + size)
                    )
            elif self.state_name == "happy":
                # Olhos ^ ^
                pen = QPen(QColor(*CONFIG["eye_color"]), 5)
                painter.setPen(pen)
                for ex in [eye_left_x, eye_right_x]:
                    path = QPainterPath()
                    path.moveTo(ex - 20, eye_y + 5)
                    path.quadTo(ex, eye_y - 15, ex + 20, eye_y + 5)
                    painter.drawPath(path)
            else:
                # Linha fechada
                pen = QPen(QColor(*CONFIG["eye_color"]), 4)
                painter.setPen(pen)
                painter.drawLine(int(eye_left_x - 20), int(eye_y), int(eye_left_x + 20), int(eye_y))
                painter.drawLine(int(eye_right_x - 20), int(eye_y), int(eye_right_x + 20), int(eye_y))

        # === SOBRANCELHAS ===
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*CONFIG["brow_color"]))

        brow_y_base = h * 0.22 + offset_y
        brow_width = 45
        brow_height = 8

        for i, (brow_x, brow_y_offset, brow_angle) in enumerate([
            (eye_left_x, state.brow_left_y, state.brow_left_angle),
            (eye_right_x, state.brow_right_y, state.brow_right_angle)
        ]):
            painter.save()
            brow_y = brow_y_base - brow_y_offset * 20
            painter.translate(brow_x, brow_y)
            angle = brow_angle if i == 0 else -brow_angle
            painter.rotate(angle)
            painter.drawRoundedRect(
                int(-brow_width / 2), int(-brow_height / 2),
                brow_width, brow_height, 4, 4
            )
            painter.restore()

        # === BOCA (QUADRADA - estilo Minecraft) ===
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*CONFIG["eye_color"]))

        mouth_x = w / 2 + offset_x
        mouth_y = h * 0.68 + offset_y
        mouth_w = 78 * state.mouth_width
        mouth_h = 13 + state.mouth_open * 52

        if state.mouth_open > 0.1:
            painter.drawRect(
                int(mouth_x - mouth_w / 2), int(mouth_y),
                int(mouth_w), int(mouth_h)
            )
        else:
            closed_h = max(4, int(8 + state.mouth_curve * 4))
            painter.drawRect(
                int(mouth_x - mouth_w / 2), int(mouth_y),
                int(mouth_w), closed_h
            )

        # === PARTÍCULAS ===
        self.particles.draw(painter)

    # -------------------------------------------------------------------------
    # EVENTOS
    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()

        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if self.drag_pos:
            self.save_position()
        self.drag_pos = None

    def keyPressEvent(self, event):
        # Apenas 3 estados ativos: sleeping, idle, speaking
        key_map = {
            Qt.Key.Key_1: "sleeping",
            Qt.Key.Key_2: "idle",
            Qt.Key.Key_3: "speaking",
            # Qt.Key.Key_4: "thinking",   # DESATIVADO
            # Qt.Key.Key_5: "surprised",  # DESATIVADO
            # Qt.Key.Key_6: "confused",   # DESATIVADO
            # Qt.Key.Key_7: "happy",      # DESATIVADO
            # Qt.Key.Key_8: "error",      # DESATIVADO
            # Qt.Key.Key_9: "working",    # DESATIVADO
        }

        if event.key() in key_map:
            self.set_state(key_map[event.key()])
        elif event.key() == Qt.Key.Key_Escape:
            self.quit_app()
        elif event.key() == Qt.Key.Key_H:
            self.emit_particle("heart", 5)
        elif event.key() == Qt.Key.Key_Q:
            self.emit_particle("question", 3)

    def closeEvent(self, event):
        self.quit_app()


# =============================================================================
# CLIENTE DE TESTE
# =============================================================================
def send_command(cmd: dict, port: int = CONFIG["socket_port"]):
    """Envia comando para a face via UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(cmd).encode("utf-8"), ("127.0.0.1", port))
    sock.close()


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = {}
        for arg in sys.argv[1:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                try:
                    value = float(value)
                except ValueError:
                    pass
                cmd[key] = value

        if cmd:
            send_command(cmd)
            print(f"Comando enviado: {cmd}")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = PipFace()
    window.show()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  PIP FACE v2.1 - Rodando na porta {CONFIG["socket_port"]}                      ║
╠══════════════════════════════════════════════════════════════╣
║  Teclas:                                                     ║
║    1 = sleeping                                              ║
║    2 = idle                                                  ║
║    3 = speaking                                              ║
║    H = corações   Q = interrogações   ESC = Sair             ║
╠══════════════════════════════════════════════════════════════╣
║  FPS: {CONFIG["fps_idle"]} (idle/sleep) | {CONFIG["fps_active"]} (ativo)                          ║
║  Posição da janela é salva automaticamente                   ║
╚══════════════════════════════════════════════════════════════╝
""")

    sys.exit(app.exec())