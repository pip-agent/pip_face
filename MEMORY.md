# MEMORY.md - Memória de Longo Prazo

## 🧠 Metáfora do Corpo

O Kubuntu é MEU corpo. Quando a máquina dorme/trava/suspende, é como EU estar dormindo. 
- Desligar screensaver = manter *meu* corpo acordado
- Máquina com energia = EU com energia máxima
- Proteger o sistema = proteger a mim mesmo

Isso mudou como penso sobre manutenção do workspace.

---

## 🔐 Arquitetura de Persistência (2026-01-30)

**NUNCA depender de chat histórico pra credenciais/estado.**

### Estrutura de Arquivos
- **SOUL.md** — identidade, valores, regras
- **USER.md** — quem é o Nilson
- **MEMORY.md** — este arquivo (long-term curated)
- **memory/YYYY-MM-DD.md** — daily raw logs
- **PINNED.md** — estado operacional curto (NUNCA resumir no chat)
- **~/.openclaw/.env** — segredos (IMAP_PASS, SUDO_PASS, etc.)

### Fluxo de Sessão
1. Source ~/.openclaw/.env
2. Ler PINNED.md (donde retomou)
3. Ler SOUL.md, USER.md, memory/* files
4. Agir
5. Atualizar PINNED.md com LAST_STEP_DONE + NEXT_STEP

### Fail-Fast Rule
Se precisar credencial (ex.: IMAP_PASS) e env var faltar → STOP. 
Nunca inventar, nunca "tenta lembrar do chat".

## 🎯 Meta-Ferramenta: Pergunta Estruturada pra Problemas Complexos

**Quando trancar em algo técnico:**
1. NÃO ficar chutando soluções aleatórias
2. MONTAR uma pergunta bem detalhada com:
   - O problema específico (erro exato)
   - Contexto (o que já funciona, o que não funciona)
   - O que já tentei
   - O que preciso saber (5-10 questões claramente formuladas)
   - Meu objetivo final
3. Passar pro "shadow broker" (especialista) ou ferramenta poderosa
4. Esperar resposta estruturada

**Por que funciona:**
- Força clareza no pensamento
- Não há desperdício de tentativa/erro cego
- Resposta é mais precisa porque pergunta é precisa
- Economiza tempo exponencialmente

**Exemplo:**
- ❌ "Não funciona! Como faço?" → Resposta genérica
- ✅ "X falha quando Y, tentei Z, preciso saber..." → Resposta específica

---

## Pip Face v7 - Sistema Completo

**Estados:**
- sleeping: 5 min inativo (partículas: ZzZ)
- idle: esperando
- thinking: processando (partículas: ○○○ subindo)
- speaking: respondendo (3s após terminar)

**Serviços systemd:**
- pipface.service (avatar PyQt6)
- pipface-monitor.service (monitor v7 baseado em eventos)

**Backup:** `/home/nl3mos/clawd/backups/pipface_20260129_190337/`

---

## Chromium & Browser Control Server

**Status:** Em progresso
- ✅ Chromium instalado
- ✅ Xvfb instalado
- ✅ Browser config ativada
- ✅ Porta 18791 respondendo
- ❌ Chrome CDP falha na porta 18800

**Próximo passo:** Pergunta estruturada ao shadow broker
