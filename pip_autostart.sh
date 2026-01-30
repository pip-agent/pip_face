#!/bin/bash
# Auto-start PipFace no boot

# Aguardar sistema estar pronto
sleep 5

# Iniciar PipFace
cd /home/nl3mos/clawd
python3 pip_face_v04.py > /tmp/pip_face.log 2>&1 &

# Iniciar Monitor
sleep 2
python3 pip_face_monitor.py > /tmp/pip_face_monitor.log 2>&1 &

# Iniciar Message Interceptor
sleep 1
python3 pip_message_interceptor.py > /tmp/pip_message_interceptor.log 2>&1 &

echo "$(date): PipFace, Monitor e Interceptor iniciados" >> /tmp/pip_autostart.log
