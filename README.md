# GateHunter v6.0.0 - NetHunter Supreme Edition

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
| **Brave Search** | Engine principal com alta taxa de sucesso |
| **Multi-Engine** | Brave + DDG + Bing + Google CSE API (opcional) |
| **15 Gateways** | Asaas, PagarMe, eRede, Stripe, Cielo, MercadoPago, etc |
| **15 Nichos** | Roupas, Gift Card, Eletronicos, Pet Shop, Joias, etc |
| **Filtro por Nicho** | Buscar lojas de um tipo especifico (ex: "roupas + PagarMe") |
| **curl_cffi** | TLS Fingerprint identico a Chrome/Safari/Edge real |
| **Proxy Pool** | Rotacao automatica para analise de sites |
| **Validacao 3 Camadas** | URL Filter + Store Score + Gateway Confirm |
| **Blacklist 96+** | Dominios de blogs, docs, suporte, redes sociais bloqueados |
| **Store Score** | 27 sinais (16 positivos + 11 negativos) |
| **Gateway Confirm** | 5 zonas de deteccao (JS_SRC, IFRAME, FORM, LINK, TEXT) |
| **Classificacao** | Detecta nicho e plataforma (WooCommerce, Shopify, VTEX...) |
| **Debug Log** | Log completo em `/sdcard/nh_files/logs_gate_hunter.txt` |
| **Relatorios** | TXT + JSON + LOJAS + All URLs |

---

## Novidade v6.0: Filtro por Nicho

Agora voce pode buscar lojas de um tipo especifico! Exemplos:

- Quero lojas de **roupas** com gateway **Asaas**
- Quero sites de **gift card** com gateway **eRede**
- Quero **pet shops** com gateway **PagarMe**

O script combina automaticamente os termos do nicho com as dorks da gateway para resultados muito mais precisos.

### Nichos Disponiveis

| # | Nicho | Termos de Busca |
|---|-------|-----------------|
| 0 | Todos | Sem filtro |
| 1 | Roupas / Moda | roupa, camiseta, vestido, moda, fashion |
| 2 | Calcados / Tenis | tenis, sapato, sneaker, calcado |
| 3 | Eletronicos | celular, notebook, smartphone, pc gamer |
| 4 | Gift Card | gift card, vale presente, cartao presente |
| 5 | Joalheria | joia, anel, colar, relogio, ouro |
| 6 | Cosmeticos | maquiagem, perfume, skincare, beleza |
| 7 | Suplementos | whey, creatina, suplemento, vitamina |
| 8 | Pet Shop | pet, racao, cachorro, gato |
| 9 | Casa / Decoracao | decoracao, movel, sofa, luminaria |
| 10 | Alimentos | cafe, vinho, chocolate, gourmet |
| 11 | Esportes | esporte, academia, corrida, bicicleta |
| 12 | Infantil | brinquedo, infantil, bebe, kids |
| 13 | Cursos / Digital | curso online, ebook, aula, treinamento |
| 14 | Assinatura | assinatura, clube, mensal, recorrente |

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
git reset --hard origin/main
git pull
python3 gatehunter.py
```

---

## Como Usar

1. Execute `python3 gatehunter.py`
2. Selecione a gateway (1-15) ou custom (0)
3. Selecione o nicho (0 = Todos, 1-14 = especifico)
4. Aguarde o scan
5. Resultados em `/sdcard/nh_files/`

### Exemplo: Lojas de roupas com PagarMe

```
GateHunter > 2        (PagarMe)
Nicho > 1             (Roupas / Moda)
```

### Exemplo: Gift Cards com eRede

```
GateHunter > 3        (Erede)
Nicho > 4             (Gift Card)
```

---

## Gateways Suportadas

| # | Gateway | Descricao |
|---|---------|-----------|
| 1 | Asaas | Plataforma de cobrancas e pagamentos |
| 2 | PagarMe | Pagar.me (Stone) - Gateway de pagamentos |
| 3 | Erede | eRede (Itau) - Adquirente e gateway |
| 4 | PayFlow | PayFlow - Gateway digital |
| 5 | AppMax | AppMax - Vendas e pagamentos |
| 6 | MercadoPago | Mercado Pago - Gateway e carteira |
| 7 | PagSeguro | PagSeguro/PagBank |
| 8 | Cielo | Cielo - Maior adquirente BR |
| 9 | Stripe | Stripe - Gateway global |
| 10 | Hotmart | Hotmart - Produtos digitais |
| 11 | Eduzz | Eduzz - Infoprodutos |
| 12 | Kiwify | Kiwify - Vendas digitais |
| 13 | Vindi | Vindi - Pagamentos recorrentes |
| 14 | Iugu | Iugu - Plataforma financeira |
| 15 | Getnet | Getnet (Santander) |
| 0 | CUSTOM | Gateway personalizada |

---

## Google CSE API (Opcional)

Para resultados premium (100 buscas/dia gratis):

1. Crie um search engine em https://programmablesearchengine.google.com/
2. Crie uma API key em https://console.cloud.google.com/apis/credentials
3. Exporte:

```bash
export GOOGLE_CSE_API_KEY="sua_chave"
export GOOGLE_CSE_CX="seu_cx"
python3 gatehunter.py
```

---

## Proxies

Edite `proxies.txt` no formato `IP:PORTA:USUARIO:SENHA`. Proxies sao usadas apenas para analise de sites (nao para buscas).

---

## Arquivos de Saida

Salvos em `/sdcard/nh_files/`:

| Arquivo | Conteudo |
|---------|----------|
| `gatehunter_GATEWAY_TIMESTAMP.txt` | Relatorio completo |
| `gatehunter_GATEWAY_TIMESTAMP.json` | Dados JSON |
| `gatehunter_GATEWAY_TIMESTAMP_LOJAS.txt` | Lojas confirmadas |
| `gatehunter_GATEWAY_TIMESTAMP_all_urls.txt` | Todas URLs |
| `logs_gate_hunter.txt` | Debug log |

---

## Aviso Legal

Ferramenta destinada **exclusivamente para fins educacionais e pesquisa autorizada**.

---

**GateHunter v6.0.0** - NetHunter Supreme Edition | [CHANGELOG](CHANGELOG.md)
