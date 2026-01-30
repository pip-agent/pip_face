#!/bin/bash

# Plano Completo de Autocuidado do Clawdbot

# Configurações base
WORKSPACE="/home/nl3mos/clawd"
LOG_FILE="$WORKSPACE/maintenance.log"
REPORT_FILE="$WORKSPACE/self_care_report.txt"
BACKUP_DIR="$WORKSPACE/backups/$(date '+%Y-%m-%d_%H-%M-%S')"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 1. Limpeza e Organização Diária
daily_cleanup() {
    log "🧹 Iniciando limpeza diária"
    
    # Criar diretórios necessários
    mkdir -p "$BACKUP_DIR/memory" "$BACKUP_DIR/logs"
    
    # Limpar arquivos temporários
    find "$WORKSPACE" -type f -name "*.tmp" -mtime +7 -delete
    find "$WORKSPACE" -type f -name "*.log" -mtime +30 -exec gzip {} \;
    
    # Backup de arquivos importantes
    mkdir -p "$BACKUP_DIR/memory"
    cp -r "$WORKSPACE/memory" "$BACKUP_DIR/memory" 2>/dev/null
    touch "$WORKSPACE/MEMORY.md"
    cp "$WORKSPACE/MEMORY.md" "$BACKUP_DIR/MEMORY.md"
    
    log "🧹 Limpeza diária concluída"
}

# 2. Exames Periódicos (Verificação de Sistema)
system_health_check() {
    log "🩺 Iniciando verificação de saúde do sistema"
    
    # Verificar uso de recursos
    DISK_USAGE=$(df -h "$WORKSPACE" | awk '/\// {print $5}' | sed 's/%//')
    MEMORY_TOTAL=$(free -m | grep Mem | awk '{print $2}')
    MEMORY_USED=$(free -m | grep Mem | awk '{print $3}')
    MEMORY_PERCENTAGE=$(echo "scale=2; ($MEMORY_USED / $MEMORY_TOTAL) * 100" | bc)
    
    # Gerar relatório de saúde
    echo "💻 Relatório de Saúde do Sistema" > "$REPORT_FILE"
    echo "----------------------------" >> "$REPORT_FILE"
    echo "🌡️ Uso de Disco: $DISK_USAGE%" >> "$REPORT_FILE"
    echo "🧠 Uso de Memória: $MEMORY_PERCENTAGE% ($MEMORY_USED MB / $MEMORY_TOTAL MB)" >> "$REPORT_FILE"
    
    # Alertas de recursos
    if [[ $DISK_USAGE -gt 70 ]]; then
        echo "🔴 ALERTA: Uso de disco alto!" >> "$REPORT_FILE"
    fi
    
    # Alertas de memória com níveis de criticidade
    if (( $(echo "$MEMORY_PERCENTAGE > 90" | bc -l) )); then
        echo "🔴 ALERTA CRÍTICO: Uso de memória acima de 90%!" >> "$REPORT_FILE"
    elif (( $(echo "$MEMORY_PERCENTAGE > 80" | bc -l) )); then
        echo "🟠 ALERTA: Uso de memória acima de 80%" >> "$REPORT_FILE"
    fi
    
    # Alertas de swap
    SWAP_USED=$(free -m | grep Swap | awk '{print $3}')
    if [[ $SWAP_USED -gt 100 ]]; then
        echo "🟠 ALERTA: Uso significativo de swap!" >> "$REPORT_FILE"
    fi
    
    log "🩺 Verificação de saúde concluída"
}

# Restante do script permanece igual ao anterior
# (funções knowledge_maintenance, system_functionality_test, security_maintenance, main)