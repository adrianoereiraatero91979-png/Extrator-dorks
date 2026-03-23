# GateHunter v3.0 - NetHunter Supreme Edition

```
   ██████╗  █████╗ ████████╗███████╗
  ██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝
  ██║  ███╗███████║   ██║   █████╗  
  ██║   ██║██╔══██║   ██║   ██╔══╝  
  ╚██████╔╝██║  ██║   ██║   ███████╗
   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
  ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
  ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
  ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
  ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
  ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

**Ferramenta profissional de OSINT** para identificação e catalogação de **lojas e e-commerces reais** que utilizam gateways de pagamento específicas. Otimizada para **Kali Linux NetHunter**.

---

## Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| **Multi-Engine Search** | DuckDuckGo + Google + Bing com dorks inteligentes |
| **curl_cffi Impersonate** | TLS Fingerprint idêntico a Chrome/Safari/Edge real |
| **Proxy Rotativa** | Pool de proxies com rotação automática e failover |
| **Filtro Anti-Lixo** | Blacklist de 66+ domínios + padrões informativos |
| **Store Validator** | Score de validação para identificar lojas REAIS |
| **15+ Gateways** | Asaas, PagarMe, eRede, Stripe, Cielo, MercadoPago... |
| **Classificação IA** | 18 categorias de nicho (roupas, eletrônicos, etc) |
| **Detecção de Plataforma** | WooCommerce, Shopify, VTEX, Nuvemshop, Tray... |
| **Debug Logging** | Log completo de tudo em `/sdcard/nh_files/` |
| **Relatórios Ultra Detalhados** | TXT + JSON + URLs + Stores Only |

---

## Gateways Suportadas

| # | Gateway | Descrição |
|---|---------|-----------|
| 1 | Asaas | Plataforma de cobranças e pagamentos |
| 2 | PagarMe | Pagar.me (Stone) - Gateway de pagamentos |
| 3 | eRede | eRede (Itaú) - Adquirente e gateway |
| 4 | PayFlow | PayFlow - Gateway de pagamentos digital |
| 5 | AppMax | AppMax - Plataforma de vendas e pagamentos |
| 6 | MercadoPago | Mercado Pago - Gateway e carteira digital |
| 7 | PagSeguro | PagSeguro/PagBank - Gateway de pagamentos |
| 8 | Cielo | Cielo - Maior adquirente do Brasil |
| 9 | Stripe | Stripe - Gateway global de pagamentos |
| 10 | Hotmart | Hotmart - Plataforma de produtos digitais |
| 11 | Eduzz | Eduzz - Plataforma de infoprodutos |
| 12 | Kiwify | Kiwify - Plataforma de vendas digitais |
| 13 | Vindi | Vindi - Plataforma de pagamentos recorrentes |
| 14 | Iugu | Iugu - Gateway e plataforma financeira |
| 15 | Getnet | Getnet (Santander) - Adquirente e gateway |
| 0 | CUSTOM | Inserir gateway personalizada |

---

## Instalação no Kali NetHunter

### Método 1: Git Clone (Recomendado)

```bash
cd /root
git clone https://github.com/adrianoereiraatero91979-png/Extrator-dorks.git gatehunter
cd gatehunter
chmod +x install.sh gatehunter.py
./install.sh
python3 gatehunter.py
```

### Método 2: Atualização

```bash
cd /root/gatehunter
git pull
python3 gatehunter.py
```

---

## Dependências

O script `install.sh` instala tudo automaticamente:

```
pip3 install curl_cffi rich fake-useragent beautifulsoup4
```

| Pacote | Função |
|--------|--------|
| `curl_cffi` | TLS Fingerprint Impersonate (Chrome/Safari/Edge) |
| `rich` | Interface colorida no terminal |
| `fake-useragent` | Geração de User-Agents realistas |
| `beautifulsoup4` | Parser HTML auxiliar |

---

## Proxies

Edite o arquivo `proxies.txt` com suas proxies no formato:

```
IP:PORTA:USUARIO:SENHA
```

Exemplo:
```
45.95.96.10:8831:user123:pass456
```

---

## Arquivos de Saída

Todos os relatórios são salvos em `/sdcard/nh_files/`:

| Arquivo | Conteúdo |
|---------|----------|
| `gatehunter_GATEWAY_TIMESTAMP.txt` | Relatório completo ultra detalhado |
| `gatehunter_GATEWAY_TIMESTAMP.json` | Dados estruturados em JSON |
| `gatehunter_GATEWAY_urls_TIMESTAMP.txt` | Lista de todas as URLs |
| `gatehunter_GATEWAY_confirmed_TIMESTAMP.txt` | Apenas URLs confirmadas |
| `gatehunter_GATEWAY_stores_TIMESTAMP.txt` | Apenas LOJAS REAIS |
| `gatehunter_debug.log` | Log de debug completo |

---

## Como Funciona

### Fase 1: Coleta via Dorks
O script usa dorks inteligentes em 3 engines (DDG, Google, Bing) para encontrar sites que usam a gateway selecionada. As dorks são focadas em encontrar **lojas reais** e não documentação/blogs.

### Fase 2: Análise Profunda
Cada URL é analisada com multi-threading (15 threads). O script:
1. Filtra domínios da própria gateway (anti-lixo)
2. Verifica presença da gateway no HTML (scripts, iframes, links)
3. Calcula **Store Score** para validar se é loja real
4. Classifica o nicho da loja (18 categorias)
5. Detecta plataforma e-commerce
6. Extrai contatos (emails, telefones)

### Fase 3: Relatórios
Gera 5 arquivos de relatório com diferentes níveis de detalhe.

---

## Store Validator

O sistema de validação usa um score baseado em sinais encontrados no HTML:

| Tipo | Peso | Exemplos |
|------|------|----------|
| HIGH | +3 | "adicionar ao carrinho", "comprar agora", "checkout" |
| MEDIUM | +2 | "R$", "preço", "frete", "estoque" |
| PLATFORM | +4 | "woocommerce", "shopify", "vtex" |
| PAYMENT | +2 | "cartão de crédito", "boleto", "pix" |
| NEGATIVE | -2 | "documentação", "tutorial", "blog post" |

**Threshold padrão: 8 pontos** para ser classificado como loja real.

---

## Aviso Legal

Esta ferramenta é destinada **exclusivamente para fins educacionais e de pesquisa autorizada**. O uso desta ferramenta para atividades ilegais ou não autorizadas é estritamente proibido. O autor não se responsabiliza pelo uso indevido.

---

**GateHunter v3.0** - NetHunter Supreme Edition
