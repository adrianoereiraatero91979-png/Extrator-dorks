#!/bin/bash
# ══════════════════════════════════════════════════════════════════
#  GATEHUNTER v5.0 - INSTALADOR NETHUNTER SUPREME EDITION
# ══════════════════════════════════════════════════════════════════

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
MAGENTA='\033[1;35m'
CYAN='\033[1;36m'
WHITE='\033[1;37m'
RESET='\033[0m'

echo ""
echo -e "${MAGENTA}══════════════════════════════════════════════════════════════${RESET}"
echo -e "${CYAN}  GATEHUNTER v5.0 - INSTALADOR NETHUNTER SUPREME EDITION${RESET}"
echo -e "${MAGENTA}══════════════════════════════════════════════════════════════${RESET}"
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Recomendado rodar como root para instalar dependencias${RESET}"
    PIP_CMD="pip3 install --user"
else
    PIP_CMD="pip3 install"
fi

# Atualizar pip
echo -e "${CYAN}[*] Atualizando pip...${RESET}"
python3 -m pip install --upgrade pip 2>/dev/null

# Instalar dependências Python
echo -e "${CYAN}[*] Instalando dependencias Python...${RESET}"

PACKAGES=(
    "curl_cffi"
    "fake-useragent"
    "beautifulsoup4"
)

for pkg in "${PACKAGES[@]}"; do
    echo -e "${WHITE}  -> Instalando ${GREEN}${pkg}${RESET}..."
    $PIP_CMD "$pkg" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  [+] ${pkg} instalado com sucesso${RESET}"
    else
        echo -e "${YELLOW}  [!] ${pkg} - tentando metodo alternativo...${RESET}"
        pip3 install "$pkg" --break-system-packages 2>/dev/null
    fi
done

# Criar diretório de saída
echo -e "${CYAN}[*] Criando diretorios...${RESET}"
mkdir -p /sdcard/nh_files 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[!] Nao foi possivel criar /sdcard/nh_files${RESET}"
    echo -e "${YELLOW}[!] Os relatorios serao salvos em ~/gatehunter_output/${RESET}"
    mkdir -p ~/gatehunter_output
fi

# Copiar proxies se existir
if [ -f "proxies.txt" ]; then
    cp proxies.txt /sdcard/nh_files/proxies.txt 2>/dev/null
    echo -e "${GREEN}[+] Proxies copiadas para /sdcard/nh_files/${RESET}"
fi

# Tornar executável
chmod +x gatehunter.py 2>/dev/null

# Verificar instalação
echo ""
echo -e "${CYAN}[*] Verificando instalacao...${RESET}"
python3 -c "
try:
    from curl_cffi import requests
    print('  [+] curl_cffi: OK')
except:
    print('  [!] curl_cffi: FALHA')
try:
    from fake_useragent import UserAgent
    print('  [+] fake_useragent: OK')
except:
    print('  [!] fake_useragent: FALHA (nao critico)')
import sys
print(f'  [+] Python: {sys.version.split()[0]}')
"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}  INSTALACAO CONCLUIDA! GateHunter v5.0${RESET}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${WHITE}  Novidades v5.0:${RESET}"
echo -e "${CYAN}    [+] Multi-Engine: DDG HTML + Google.com.br + Bing + CSE API${RESET}"
echo -e "${CYAN}    [+] Busca SEM proxy (IP direto = menos bloqueios)${RESET}"
echo -e "${CYAN}    [+] Dorks simples e abrangentes (mais resultados)${RESET}"
echo -e "${CYAN}    [+] Blacklist 152+ dominios${RESET}"
echo -e "${CYAN}    [+] Store Score com 27 sinais de validacao${RESET}"
echo -e "${CYAN}    [+] Gateway Confirm em 7 zonas tecnicas${RESET}"
echo -e "${CYAN}    [+] Debug Log em /sdcard/nh_files/logs_gate_hunter.txt${RESET}"
echo ""
echo -e "${WHITE}  Google CSE API (opcional - 100 buscas/dia gratis):${RESET}"
echo -e "${CYAN}    export GOOGLE_CSE_API_KEY=\"sua_chave\"${RESET}"
echo -e "${CYAN}    export GOOGLE_CSE_CX=\"seu_cx\"${RESET}"
echo ""
echo -e "${WHITE}  Para executar:${RESET}"
echo -e "${CYAN}    python3 gatehunter.py${RESET}"
echo ""
