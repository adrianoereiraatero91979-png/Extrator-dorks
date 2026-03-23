# GateHunter v4.0 - NetHunter Supreme Edition

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
| **Multi-Engine Search** | DuckDuckGo + Google + Bing com dorks focadas em assinaturas JS |
| **curl_cffi Impersonate** | TLS Fingerprint idêntico a Chrome/Safari/Edge real |
| **Proxy Rotativa** | Pool de proxies com rotação automática e failover |
| **Validação 3 Camadas** | URL Filter + Gateway Confirm + Store Validator |
| **Blacklist Massiva** | 200+ domínios bloqueados (blogs, docs, suporte, etc) |
| **15+ Gateways** | Asaas, PagarMe, eRede, Stripe, Cielo, MercadoPago... |
| **Store Score** | Score inteligente com sinais positivos e negativos |
| **Classificação** | 18 categorias de nicho (roupas, eletrônicos, etc) |
| **Detecção Plataforma** | WooCommerce, Shopify, VTEX, Nuvemshop, Tray... |
| **Debug Logging** | Log completo em `/sdcard/nh_files/logs_gate_hunter.txt` |
| **Relatórios** | TXT + JSON + LOJAS + All URLs |

---

## Validação em 3 Camadas (v4.0)

### Camada 1: URL Filter
- Blacklist de 200+ domínios (YouTube, GitHub, Medium, blogs de gateways, etc)
- Filtro de subdomínios informativos (docs., blog., help., support., api., etc)
- Bloqueio de padrões de URL ruins (/blog/, /docs/, /faq/, /tutorial/, etc)
- Domínios da própria gateway são bloqueados automaticamente

### Camada 2: Gateway Confirmation
- Busca assinaturas JS em zonas técnicas: `<script src>`, `<iframe src>`, `<form action>`, `<link href>`, `data-*`
- NÃO confirma por texto livre (evita falsos positivos de artigos que mencionam a gateway)
- Fallback: text_signatures com threshold de 3+ ocorrências

### Camada 3: Store Validator
Score baseado em sinais encontrados no HTML:

| Sinal | Peso | Exemplos |
|-------|------|----------|
| Preços (R$) | +5 | `R$ 89,90`, `data-price`, `class="price"` |
| Botão compra | +5 | "adicionar ao carrinho", "comprar agora" |
| Carrinho | +4 | "carrinho", "sacola", "cart" |
| Plataforma | +4 | WooCommerce, Shopify, VTEX detectados |
| Produtos | +3 | "produto", "catálogo", "categoria" |
| Frete | +3 | "frete", "CEP", "Correios", "Sedex" |
| Pagamento | +3 | "cartão de crédito", "boleto", "pix" |
| Variações | +2 | "tamanho", "cor", "quantidade" |
| Avaliações | +2 | "avaliação", "estrelas", "review" |
| Documentação | -15 | "API reference", "npm install", "SDK" |
| Blog/Artigo | -10 | "publicado em", "leia mais", "tags:" |
| Tutorial | -8 | "como configurar", "passo a passo" |
| Suporte | -8 | "base de conhecimento", "FAQ" |
| Comparativo | -8 | "melhor gateway", "prós e contras" |
| Fórum | -10 | "responder tópico", "membro desde" |

**Threshold: >= 8 pontos** para ser classificado como loja real.

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

### Primeira vez

```bash
cd /root
git clone https://github.com/adrianoereiraatero91979-png/Extrator-dorks.git gatehunter
cd gatehunter
chmod +x install.sh gatehunter.py
./install.sh
python3 gatehunter.py
```

### Atualização

```bash
cd /root/gatehunter
git pull
python3 gatehunter.py
```

---

## Dependências

O script `install.sh` instala tudo automaticamente:

| Pacote | Função |
|--------|--------|
| `curl_cffi` | TLS Fingerprint Impersonate (Chrome/Safari/Edge) |
| `fake-useragent` | Geração de User-Agents realistas |
| `beautifulsoup4` | Parser HTML auxiliar (opcional) |

---

## Proxies

Edite o arquivo `proxies.txt` com suas proxies no formato:

```
IP:PORTA:USUARIO:SENHA
```

---

## Arquivos de Saída

Todos os relatórios são salvos em `/sdcard/nh_files/`:

| Arquivo | Conteúdo |
|---------|----------|
| `gatehunter_GATEWAY_TIMESTAMP.txt` | Relatório completo ultra detalhado |
| `gatehunter_GATEWAY_TIMESTAMP.json` | Dados estruturados em JSON |
| `gatehunter_GATEWAY_TIMESTAMP_LOJAS.txt` | Apenas LOJAS REAIS confirmadas |
| `gatehunter_GATEWAY_TIMESTAMP_all_urls.txt` | Todas as URLs analisadas |
| `logs_gate_hunter.txt` | Debug log completo |

---

## Changelog

### v4.0 (2026-03-23)
- Dorks profissionais focadas em assinaturas JS técnicas
- Validação em 3 camadas (URL Filter + Gateway Confirm + Store Validator)
- Blacklist massiva de 200+ domínios
- Detecção de gateway via zonas técnicas (script src, iframe, form)
- Store Score com sinais positivos e negativos
- Debug logging completo em `/sdcard/nh_files/logs_gate_hunter.txt`
- Dedup por domínio

### v3.0
- Filtro anti-lixo com blacklist
- Store Validator básico

### v2.0
- Versão inicial com curl_cffi e multi-engine

---

## Aviso Legal

Esta ferramenta é destinada **exclusivamente para fins educacionais e de pesquisa autorizada**. O uso desta ferramenta para atividades ilegais ou não autorizadas é estritamente proibido.

---

**GateHunter v4.0** - NetHunter Supreme Edition
