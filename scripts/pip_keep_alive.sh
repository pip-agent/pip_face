#!/bin/bash
# Keep-Alive para PipFace - Monitora e reinicia se necessário

WORKSPACE="/home/nl3mos/clawd"
PIDFILE="/tmp/pip_face.pid"

# Verificar se pip_face_v04 está rodando
if ! pgrep -f "python3 ${WORKSPACE}/pip_face_v04.py" > /dev/null; then
    echo "[$(date)] Reiniciando pip_face_v04..." >> /tmp/pip_keep_alive.log
    cd "$WORKSPACE"
    python3 pip_face_v04.py > /tmp/pip_face.log 2>&1 &
    sleep 2
fi

# Verificar se pip_face_monitor está rodando
if ! pgrep -f "python3 ${WORKSPACE}/pip_face_monitor.py" > /dev/null; then
    echo "[$(date)] Reiniciando pip_face_monitor..." >> /tmp/pip_keep_alive.log
    cd "$WORKSPACE"
    python3 pip_face_monitor.py > /tmp/pip_face_monitor.log 2>&1 &
    sleep 1
fi

# Verificar se pip_message_interceptor está rodando
if ! pgrep -f "python3 ${WORKSPACE}/pip_message_interceptor.py" > /dev/null; then
    echo "[$(date)] Reiniciando pip_message_interceptor..." >> /tmp/pip_keep_alive.log
    cd "$WORKSPACE"
    python3 pip_message_interceptor.py > /tmp/pip_message_interceptor.log 2>&1 &
fi

echo "[$(date)] Check concluído" >> /tmp/pip_keep_alive.log
