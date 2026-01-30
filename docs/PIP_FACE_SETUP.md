# PIP FACE - Guia de Configuração e Uso

## Arquivos

- `pip_face_v04.py` — Script principal da animação
- `pip_face_integration.py` — Wrapper Python para integração fácil

## Pré-requisitos

```bash
pip install PyQt6
```

## Inicialização

### Opção 1: Manual (desenvolvimento)

Terminal 1:
```bash
cd /home/nl3mos/clawd
python3 pip_face_v04.py
```

Terminal 2:
```bash
# Seu Clawdbot aqui
```

### Opção 2: Automático (produção)

No código do Clawdbot, adicionar:

```python
import subprocess

pip_process = subprocess.Popen(
    ["python3", "/home/nl3mos/clawd/pip_face_v04.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# No shutdown:
atexit.register(lambda: pip_process.terminate())
```

## Uso no Clawdbot

### Importar

```python
from pip_face_integration import get_face

face = get_face()
```

### Exemplo de Fluxo

```python
async def process_user_message(message):
    face.thinking()  # Mostra que tá processando
    
    response = await call_api(message)
    
    if response:
        face.speaking()  # Começa a responder
        await send_response(response)
        face.happy()     # Sucesso!
    else:
        face.error()     # Algo deu errado
    
    await asyncio.sleep(2)
    face.idle()  # Volta ao normal
```

## Estados Disponíveis

| Estado | Método | Uso |
|--------|--------|-----|
| idle | `face.idle()` | Aguardando input |
| sleeping | `face.sleeping()` | Standby/inativo |
| thinking | `face.thinking()` | Processando |
| speaking | `face.speaking(amplitude=0.5)` | Respondendo |
| working | `face.working()` | Tarefa longa |
| surprised | `face.surprised()` | Evento inesperado |
| confused | `face.confused()` | Não entendeu |
| happy | `face.happy()` | Sucesso |
| error | `face.error()` | Erro |

## Partículas

```python
face.particle("heart")      # ❤️
face.particle("star")       # ⭐
face.particle("question")   # ❓
face.particle("exclaim")    # ❗
face.particle("zzz")        # 😴
face.particle("dots")       # ...
face.particle("sweat")      # 💦
face.particle("gear")       # ⚙️
```

## Teste Rápido

```bash
python3 pip_face_integration.py
```

## Troubleshooting

### Face não aparece
- Verificar se `pip_face_v04.py` está rodando
- Checar porta 5555 está livre: `lsof -i :5555`

### Lag/travamento
- Normal em VM, esperado em bare metal rodar suave
- Reduzir FPS em CONFIG se necessário

### Emojis não aparecem
No Linux:
```bash
sudo apt-get install fonts-noto-color-emoji
```

## Próximas Modificações

O script é todo seu! Quando quiser customizar:
- Cores
- Tamanho dos olhos
- Velocidade das animações
- Novos estados/partículas

Basta editar `pip_face_v04.py` e reiniciar.

---

**Status**: ✅ Pronto para produção
**Versão**: v04 (estável)
