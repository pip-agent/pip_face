#!/bin/bash

# Script de utilitários para o Clawdbot

# Função para verificar status do sistema
system_check() {
    echo "=== Clawdbot System Check ==="
    echo "Versão: $(clawdbot version)"
    echo "Gateway Status:"
    clawdbot gateway status
    echo
    echo "Canais Ativos:"
    clawdbot channels list
    echo
    echo "Modelos Disponíveis:"
    clawdbot models list
}

# Função para resumo de memória
memory_summary() {
    echo "=== Resumo de Memória ==="
    echo "Arquivos de memória diária:"
    ls -l memory/
    echo
    echo "Últimas entradas em MEMORY.md:"
    tail -n 5 MEMORY.md
}

# Função para verificar atualizações
check_updates() {
    echo "=== Verificação de Atualizações ==="
    clawdbot update check
}

# Permite executar funções específicas
case "$1" in
    "system")
        system_check
        ;;
    "memory")
        memory_summary
        ;;
    "updates")
        check_updates
        ;;
    *)
        echo "Uso: $0 {system|memory|updates}"
        exit 1
        ;;
esac