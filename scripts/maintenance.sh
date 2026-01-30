#!/bin/bash

# Ambiente de manutenção Clawdot - Protocolo de Segurança

LOG_FILE="/home/nl3mos/clawd/maintenance.log"
REPORT_FILE="/home/nl3mos/clawd/maintenance_report.txt"
BACKUP_DIR="/home/nl3mos/clawd/backups"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Função de Análise de Segurança
analyze_security_alerts() {
    log "🚨 Iniciando análise de alertas"
    
    # Limpar arquivo de relatório
    > "$REPORT_FILE"
    
    echo "🕵️ Relatório de Segurança - $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
    echo "-------------------------------------------" >> "$REPORT_FILE"
    
    # Verificar conexões e modelos
    WHATSAPP_ERRORS=$(find /home/nl3mos/clawd -type f -name "*whatsapp*" | wc -l)
    if [[ $WHATSAPP_ERRORS -gt 0 ]]; then
        echo "🔇 WhatsApp: Configurações encontradas. Removendo..." >> "$REPORT_FILE"
        find /home/nl3mos/clawd -type f -name "*whatsapp*" -delete
    fi
    
    # Verificar erros de conexão
    NETWORK_ERRORS=$(netstat -tuln | grep -c ESTABLISHED)
    echo "🌐 Conexões de rede ativas: $NETWORK_ERRORS" >> "$REPORT_FILE"
    
    # Verificar espaço em disco
    DISK_USAGE=$(df -h / | awk '/\// {print $5}' | sed 's/%//')
    echo "💾 Uso de disco: $DISK_USAGE%" >> "$REPORT_FILE"
    
    if [[ $DISK_USAGE -gt 70 ]]; then
        echo "⚠️ Atenção: Uso de disco alto" >> "$REPORT_FILE"
    fi
    
    log "🚨 Análise de alertas concluída"
}

# Função de limpeza
cleanup_system() {
    log "🧹 Iniciando limpeza"
    
    # Criar diretório de backup
    mkdir -p "$BACKUP_DIR/memory"
    
    # Limpar arquivos temporários
    find /home/nl3mos/clawd -type f -name "*.tmp" -mtime +7 -delete
    
    # Backup de arquivos importantes
    cp -r /home/nl3mos/clawd/memory/* "$BACKUP_DIR/memory/" 2>/dev/null
    
    log "🧹 Limpeza concluída"
}

# Função principal
main() {
    log "🤖 Iniciando manutenção"
    
    analyze_security_alerts
    cleanup_system
    
    # Mostrar relatório
    cat "$REPORT_FILE"
    
    log "🤖 Manutenção concluída"
}

# Executar
main