# PipFace Auto-Start & Message Integration

## Configuração Completa

### 1. Instalação do Serviço Systemd (Auto-Start no Boot)

```bash
# Copiar arquivo de serviço
sudo cp /home/nl3mos/clawd/pipface.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Ativar serviço para auto-start
sudo systemctl enable pipface.service

# Iniciar o serviço agora
sudo systemctl start pipface.service

# Verificar status
sudo systemctl status pipface.service
```

### 2. Integração com Mensagens do Clawdbot

Sempre que você enviar uma mensagem, chame:

```python
from pip_face_integration import process_message_with_emoji

# Antes de enviar a resposta
process_message_with_emoji(sua_mensagem)
```

### 3. Mapeamento de Emojis

| Emoji | Estado | Uso |
|-------|--------|-----|
| 😄😊🎉❤️✅ | happy | Sucesso, conclusão, felicidade |
| 🤔🎭💭 | thinking | Processando, pensando |
| ⚙️🔄🛠️ | working | Trabalho longo, tarefa em progresso |
| ❌😢⚠️ | error | Erro, falha, problema |
| 😴 | sleeping | Modo repouso |
| 🧘😐 | idle | Aguardando |
| 😕🤨 | confused | Confuso, interrogação |
| 😮 | surprised | Surpreso, espanto |
| 🎯💬📢 | speaking | Falando, respondendo |

### 4. Heurística Automática

Se nenhum emoji for encontrado, o sistema detecta automaticamente:

```
"erro", "falha" → error (vermelho)
"sucesso", "pronto", "ok" → happy (feliz)
"processando", "carregando" → working (trabalhando)
"verificar", "analisando" → thinking (pensando)
"?" → confused (confuso)
padrão → speaking (falando)
```

### 5. Uso Real

```python
# No pipeline de mensagens do Clawdbot
async def send_response(message: str):
    # Sincronizar face ANTES de enviar
    from pip_face_integration import process_message_with_emoji
    process_message_with_emoji(message)
    
    # Depois enviar a mensagem
    await messenger.send(message)
```

## Verificação

### Logs
```bash
# Log do PipFace
tail -f /tmp/pip_face.log

# Log do Monitor
tail -f /tmp/pip_face_monitor.log

# Log do Systemd
sudo journalctl -u pipface.service -f
```

### Teste Manual
```bash
python3 /home/nl3mos/clawd/pip_message_hook.py
```

## Troubleshooting

**PipFace não inicia no boot:**
```bash
sudo systemctl status pipface.service
sudo journalctl -u pipface.service -n 50
```

**Emojis não sincronizam:**
- Verificar se `pip_message_hook.py` está importando corretamente
- Testar manualmente: `python3 pip_message_hook.py`

**Display não aparece:**
- Verificar `DISPLAY` está correto
- Verificar permissões X11: `xhost +local:`

## Status da Integração

✅ Auto-start via systemd
✅ Message hook com emoji detection
✅ Heurística inteligente de contexto
✅ Integração com PipFace v04
✅ Pronto para produção

---

**Próximos passos:** Integrar `process_message_with_emoji()` no pipeline real de respostas do Clawdbot.
