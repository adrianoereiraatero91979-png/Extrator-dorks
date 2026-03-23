# GateHunter v5.0 - NetHunter Supreme Edition

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

**Ferramenta profissional de OSINT** para identificacao e catalogacao de **lojas e e-commerces reais** que utilizam gateways de pagamento especificas. Otimizada para **Kali Linux NetHunter**.

---

## Funcionalidades

| Recurso | Descricao |
|---------|-----------|
| **Multi-Engine Search** | DDG HTML + Google.com.br + Bing + Google CSE API (opcional) |
| **Busca Inteligente** | IP direto para buscas (sem proxy = menos bloqueios) |
| **curl_cffi Impersonate** | TLS Fingerprint identico a Chrome/Safari/Edge real |
| **Proxy Rotativa** | Pool de proxies com rotacao automatica (apenas para analise) |
| **Validacao 3 Camadas** | URL Filter + Gateway Confirm + Store Validator |
| **Blacklist Massiva** | 152+ dominios bloqueados (blogs, docs, suporte, etc) |
| **15+ Gateways** | Asaas, PagarMe, eRede, Stripe, Cielo, MercadoPago... |
| **Store Score** | 27 sinais (16 positivos + 11 negativos) para validar loja real |
| **Gateway Confirm** | 7 zonas de deteccao (JS_SRC, IFRAME, FORM, LINK, INLINE_JS, META, TEXT) |
| **Classificacao** | 15 categorias de nicho (roupas, eletronicos, pet, etc) |
| **Deteccao Plataforma** | WooCommerce, Shopify, VTEX, Nuvemshop, Tray, Yampi... |
| **Debug Logging** | Log completo em `/sdcard/nh_files/logs_gate_hunter.txt` |
| **Relatorios** | TXT detalhado + JSON + LOJAS + All URLs |

---

## Como Funciona

O GateHunter opera em 3 fases:

**Fase 1 - Coleta via Dorks**: Busca em DDG HTML, Google.com.br e Bing usando dorks otimizadas que focam em contexto de e-commerce ("comprar", "carrinho", "checkout") combinado com o nome da gateway. Filtra automaticamente sites da blacklist de 152+ dominios. A busca e feita SEM proxy (IP direto do celular e mais confiavel para search engines).

**Fase 2 - Analise de Sites**: Acessa cada URL com threads paralelas usando proxy pool, confirma a presenca da gateway no codigo-fonte em 7 zonas tecnicas (scripts JS, iframes, forms, links, inline JS, meta tags, texto) e calcula um score de loja baseado em 27 sinais.

**Fase 3 - Relatorios**: Gera relatorios detalhados separando lojas confirmadas (gateway + loja), sites com gateway sem loja, e lojas sem gateway confirmada.

---

## Validacao em 3 Camadas

### Camada 1: URL Filter
Blacklist de 152+ dominios bloqueados automaticamente: YouTube, GitHub, Medium, blogs das gateways, ReclameAqui, Wikipedia, plataformas de e-commerce (Shopify, Nuvemshop, Tray), comparadores (B2BStack, Capterra), e mais. Tambem filtra subdominios informativos (docs., blog., help., api.) e paths ruins (/blog, /docs, /tutorial).

### Camada 2: Gateway Confirmation
Busca assinaturas da gateway em 7 zonas tecnicas do HTML:

| Zona | Descricao | Exemplo |
|------|-----------|---------|
| JS_SRC | Script tags com src | `<script src="js.pagar.me/v5/sdk.js">` |
| IFRAME | Iframes embutidos | `<iframe src="checkout.asaas.com">` |
| FORM | Form actions | `<form action="api.cielo.com.br">` |
| LINK | Links de checkout | `<a href="checkout.stripe.com">` |
| INLINE_JS | Variaveis em scripts | `var gateway = "pagarme"` |
| META | Meta tags e data-attrs | `data-gateway="mercadopago"` |
| TEXT | Texto (3+ ocorrencias) | Mencoes multiplas no conteudo |

### Camada 3: Store Validator
Score baseado em sinais encontrados no HTML. Threshold: >= 6 pontos.

| Sinal | Peso | Exemplos |
|-------|------|----------|
| Precos (R$) | +5 | `R$ 89,90`, `class="price"` |
| Botao compra | +5 | "adicionar ao carrinho", "comprar agora" |
| Checkout | +4 | "finalizar compra", "fechar pedido" |
| Frete | +4 | "calcular frete", "CEP", "Correios" |
| Plataforma e-commerce | +5 | WooCommerce, Shopify, VTEX detectados |
| Carrinho | +3 | "carrinho", "sacola", "cart" |
| Parcelas | +3 | "12x sem juros", "parcelamento" |
| Documentacao | -10 | "API reference", "endpoint" |
| Tutorial | -8 | "passo a passo", "como usar" |
| Blog | -6 | "artigo", "publicado em" |
| Integracao | -8 | "SDK", "webhook", "API key" |

---

## Gateways Suportadas

| # | Gateway | Descricao |
|---|---------|-----------|
| 1 | Asaas | Plataforma de cobrancas e pagamentos |
| 2 | PagarMe | Pagar.me (Stone) - Gateway de pagamentos |
| 3 | Erede | eRede (Itau) - Adquirente e gateway |
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

## Instalacao no Kali NetHunter

### Primeira vez

```bash
cd /root
git clone https://github.com/adrianoereiraatero91979-png/Extrator-dorks.git gatehunter
cd gatehunter
chmod +x install.sh gatehunter.py
./install.sh
python3 gatehunter.py
```

### Atualizacao

```bash
cd /root/gatehunter
git pull
python3 gatehunter.py
```

Se der conflito:

```bash
cd /root/gatehunter
git reset --hard origin/main
git pull
python3 gatehunter.py
```

---

## Google CSE API (Opcional)

Para resultados ainda melhores, configure a Google Custom Search Engine API (100 buscas/dia gratis):

1. Acesse https://programmablesearchengine.google.com/ e crie um Custom Search Engine
2. Acesse https://console.cloud.google.com/apis/credentials e crie uma API Key
3. Exporte as variaveis antes de rodar:

```bash
export GOOGLE_CSE_API_KEY="sua_chave_aqui"
export GOOGLE_CSE_CX="seu_cx_aqui"
python3 gatehunter.py
```

---

## Proxies

Edite o arquivo `proxies.txt` com suas proxies no formato:

```
IP:PORTA:USUARIO:SENHA
```

As proxies sao usadas **apenas para analise de sites**, nao para buscas. O IP direto do celular e mais confiavel para search engines.

---

## Arquivos de Saida

Todos os relatorios sao salvos em `/sdcard/nh_files/`:

| Arquivo | Conteudo |
|---------|----------|
| `gatehunter_GATEWAY_TIMESTAMP.txt` | Relatorio completo ultra detalhado |
| `gatehunter_GATEWAY_TIMESTAMP.json` | Dados estruturados em JSON |
| `gatehunter_GATEWAY_TIMESTAMP_LOJAS.txt` | Apenas LOJAS REAIS confirmadas |
| `gatehunter_GATEWAY_TIMESTAMP_all_urls.txt` | Todas as URLs analisadas |
| `logs_gate_hunter.txt` | Debug log completo da sessao |

---

## Aviso Legal

Esta ferramenta e destinada **exclusivamente para fins educacionais e de pesquisa autorizada**. O uso desta ferramenta para atividades ilegais ou nao autorizadas e estritamente proibido.

---

**GateHunter v5.0** - NetHunter Supreme Edition
