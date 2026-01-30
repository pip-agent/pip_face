# Pip Face Backup - v7 Funcional

## Arquivos
- pip_face_v04.py - Avatar PyQt6 com estados: sleeping, idle, speaking, thinking
- pip_face_monitor.py - Monitor v7 baseado em eventos do log do Clawdbot
- pipface.service - Serviço systemd do avatar
- pipface-monitor.service - Serviço systemd do monitor

## Estados
- sleeping: 5 min inativo, partículas ZzZ
- idle: esperando
- speaking: respondendo (3s após terminar)
- thinking: processando, partículas ○○○ subindo

## Lógica do Monitor
- new=processing → thinking
- tool start → thinking
- run_completed → speaking (3s) → idle
- 300s idle → sleeping

## Comandos
```bash
systemctl --user status pipface pipface-monitor
systemctl --user restart pipface pipface-monitor
```
