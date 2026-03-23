#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  GATEHUNTER v6.1.0 - NETHUNTER SUPREME EDITION              ║
║  Payment Gateway OSINT - Multi-Engine Dork Scanner           ║
║  Brave + DDG + Bing + Google CSE API                         ║
║  4-Layer Validation + Ambiguous Gateway + Niche Filter       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import json
import time
import random
import urllib.request
import urllib.parse
import urllib.error
import traceback
import threading
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

VERSION = "6.1.0"

# ══════════════════════════════════════════════════════════════════
#                     CONFIGURACAO
# ══════════════════════════════════════════════════════════════════

OUTPUT_DIR = "/sdcard/nh_files"
FALLBACK_OUTPUT = os.path.expanduser("~/gatehunter_output")
LOG_FILE = "logs_gate_hunter.txt"
PROXY_FILE_PATHS = ["/sdcard/nh_files/proxies.txt", "proxies.txt"]

MAX_THREADS = 15
REQUEST_TIMEOUT = 20
STORE_SCORE_THRESHOLD = 12
SEARCH_DELAY_MIN = 5
SEARCH_DELAY_MAX = 10

# Google Custom Search Engine (opcional - 100 buscas/dia gratis)
GOOGLE_CSE_API_KEY = os.environ.get("GOOGLE_CSE_API_KEY", "")
GOOGLE_CSE_CX = os.environ.get("GOOGLE_CSE_CX", "")

# curl_cffi (melhor TLS fingerprint)
CFFI_OK = False
try:
    from curl_cffi import requests as cffi_requests
    CFFI_OK = True
except ImportError:
    pass

# ══════════════════════════════════════════════════════════════════
#                       CORES ANSI
# ══════════════════════════════════════════════════════════════════

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; W = "\033[97m"; D = "\033[90m"
RST = "\033[0m"; BOLD = "\033[1m"

# ══════════════════════════════════════════════════════════════════
#                    USER AGENTS PREMIUM
# ══════════════════════════════════════════════════════════════════

PREMIUM_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# ══════════════════════════════════════════════════════════════════
#                    NICHOS / CATEGORIAS
# ══════════════════════════════════════════════════════════════════

NICHOS = {
    "Todos": {"terms": [], "desc": "Buscar todos os tipos de loja"},
    "Roupas / Moda": {"terms": ["roupas", "moda", "camiseta", "vestido", "loja de roupas"], "desc": "Lojas de roupas e moda"},
    "Calcados / Tenis": {"terms": ["tenis", "sapato", "calcados", "sneaker", "loja de tenis"], "desc": "Lojas de calcados"},
    "Eletronicos": {"terms": ["eletronicos", "celular", "notebook", "tecnologia", "smartphone"], "desc": "Lojas de eletronicos"},
    "Gift Card": {"terms": ["gift card", "cartao presente", "vale presente", "giftcard"], "desc": "Sites de gift card"},
    "Joias / Relogios": {"terms": ["joias", "relogio", "anel", "colar", "brinco", "pulseira"], "desc": "Joalherias online"},
    "Cosmeticos / Beleza": {"terms": ["cosmeticos", "maquiagem", "perfume", "beleza", "skincare"], "desc": "Lojas de beleza"},
    "Suplementos / Saude": {"terms": ["suplemento", "whey", "vitamina", "saude", "fitness"], "desc": "Lojas de suplementos"},
    "Pet Shop": {"terms": ["pet shop", "racao", "cachorro", "gato", "pet"], "desc": "Pet shops online"},
    "Casa / Decoracao": {"terms": ["decoracao", "moveis", "casa", "cama mesa banho"], "desc": "Lojas de casa e decoracao"},
    "Alimentos / Bebidas": {"terms": ["alimentos", "bebidas", "cafe", "vinho", "gourmet"], "desc": "Lojas de alimentos"},
    "Esportes": {"terms": ["esportes", "academia", "fitness", "corrida", "futebol"], "desc": "Lojas de artigos esportivos"},
    "Infantil / Brinquedos": {"terms": ["brinquedo", "infantil", "crianca", "bebe", "kids"], "desc": "Lojas infantis"},
    "Cursos / Digital": {"terms": ["curso online", "ebook", "infoproduto", "mentoria"], "desc": "Produtos digitais"},
    "Assinatura / Recorrente": {"terms": ["assinatura", "clube", "box mensal", "plano mensal"], "desc": "Servicos de assinatura"},
}

# ══════════════════════════════════════════════════════════════════
#                    GATEWAYS DE PAGAMENTO
# ══════════════════════════════════════════════════════════════════

# Gateways com nomes ambíguos que podem ser confundidos com
# nomes de produtos, marcas ou palavras comuns.
# Para essas, exigimos evidência TÉCNICA forte (JS_SRC, IFRAME, FORM action
# apontando para domínio da gateway). TEXT_CONTEXT e LINK genérico NÃO confirmam.
AMBIGUOUS_GATEWAYS = {"Cielo", "Stripe", "Vindi", "Iugu", "Getnet"}

GATEWAYS = {
    "Asaas": {
        "desc": "Asaas - Plataforma de cobrancas e pagamentos",
        "signatures": ["asaas.com", "api.asaas", "cdn.asaas", "checkout.asaas"],
        "js_domains": ["asaas.com"],
        "dorks": [
            '"checkout asaas" comprar',
            '"asaas.com" formas de pagamento',
            '"asaas" pix boleto cartao loja',
            '"asaas" loja virtual pagamento',
            '"asaas" carrinho finalizar compra',
            'site:.com.br "asaas" comprar produto',
            '"asaas" ecommerce loja online',
            '"asaas" pagamento seguro loja',
            '"asaas" parcelamento produto',
            '"asaas" cobranca loja online',
            '"powered by asaas"',
            '"asaas" frete entrega loja',
        ],
    },
    "PagarMe": {
        "desc": "Pagar.me (Stone) - Gateway de pagamentos",
        "signatures": ["pagar.me", "pagarme", "api.pagar.me", "checkout.pagar.me"],
        "js_domains": ["pagar.me"],
        "dorks": [
            '"checkout.pagar.me"',
            '"pagar.me" formas de pagamento loja',
            '"pagar.me" loja online comprar',
            '"api.pagar.me" checkout',
            '"pagar.me" carrinho produto',
            'site:.com.br "pagar.me" comprar',
            '"pagar.me" pix boleto cartao',
            '"pagarme" loja virtual ecommerce',
            '"pagar.me" frete entrega produto',
            '"pagar.me" parcelamento loja',
            '"powered by pagar.me"',
            '"pagar.me" pagamento seguro',
        ],
    },
    "eRede": {
        "desc": "eRede (Itau) - Adquirente e gateway",
        "signatures": ["userede.com.br", "e.rede.com.br", "erede"],
        "js_domains": ["userede.com.br", "e.rede.com.br"],
        "dorks": [
            '"userede.com.br" loja comprar',
            '"e.rede" checkout pagamento',
            '"erede" formas de pagamento loja',
            'site:.com.br "erede" loja online',
            '"erede" pix cartao boleto loja',
            '"userede" ecommerce pagamento',
            '"erede" carrinho comprar produto',
            '"erede" pagamento seguro loja',
            '"erede" parcelamento loja online',
            '"erede" loja virtual checkout',
        ],
    },
    "PayFlow": {
        "desc": "PayFlow - Gateway de pagamentos digital",
        "signatures": ["payflow.com.br", "payflow", "api.payflow"],
        "js_domains": ["payflow.com.br"],
        "dorks": [
            '"payflow" formas de pagamento loja',
            '"payflow.com.br" checkout comprar',
            '"payflow" loja online pagamento',
            'site:.com.br "payflow" comprar',
            '"payflow" pix boleto cartao loja',
            '"payflow" carrinho finalizar compra',
            '"payflow" ecommerce loja virtual',
            '"payflow" pagamento seguro',
        ],
    },
    "AppMax": {
        "desc": "AppMax - Plataforma de vendas e pagamentos",
        "signatures": ["appmax.com.br", "appmax", "api.appmax"],
        "js_domains": ["appmax.com.br"],
        "dorks": [
            '"appmax" formas de pagamento loja',
            '"appmax.com.br" checkout comprar',
            '"appmax" loja online pagamento',
            'site:.com.br "appmax" comprar',
            '"appmax" pix boleto cartao loja',
            '"appmax" carrinho finalizar compra',
            '"appmax" ecommerce loja virtual',
            '"appmax" pagamento seguro',
        ],
    },
    "MercadoPago": {
        "desc": "Mercado Pago - Gateway e carteira digital",
        "signatures": ["mercadopago.com", "mercadopago", "checkout.mercadopago"],
        "js_domains": ["mercadopago.com"],
        "dorks": [
            '"mercado pago" formas de pagamento loja',
            '"mercadopago" checkout comprar',
            '"mercado pago" loja online pagamento',
            'site:.com.br "mercado pago" comprar produto',
            '"mercado pago" pix boleto cartao loja',
            '"mercado pago" carrinho comprar',
            '"mercadopago" loja virtual ecommerce',
            '"mercado pago" parcelamento loja',
            '"mercado pago" frete entrega comprar',
            '"sdk.mercadopago"',
            '"mercado pago" pagamento seguro',
            '"mercado pago" loja roupas comprar',
        ],
    },
    "PagSeguro": {
        "desc": "PagSeguro/PagBank - Gateway de pagamentos",
        "signatures": ["pagseguro.uol.com.br", "pagseguro", "pagbank"],
        "js_domains": ["pagseguro.uol.com.br", "pagseguro.com"],
        "dorks": [
            '"pagseguro" formas de pagamento loja',
            '"pagseguro" loja online comprar',
            '"pagseguro" checkout pagamento',
            '"pagbank" loja virtual comprar',
            'site:.com.br "pagseguro" comprar produto',
            '"pagseguro" pix boleto cartao loja',
            '"pagseguro" carrinho comprar',
            '"pagseguro" parcelamento loja',
            '"pagseguro" pagamento seguro',
            '"stc.pagseguro"',
            '"pagbank" ecommerce pagamento',
            '"pagseguro" frete entrega loja',
        ],
    },
    "Cielo": {
        "desc": "Cielo - Maior adquirente do Brasil",
        "signatures": ["cielo.com.br", "cieloecommerce", "api.cielo", "checkout.cielo"],
        "js_domains": ["cielo.com.br", "cieloecommerce.cielo.com.br"],
        "dorks": [
            '"cieloecommerce" checkout loja',
            '"api.cielo.com.br" pagamento',
            '"checkout.cielo" loja comprar',
            'site:.com.br "cielo ecommerce" loja',
            '"cielo" formas de pagamento loja online',
            '"cielo" adquirente pagamento loja',
            '"cielo" maquininha loja virtual',
            '"cielo 3.0" pagamento loja',
            '"cielo" pix boleto cartao loja online',
            '"cielo" parcelamento loja comprar',
            '"powered by cielo"',
            '"cielo" checkout seguro loja',
        ],
    },
    "Stripe": {
        "desc": "Stripe - Gateway global de pagamentos",
        "signatures": ["stripe.com", "js.stripe.com", "checkout.stripe"],
        "js_domains": ["stripe.com", "js.stripe.com"],
        "dorks": [
            '"js.stripe.com" loja comprar',
            '"checkout.stripe.com" comprar',
            '"stripe" formas de pagamento loja brasil',
            'site:.com.br "stripe" loja online comprar',
            '"stripe" ecommerce pagamento brasil',
            '"stripe" carrinho comprar produto',
            '"stripe" pagamento seguro loja',
            '"stripe elements" pagamento loja',
            '"pk_live_" stripe loja',
            '"stripe" checkout loja brasil',
        ],
    },
    "Hotmart": {
        "desc": "Hotmart - Plataforma de produtos digitais",
        "signatures": ["hotmart.com", "pay.hotmart", "hotmart"],
        "js_domains": ["hotmart.com"],
        "dorks": [
            '"pay.hotmart" comprar',
            '"hotmart" comprar curso online',
            '"hotmart" pagamento produto digital',
            '"hotmart" checkout comprar agora',
            '"hotmart" ebook comprar',
            '"hotmart" mentoria comprar',
            '"hotmart" pagamento pix boleto',
            '"hotmart" curso online matricula',
        ],
    },
    "Eduzz": {
        "desc": "Eduzz - Plataforma de infoprodutos",
        "signatures": ["eduzz.com", "eduzz", "sun.eduzz"],
        "js_domains": ["eduzz.com"],
        "dorks": [
            '"sun.eduzz" comprar',
            '"eduzz" comprar curso online',
            '"eduzz" pagamento produto digital',
            '"eduzz" checkout comprar',
            '"eduzz" ebook comprar',
            '"eduzz" pagamento pix boleto',
            '"eduzz" curso online matricula',
            '"eduzz" mentoria comprar agora',
        ],
    },
    "Kiwify": {
        "desc": "Kiwify - Plataforma de vendas digitais",
        "signatures": ["kiwify.com.br", "kiwify", "pay.kiwify"],
        "js_domains": ["kiwify.com.br"],
        "dorks": [
            '"pay.kiwify" comprar',
            '"kiwify" comprar curso online',
            '"kiwify" pagamento produto digital',
            '"kiwify" checkout comprar',
            '"kiwify" ebook comprar',
            '"kiwify" pagamento pix boleto',
            '"kiwify" curso online matricula',
            '"kiwify" mentoria comprar agora',
        ],
    },
    "Vindi": {
        "desc": "Vindi - Plataforma de pagamentos recorrentes",
        "signatures": ["vindi.com.br", "api.vindi", "app.vindi"],
        "js_domains": ["vindi.com.br"],
        "dorks": [
            '"app.vindi" assinatura',
            '"vindi" pagamento recorrente loja',
            '"vindi" assinatura plano mensal',
            'site:.com.br "vindi" pagamento loja',
            '"vindi" checkout comprar',
            '"vindi" cobranca recorrente loja',
            '"vindi" formas de pagamento',
            '"api.vindi" pagamento',
        ],
    },
    "Iugu": {
        "desc": "Iugu - Gateway e plataforma financeira",
        "signatures": ["iugu.com", "api.iugu", "faturas.iugu"],
        "js_domains": ["iugu.com"],
        "dorks": [
            '"faturas.iugu" pagamento',
            '"iugu" formas de pagamento loja',
            '"api.iugu" checkout',
            'site:.com.br "iugu" pagamento loja',
            '"iugu" pix boleto cartao loja',
            '"iugu" cobranca loja online',
            '"iugu" pagamento seguro loja',
            '"iugu" assinatura plano',
        ],
    },
    "Getnet": {
        "desc": "Getnet (Santander) - Adquirente e gateway",
        "signatures": ["getnet.com.br", "api.getnet", "checkout.getnet"],
        "js_domains": ["getnet.com.br"],
        "dorks": [
            '"api.getnet" pagamento loja',
            '"checkout.getnet" comprar',
            '"getnet" formas de pagamento loja',
            'site:.com.br "getnet" loja online',
            '"getnet" pix cartao boleto loja',
            '"getnet" ecommerce pagamento',
            '"getnet" pagamento seguro loja',
            '"getnet" adquirente loja virtual',
        ],
    },
}

# ══════════════════════════════════════════════════════════════════
#                    DOMAIN BLACKLIST (MEGA)
# ══════════════════════════════════════════════════════════════════

DOMAIN_BLACKLIST = {
    # ── Proprias gateways ──
    "asaas.com", "pagar.me", "pagarme.com.br", "userede.com.br", "rede.com.br",
    "payflow.com.br", "appmax.com.br", "mercadopago.com", "mercadopago.com.br",
    "pagseguro.uol.com.br", "pagseguro.com", "pagbank.com.br", "cielo.com.br",
    "stripe.com", "hotmart.com", "eduzz.com", "kiwify.com.br", "vindi.com.br",
    "iugu.com", "getnet.com.br", "stone.com.br", "mundipagg.com",
    # ── Plataformas e-commerce (docs/ajuda) ──
    "nuvemshop.com.br", "tray.com.br", "lojaintegrada.com.br", "vtex.com",
    "shopify.com", "woocommerce.com", "magento.com", "yampi.com.br",
    "cartpanda.com", "wbuy.com.br", "toplojas.com.br", "bwcommerce.com.br",
    "moblix.com.br", "bagy.com.br", "loja.com.br",
    # ── Redes sociais e conteudo ──
    "youtube.com", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "tiktok.com", "pinterest.com", "reddit.com", "threads.net",
    # ── Repositorios e dev ──
    "github.com", "github.io", "gitlab.com", "bitbucket.org", "stackoverflow.com",
    "npmjs.com", "packagist.org", "pypi.org", "codesandbox.io", "codepen.io",
    # ── Blogs e noticias ──
    "medium.com", "wordpress.com", "blogspot.com", "tumblr.com",
    "enotas.com.br", "digitalmanager.guru", "resultadosdigitais.com.br",
    "rockcontent.com", "neilpatel.com", "hubspot.com", "digitei.com",
    "ecommercebrasil.com.br", "mundodomarketing.com.br", "canaltech.com.br",
    "techtudo.com.br", "tecnoblog.net", "olhardigital.com.br",
    # ── Comparadores, reviews, cupons ──
    "reclameaqui.com.br", "trustpilot.com", "g2.com", "capterra.com",
    "b2bstack.com.br", "comparatec.com.br", "desconto.com.br", "cupom.com",
    "meliuz.com.br", "pelando.com.br", "promobit.com.br", "cuponation.com.br",
    # ── Educacao e docs ──
    "wikipedia.org", "wikimedia.org", "wikidata.org", "docs.google.com",
    "drive.google.com", "slideshare.net", "scribd.com",
    # ── Governo e institucional ──
    "gov.br", "bcb.gov.br", "receita.fazenda.gov.br", "sec.gov",
    # ── Buscadores ──
    "google.com", "google.com.br", "bing.com", "yahoo.com", "duckduckgo.com",
    "brave.com", "search.brave.com",
    # ── Marketplaces grandes ──
    "amazon.com", "amazon.com.br", "mercadolivre.com.br", "aliexpress.com",
    "olx.com.br", "magazineluiza.com.br", "americanas.com.br", "casasbahia.com.br",
    "shopee.com.br", "wish.com", "ebay.com",
    # ── Automacao e integracao ──
    "albato.com", "zapier.com", "make.com", "n8n.io", "pluga.co",
    # ── Empregos e financeiro ──
    "glassdoor.com", "glassdoor.com.br", "indeed.com", "catho.com.br",
    "crunchbase.com", "bloomberg.com", "investing.com", "infomoney.com",
    # ── Outros irrelevantes ──
    "zhihu.com", "baidu.com", "hackerone.com", "bibleinfo.com",
    "apps.apple.com", "play.google.com", "totvs.com", "isin.org",
    "mobiletransaction.org", "linknacional.com.br", "lojavirtualprotegida.com.br",
    "zendesk.com", "freshdesk.com", "intercom.com", "jivochat.com",
    "banco.bradesco", "bb.com.br", "itau.com.br", "santander.com.br",
    "cielofragrance.com", "community.shopify.com", "wordpress.org",
    "investidorsardinha.r7.com", "fintech.com.br", "socialhub.pro",
    "loja5.com.br", "basedeconhecimento.tray.com.br",
    # ── Sites de plugins/modulos ──
    "envato.com", "themeforest.net", "codecanyon.net",
}

# Palavras no domínio que indicam site informacional
DOMAIN_BAD_WORDS = [
    "developer", "docs", "blog", "help", "support", "suporte", "ajuda",
    "api", "status", "central", "atendimento", "basedeconhecimento",
    "kb", "wiki", "faq", "forum", "community", "comunidade", "learn",
    "academy", "tutorial", "curso", "review", "comparar",
]

BAD_PATH_PATTERNS = [
    "/blog/", "/blog?", "/docs/", "/doc/", "/api/", "/developer/",
    "/help/", "/support/", "/suporte/", "/ajuda/", "/tutorial/",
    "/artigo/", "/article/", "/como-", "/how-to", "/changelog",
    "/status/", "/pricing/", "/planos/", "/careers/", "/vagas/",
    "/about/", "/sobre/", "/press/", "/imprensa/", "/parceiros/",
    "/integracoes/", "/integrations/", "/plugins/", "/apps/",
    "/connect/", "/marketplace/", "/modulo/", "/module/",
]

# ══════════════════════════════════════════════════════════════════
#                    DEBUG LOGGER
# ══════════════════════════════════════════════════════════════════

class DebugLogger:
    def __init__(self):
        self.log_path = None
        self._lock = threading.Lock()

    def start_session(self):
        output = OUTPUT_DIR if os.path.isdir(OUTPUT_DIR) else FALLBACK_OUTPUT
        os.makedirs(output, exist_ok=True)
        self.log_path = os.path.join(output, LOG_FILE)
        self._write("=" * 80)
        self._write(f"GATEHUNTER v{VERSION} - DEBUG LOG INICIADO")
        self._write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._write(f"Log path: {self.log_path}")
        self._write(f"Python: {sys.version}")
        self._write(f"Platform: {sys.platform}")
        self._write(f"curl_cffi: {CFFI_OK}")
        self._write(f"Google CSE: {'Configurado' if GOOGLE_CSE_API_KEY else 'Nao configurado'}")
        self._write("=" * 80)

    def _write(self, msg, level="INFO"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        thread = threading.current_thread().name[:12]
        line = f"{ts} | {level:8s} | {thread:12s} | {msg}"
        with self._lock:
            if self.log_path:
                try:
                    with open(self.log_path, "a", encoding="utf-8") as f:
                        f.write(line + "\n")
                except:
                    pass

    def debug(self, msg): self._write(msg, "DEBUG")
    def info(self, msg): self._write(msg, "INFO")
    def warning(self, msg): self._write(msg, "WARNING")
    def error(self, msg): self._write(msg, "ERROR")

log = DebugLogger()

# ══════════════════════════════════════════════════════════════════
#                    PROXY ROTATOR
# ══════════════════════════════════════════════════════════════════

class ProxyRotator:
    def __init__(self):
        self.proxies = []
        self.index = 0
        self._lock = threading.Lock()
        self._load_proxies()

    def _load_proxies(self):
        for path in PROXY_FILE_PATHS:
            if os.path.isfile(path):
                log.info(f"Loading proxies from: {path}")
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = line.split(":")
                            if len(parts) >= 2:
                                proxy = {
                                    "ip": parts[0], "port": parts[1],
                                    "user": parts[2] if len(parts) > 2 else "",
                                    "pass": parts[3] if len(parts) > 3 else "",
                                }
                                self.proxies.append(proxy)
                break
        log.info(f"Total proxies loaded: {len(self.proxies)}")

    def get_next(self) -> Optional[Dict]:
        if not self.proxies:
            return None
        with self._lock:
            proxy = self.proxies[self.index % len(self.proxies)]
            self.index += 1
            return proxy

    def get_proxy_url(self, proxy: Dict) -> str:
        if proxy["user"]:
            return f"http://{proxy['user']}:{proxy['pass']}@{proxy['ip']}:{proxy['port']}"
        return f"http://{proxy['ip']}:{proxy['port']}"

# ══════════════════════════════════════════════════════════════════
#                  FINGERPRINT GENERATOR
# ══════════════════════════════════════════════════════════════════

class FingerprintGenerator:
    PLATFORMS = [
        {"os": "Windows", "sec_ch_ua_platform": '"Windows"'},
        {"os": "macOS", "sec_ch_ua_platform": '"macOS"'},
        {"os": "Linux", "sec_ch_ua_platform": '"Linux"'},
    ]

    def generate(self) -> Dict:
        ua = random.choice(PREMIUM_USER_AGENTS)
        plat = random.choice(self.PLATFORMS)
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-CH-UA-Platform": plat["sec_ch_ua_platform"],
        }
        log.debug(f"FINGERPRINT | UA={ua[:60]} | Platform={plat['sec_ch_ua_platform']}")
        return headers

fingerprint = FingerprintGenerator()

# ══════════════════════════════════════════════════════════════════
#                   SMART REQUESTER
# ══════════════════════════════════════════════════════════════════

class SmartRequester:
    IMPERSONATE_TARGETS = ["chrome120", "chrome119", "chrome116", "safari17_0", "safari15_5", "edge101"]

    def __init__(self, proxy_rotator: ProxyRotator):
        self.proxy = proxy_rotator
        self.stats = {"requests": 0, "success": 0, "failed": 0, "blocked": 0}
        self._lock = threading.Lock()

    def get(self, url: str, use_proxy: bool = True, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
        with self._lock:
            self.stats["requests"] += 1

        headers = fingerprint.generate()
        proxy = self.proxy.get_next() if use_proxy else None

        # Tentar com curl_cffi
        if CFFI_OK:
            try:
                imp = random.choice(self.IMPERSONATE_TARGETS)
                proxies = None
                if proxy:
                    purl = self.proxy.get_proxy_url(proxy)
                    proxies = {"http": purl, "https": purl}

                r = cffi_requests.get(url, impersonate=imp, timeout=timeout, headers=headers, proxies=proxies, allow_redirects=True)

                log.debug(f"HTTP GET | status={r.status_code} | proxy={proxy['ip'] if proxy else 'DIRECT'} | imp={imp} | url={url[:100]}")

                if r.status_code == 429:
                    with self._lock:
                        self.stats["blocked"] += 1
                    return None

                if r.status_code == 200:
                    with self._lock:
                        self.stats["success"] += 1
                    return r.text

            except Exception as e:
                log.debug(f"curl_cffi error: {type(e).__name__}: {str(e)[:80]}")

        # Fallback urllib
        try:
            req = urllib.request.Request(url, headers=headers)
            if proxy and proxy["user"]:
                proxy_handler = urllib.request.ProxyHandler({
                    "http": self.proxy.get_proxy_url(proxy),
                    "https": self.proxy.get_proxy_url(proxy),
                })
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()

            resp = opener.open(req, timeout=timeout)
            html = resp.read().decode("utf-8", errors="ignore")

            log.debug(f"HTTP urllib | status={resp.status} | url={url[:100]}")
            with self._lock:
                self.stats["success"] += 1
            return html

        except Exception as e:
            log.debug(f"urllib error: {type(e).__name__}: {str(e)[:80]}")
            with self._lock:
                self.stats["failed"] += 1
            return None


# ══════════════════════════════════════════════════════════════════
#                    DORK ENGINE (MULTI-ENGINE)
# ══════════════════════════════════════════════════════════════════

class DorkEngine:
    """Motor de busca multi-engine com rotacao: Brave + DDG + Bing + Google CSE"""

    def __init__(self, requester: SmartRequester):
        self.requester = requester
        self.seen_domains = set()
        self._lock = threading.Lock()
        self._engine_index = 0

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""

    def _is_valid_url(self, url: str) -> bool:
        """Filtro de URL em 4 camadas: dominio, bad words, path, dedup"""
        domain = self._extract_domain(url)
        if not domain:
            return False

        # Camada 1: Blacklist de dominio exato
        for bl in DOMAIN_BLACKLIST:
            if domain == bl or domain.endswith("." + bl):
                log.debug(f"FILTERED [BLACKLIST] | {url[:80]} | match={bl}")
                return False

        # Camada 2: Palavras ruins no dominio (developer, docs, blog, etc)
        domain_parts = domain.replace(".", " ").replace("-", " ").lower()
        for bad_word in DOMAIN_BAD_WORDS:
            if bad_word in domain_parts:
                log.debug(f"FILTERED [DOMAIN_WORD] | {url[:80]} | word={bad_word}")
                return False

        # Camada 3: Path ruim
        url_lower = url.lower()
        for bad in BAD_PATH_PATTERNS:
            if bad in url_lower:
                log.debug(f"FILTERED [PATH] | {url[:80]} | match={bad}")
                return False

        # Camada 4: Dedup por dominio
        with self._lock:
            if domain in self.seen_domains:
                log.debug(f"FILTERED [DEDUP] | {url[:80]}")
                return False
            self.seen_domains.add(domain)

        log.info(f"URL PASSED | {url[:100]} | domain={domain}")
        return True

    def _clean_url(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean.endswith("/"):
                clean = clean[:-1]
            return clean
        except:
            return url

    # ─────────────────────────────────────────────────
    #  ENGINE 1: BRAVE SEARCH
    # ─────────────────────────────────────────────────
    def search_brave(self, query: str, max_pages: int = 3) -> Set[str]:
        urls = set()
        log.info(f"BRAVE SEARCH | query={query}")

        headers = {
            "User-Agent": random.choice(PREMIUM_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }

        for page in range(max_pages):
            try:
                q = urllib.parse.quote(query)
                offset = page * 10
                url = f"https://search.brave.com/search?q={q}&source=web&offset={offset}"

                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req, timeout=15)
                html = resp.read().decode("utf-8", errors="ignore")

                page_urls = set()
                for m in re.finditer(r'href="(https?://[^"]+)"', html):
                    u = m.group(1)
                    domain = self._extract_domain(u)
                    if domain and not any(x in domain for x in ["brave.com", "search.brave", "googleapis", "gstatic"]):
                        page_urls.add(self._clean_url(u))

                new = page_urls - urls
                urls.update(page_urls)
                log.info(f"BRAVE page {page} | found={len(page_urls)} | new={len(new)}")

                if page < max_pages - 1:
                    time.sleep(random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX))

            except urllib.error.HTTPError as e:
                if e.code == 429:
                    log.warning(f"BRAVE RATE LIMITED | page={page} | waiting 20s")
                    time.sleep(20)
                else:
                    log.error(f"BRAVE ERROR | page={page} | {e}")
                break
            except Exception as e:
                log.error(f"BRAVE ERROR | page={page} | {type(e).__name__}: {str(e)[:80]}")
                break

        log.info(f"BRAVE TOTAL | query={query[:60]} | urls={len(urls)}")
        return urls

    # ─────────────────────────────────────────────────
    #  ENGINE 2: DUCKDUCKGO HTML
    # ─────────────────────────────────────────────────
    def search_ddg(self, query: str, max_pages: int = 2) -> Set[str]:
        urls = set()
        log.info(f"DDG SEARCH | query={query}")

        headers = {
            "User-Agent": random.choice(PREMIUM_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }

        for page in range(max_pages):
            try:
                q = urllib.parse.quote(query)
                if page == 0:
                    url = f"https://html.duckduckgo.com/html/?q={q}"
                else:
                    url = f"https://html.duckduckgo.com/html/?q={q}&s={page*30}&dc={page*30+1}"

                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req, timeout=15)
                html = resp.read().decode("utf-8", errors="ignore")

                page_urls = set()
                for m in re.finditer(r'uddg=(https?%3A[^&"\']+)', html):
                    u = urllib.parse.unquote(m.group(1))
                    if "duckduckgo" not in u:
                        page_urls.add(self._clean_url(u))

                for m in re.finditer(r'class="result__a"[^>]*href="(https?://[^"]+)"', html):
                    u = m.group(1)
                    if "duckduckgo" not in u:
                        page_urls.add(self._clean_url(u))

                new = page_urls - urls
                urls.update(page_urls)
                log.info(f"DDG page {page} | found={len(page_urls)} | new={len(new)}")

                if resp.status == 202:
                    log.warning("DDG returned 202 (rate limited)")
                    break

                if page < max_pages - 1:
                    time.sleep(random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX))

            except Exception as e:
                log.error(f"DDG ERROR | page={page} | {type(e).__name__}: {str(e)[:80]}")
                break

        log.info(f"DDG TOTAL | query={query[:60]} | urls={len(urls)}")
        return urls

    # ─────────────────────────────────────────────────
    #  ENGINE 3: BING
    # ─────────────────────────────────────────────────
    def search_bing(self, query: str, max_pages: int = 2) -> Set[str]:
        urls = set()
        log.info(f"BING SEARCH | query={query}")

        for page in range(max_pages):
            try:
                q = urllib.parse.quote(query)
                first = page * 10 + 1
                url = f"https://www.bing.com/search?q={q}&first={first}&count=20&setlang=pt-BR&cc=BR"

                headers = {
                    "User-Agent": random.choice(PREMIUM_USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "pt-BR,pt;q=0.9",
                    "Cookie": "SRCHHPGUSR=ADLT=OFF&NRSLT=20&SRCHLANG=pt-BR",
                }
                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req, timeout=15)
                html = resp.read().decode("utf-8", errors="ignore")

                page_urls = set()
                for m in re.finditer(r'<cite[^>]*>(https?://[^<]+)</cite>', html):
                    u = re.sub(r'<[^>]+>', '', m.group(1)).strip().split(" ")[0]
                    if u.startswith("http"):
                        page_urls.add(self._clean_url(u))

                for m in re.finditer(r'<h2[^>]*><a[^>]+href="(https?://[^"]+)"', html):
                    u = m.group(1)
                    if "bing.com" not in u and "microsoft.com" not in u:
                        page_urls.add(self._clean_url(u))

                new = page_urls - urls
                urls.update(page_urls)
                log.info(f"BING page {page} | found={len(page_urls)} | new={len(new)}")

                if page < max_pages - 1:
                    time.sleep(random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX))

            except Exception as e:
                log.error(f"BING ERROR | page={page} | {type(e).__name__}: {str(e)[:80]}")
                break

        log.info(f"BING TOTAL | query={query[:60]} | urls={len(urls)}")
        return urls

    # ─────────────────────────────────────────────────
    #  ENGINE 4: GOOGLE CSE API (opcional)
    # ─────────────────────────────────────────────────
    def search_google_cse(self, query: str, max_pages: int = 2) -> Set[str]:
        if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX:
            return set()

        urls = set()
        log.info(f"GOOGLE CSE | query={query}")

        for page in range(max_pages):
            try:
                start = page * 10 + 1
                params = urllib.parse.urlencode({
                    "key": GOOGLE_CSE_API_KEY, "cx": GOOGLE_CSE_CX,
                    "q": query, "start": start, "num": 10,
                    "lr": "lang_pt", "cr": "countryBR",
                })
                url = f"https://www.googleapis.com/customsearch/v1?{params}"

                req = urllib.request.Request(url)
                resp = urllib.request.urlopen(req, timeout=15)
                data = json.loads(resp.read().decode("utf-8"))

                for item in data.get("items", []):
                    link = item.get("link", "")
                    if link:
                        urls.add(self._clean_url(link))

                log.info(f"GOOGLE CSE page {page} | items={len(data.get('items', []))}")
                if page < max_pages - 1:
                    time.sleep(1)

            except Exception as e:
                log.error(f"GOOGLE CSE ERROR | {type(e).__name__}: {str(e)[:80]}")
                break

        return urls

    # ─────────────────────────────────────────────────
    #  ROTACAO DE ENGINES POR DORK
    # ─────────────────────────────────────────────────
    def _get_next_engine(self) -> str:
        """Rotaciona entre engines para evitar rate limit"""
        engines = ["brave", "ddg", "bing"]
        engine = engines[self._engine_index % len(engines)]
        self._engine_index += 1
        return engine

    def search_single_engine(self, dork: str, engine: str) -> Set[str]:
        """Buscar em uma engine específica"""
        if engine == "brave":
            return self.search_brave(dork, max_pages=3)
        elif engine == "ddg":
            return self.search_ddg(dork, max_pages=2)
        elif engine == "bing":
            return self.search_bing(dork, max_pages=2)
        elif engine == "cse":
            return self.search_google_cse(dork, max_pages=2)
        return set()

    def collect_urls(self, dorks: List[str], niche_terms: List[str] = None) -> List[str]:
        """Coletar URLs de todas as dorks com rotacao de engines e filtro de nicho"""
        all_raw_urls = set()
        valid_urls = []

        expanded_dorks = list(dorks)

        # Se tem nicho, adicionar variações com termos do nicho
        if niche_terms:
            for dork in dorks[:4]:
                for term in niche_terms[:2]:
                    expanded_dorks.append(f"{dork} {term}")

        log.info(f"COLLECTING | base_dorks={len(dorks)} | expanded={len(expanded_dorks)} | niche={niche_terms}")

        for i, dork in enumerate(expanded_dorks, 1):
            # Rotação de engine: cada dork vai para uma engine diferente
            engine = self._get_next_engine()

            print(f"  {D}{datetime.now().strftime('%H:%M:%S')}{RST} [{C}-{RST}] Dork [{i}/{len(expanded_dorks)}]: {Y}{dork[:55]}{RST} [{M}{engine.upper()}{RST}]")
            log.info(f"DORK [{i}/{len(expanded_dorks)}] | engine={engine} | {dork}")

            raw_urls = self.search_single_engine(dork, engine)

            # Se a engine principal retornou pouco, tentar outra
            if len(raw_urls) < 3:
                backup_engine = self._get_next_engine()
                if backup_engine != engine:
                    log.info(f"LOW RESULTS ({len(raw_urls)}), trying backup engine: {backup_engine}")
                    backup_urls = self.search_single_engine(dork, backup_engine)
                    raw_urls.update(backup_urls)

            new_raw = raw_urls - all_raw_urls
            all_raw_urls.update(raw_urls)

            for url in new_raw:
                if self._is_valid_url(url):
                    valid_urls.append(url)

            print(f"  {D}{datetime.now().strftime('%H:%M:%S')}{RST} [{G}+{RST}] -> {len(new_raw)} raw, {G}{len(valid_urls)}{RST} validas acumuladas")
            log.info(f"DORK RESULT | raw_new={len(new_raw)} | valid_total={len(valid_urls)}")

            # Delay entre dorks
            if i < len(expanded_dorks):
                delay = random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX)
                time.sleep(delay)

        # Se Google CSE está configurado, usar como bonus
        if GOOGLE_CSE_API_KEY:
            for dork in dorks[:3]:
                cse_urls = self.search_google_cse(dork, max_pages=1)
                new_cse = cse_urls - all_raw_urls
                all_raw_urls.update(cse_urls)
                for url in new_cse:
                    if self._is_valid_url(url):
                        valid_urls.append(url)

        log.info(f"COLLECTION DONE | total_raw={len(all_raw_urls)} | valid={len(valid_urls)}")
        return valid_urls


# ══════════════════════════════════════════════════════════════════
#                    SITE ANALYZER
# ══════════════════════════════════════════════════════════════════

class SiteAnalyzer:
    """Analisa sites para confirmar gateway e classificar nicho"""

    ECOMMERCE_PLATFORMS = {
        "WooCommerce": ["woocommerce", "wc-ajax", "add-to-cart", "wp-content/plugins/woocommerce"],
        "Shopify": ["cdn.shopify", "myshopify", "shopify-section"],
        "VTEX": ["vtexcommercestable", "vteximg", "vtex.com"],
        "Magento": ["mage-", "checkout/cart", "magento"],
        "Nuvemshop": ["nuvemshop", "lojanuvem", "nuvem.shop"],
        "Tray": ["tray.com.br", "traycorp", "tray-checkout"],
        "Loja Integrada": ["lojaintegrada", "loja-integrada"],
        "OpenCart": ["opencart", "route=product", "route=checkout"],
        "PrestaShop": ["prestashop", "presta-shop", "module/ps_"],
        "Yampi": ["yampi", "checkout.yampi"],
        "CartPanda": ["cartpanda"],
        "Bagy": ["bagy.com.br"],
    }

    NICHE_KEYWORDS = {
        "Loja de Roupas / Moda": ["roupa", "camiseta", "vestido", "blusa", "calca", "jeans", "moda", "fashion", "look", "colecao", "feminino", "masculino", "plus size"],
        "Loja de Calcados / Tenis": ["tenis", "sapato", "bota", "sandalia", "chinelo", "calcado", "sneaker", "sapatilha"],
        "Loja de Eletronicos": ["celular", "smartphone", "notebook", "tablet", "fone", "headset", "eletronico", "informatica", "pc gamer"],
        "Gift Card / Vale Presente": ["gift card", "giftcard", "vale presente", "cartao presente", "credito digital", "recarga"],
        "Joalheria / Relogios": ["joia", "anel", "colar", "brinco", "pulseira", "relogio", "ouro", "prata", "alianca"],
        "Cosmeticos / Beleza": ["cosmetico", "maquiagem", "perfume", "batom", "skincare", "creme", "hidratante", "beleza", "cabelo"],
        "Suplementos / Saude": ["suplemento", "whey", "creatina", "vitamina", "proteina", "pre treino", "fitness"],
        "Pet Shop": ["pet", "racao", "cachorro", "gato", "petisco", "coleira", "veterinario"],
        "Casa / Decoracao": ["decoracao", "movel", "sofa", "mesa", "cadeira", "cortina", "tapete", "luminaria"],
        "Alimentos / Bebidas": ["alimento", "cafe", "vinho", "cerveja", "chocolate", "gourmet", "organico"],
        "Esportes / Fitness": ["esporte", "academia", "corrida", "futebol", "bicicleta", "yoga", "natacao"],
        "Infantil / Brinquedos": ["brinquedo", "infantil", "crianca", "bebe", "kids", "boneca", "lego"],
        "Farmacia / Saude": ["farmacia", "medicamento", "remedio", "saude", "dermocosmetico"],
        "Loja Geral / Variedades": ["loja", "produto", "comprar", "oferta", "promocao", "desconto"],
    }

    def __init__(self, requester: SmartRequester, gateway_key: str):
        self.requester = requester
        self.gateway = GATEWAYS[gateway_key]
        self.gateway_key = gateway_key
        self.is_ambiguous = gateway_key in AMBIGUOUS_GATEWAYS

    def analyze(self, url: str) -> Optional[Dict]:
        log.info(f"ANALYZING | {url}")

        try:
            html = self.requester.get(url, use_proxy=True, timeout=REQUEST_TIMEOUT)
            if not html:
                log.warning(f"NO HTML | {url}")
                return None

            html_lower = html.lower()
            log.debug(f"HTML SIZE | {len(html)} bytes | {url[:80]}")

            # ── Store Validator ──
            store_score, score_details = self._calculate_store_score(html_lower)
            log.info(f"STORE SCORE | score={store_score} | threshold={STORE_SCORE_THRESHOLD} | {url[:80]}")

            if store_score < STORE_SCORE_THRESHOLD:
                log.info(f"REJECTED [LOW SCORE] | score={store_score} | {url[:80]}")
                return None

            # ── Confirmar gateway no HTML ──
            gateway_confirmed, gateway_evidence = self._confirm_gateway(html, html_lower, url)
            log.info(f"GATEWAY CHECK | confirmed={gateway_confirmed} | evidence={gateway_evidence[:80] if gateway_evidence else 'NONE'} | {url[:80]}")

            # ── Detectar plataforma ──
            platform = self._detect_platform(html_lower)

            # ── Classificar nicho ──
            niche = self._classify_niche(html_lower)

            # ── Extrair metadados ──
            title = self._extract_title(html)
            description = self._extract_meta(html, "description")
            emails = self._extract_emails(html)
            phones = self._extract_phones(html)

            result = {
                "url": url,
                "domain": self._extract_domain(url),
                "title": title[:200] if title else "",
                "description": description[:300] if description else "",
                "gateway_confirmed": gateway_confirmed,
                "gateway_evidence": gateway_evidence,
                "store_score": store_score,
                "platform": platform,
                "niche": niche,
                "emails": emails[:5],
                "phones": phones[:5],
                "html_size": len(html),
                "timestamp": datetime.now().isoformat(),
            }

            status = "CONFIRMED" if gateway_confirmed else "STORE_ONLY"
            log.info(f"{status} | score={store_score} | niche={niche} | platform={platform} | {url[:80]}")
            return result

        except Exception as e:
            log.error(f"ANALYZE ERROR | {url[:80]} | {type(e).__name__}: {str(e)[:100]}")
            return None

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""

    def _calculate_store_score(self, html_lower: str) -> Tuple[int, List[str]]:
        """Calcular score de loja real (-100 a +100)"""
        score = 0
        details = []

        # ── SINAIS POSITIVOS ──
        positive_signals = [
            (r'R\$\s*\d+[.,]\d{2}', 6, "PRECO_BRL"),
            (r'add.?to.?cart|adicionar.?ao.?carrinho|comprar.?agora|buy.?now', 5, "ADD_CART"),
            (r'carrinho|cart|sacola|bag', 4, "CARRINHO"),
            (r'checkout|finalizar.?compra|fechar.?pedido', 5, "CHECKOUT"),
            (r'frete|entrega|envio|shipping|sedex|correios', 4, "FRETE"),
            (r'cep|calcular.?frete|prazo.?de.?entrega', 3, "CEP_FRETE"),
            (r'estoque|disponivel|em.?estoque|in.?stock', 3, "ESTOQUE"),
            (r'tamanho|size|cor|color|variacao', 3, "VARIACAO"),
            (r'parcelamento|parcela|vezes.?sem.?juros|installment', 4, "PARCELAMENTO"),
            (r'pix|boleto|cartao.?de.?credito|credit.?card', 4, "FORMA_PGTO"),
            (r'avaliacao|review|estrela|star|nota', 2, "REVIEW"),
            (r'wishlist|lista.?de.?desejos|favorito', 2, "WISHLIST"),
            (r'minha.?conta|my.?account|cadastr', 2, "CONTA"),
        ]

        for pattern, points, name in positive_signals:
            matches = len(re.findall(pattern, html_lower))
            if matches > 0:
                add = min(points * min(matches, 3), points * 3)
                score += add
                details.append(f"+{add} {name}({matches}x)")

        # ── SINAIS DE PLATAFORMA ──
        for platform, keywords in self.ECOMMERCE_PLATFORMS.items():
            for kw in keywords:
                if kw in html_lower:
                    score += 5
                    details.append(f"+5 PLATFORM({platform})")
                    break

        # ── SINAIS NEGATIVOS ──
        negative_signals = [
            (r'documentacao|documentation|api.?reference', -15, "DOCS"),
            (r'tutorial|how.?to|como.?fazer|passo.?a.?passo', -10, "TUTORIAL"),
            (r'blog.?post|artigo|article|publicado.?em|posted.?on', -10, "BLOG"),
            (r'changelog|release.?notes|versao|version.?\d', -12, "CHANGELOG"),
            (r'sdk|npm.?install|pip.?install|composer|yarn.?add', -15, "SDK"),
            (r'endpoint|api.?key|token|webhook|callback', -10, "API"),
            (r'integra[cç][aã]o.?com|integration.?with|plugin.?de|modulo.?de', -8, "INTEGRACAO"),
            (r'comparativo|versus|vs\.|alternativa|competitor', -8, "COMPARATIVO"),
            (r'reclama[cç][aã]o|reclamar|denunciar|fraude', -10, "RECLAMACAO"),
            (r'vagas|careers|trabalhe.?conosco|hiring', -10, "VAGAS"),
            (r'cupom.?de.?desconto|codigo.?promocional|coupon.?code', -8, "CUPOM_SITE"),
        ]

        for pattern, points, name in negative_signals:
            matches = len(re.findall(pattern, html_lower))
            if matches > 0:
                add = max(points * min(matches, 2), points * 2)
                score += add
                details.append(f"{add} {name}({matches}x)")

        # ── PENALIDADE: titulo contém "plugin" ou "módulo" ──
        title_lower = ""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_lower)
        if title_match:
            title_lower = title_match.group(1).lower()
            if any(w in title_lower for w in ["plugin", "modulo", "módulo", "extensão", "extensao", "addon"]):
                score -= 30
                details.append("-30 PLUGIN_TITLE")

        log.debug(f"SCORE DETAILS | score={score} | {' | '.join(details[:12])}")
        return score, details

    def _confirm_gateway(self, html: str, html_lower: str, url: str) -> Tuple[bool, str]:
        """Confirmar presença da gateway no HTML via assinaturas técnicas.
        Para gateways ambíguas, exige evidência FORTE (JS_SRC, IFRAME, FORM para domínio da gateway)."""
        signatures = self.gateway["signatures"]
        js_domains = self.gateway.get("js_domains", [])
        evidence_parts = []
        strong_evidence = False

        # Zona 1: Tags <script src="..."> (EVIDENCIA FORTE)
        for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE):
            src = m.group(1).lower()
            for jd in js_domains:
                if jd in src:
                    evidence_parts.append(f"JS_SRC:{m.group(1)[:80]}")
                    strong_evidence = True
            if not strong_evidence:
                for sig in signatures:
                    if sig in src:
                        evidence_parts.append(f"JS_SRC:{m.group(1)[:80]}")
                        strong_evidence = True

        # Zona 2: Tags <iframe src="..."> (EVIDENCIA FORTE)
        for m in re.finditer(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE):
            src = m.group(1).lower()
            for jd in js_domains:
                if jd in src:
                    evidence_parts.append(f"IFRAME:{m.group(1)[:80]}")
                    strong_evidence = True

        # Zona 3: Tags <form action="..."> para domínio da gateway (EVIDENCIA FORTE)
        for m in re.finditer(r'<form[^>]+action=["\']([^"\']+)["\']', html, re.IGNORECASE):
            action = m.group(1).lower()
            for jd in js_domains:
                if jd in action:
                    evidence_parts.append(f"FORM:{m.group(1)[:80]}")
                    strong_evidence = True

        # Zona 4: Links <a href="..."> apontando para domínio da gateway
        gateway_link_count = 0
        for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE):
            href = m.group(1).lower()
            for jd in js_domains:
                if jd in href:
                    gateway_link_count += 1
                    if gateway_link_count <= 2:
                        evidence_parts.append(f"LINK_GW:{m.group(1)[:80]}")

        # Zona 5: Texto inline (EVIDENCIA FRACA - só para gateways não-ambíguas)
        if not self.is_ambiguous:
            for sig in signatures:
                if sig in html_lower:
                    context_patterns = [
                        f'pagamento.*{re.escape(sig)}',
                        f'{re.escape(sig)}.*pagamento',
                        f'{re.escape(sig)}.*checkout',
                        f'gateway.*{re.escape(sig)}',
                        f'formas.?de.?pagamento.*{re.escape(sig)}',
                    ]
                    for cp in context_patterns:
                        if re.search(cp, html_lower):
                            evidence_parts.append(f"TEXT_CONTEXT:{sig}")
                            break

        # Para gateways AMBÍGUAS, exigir evidência forte
        if self.is_ambiguous:
            confirmed = strong_evidence
            if not confirmed:
                log.info(f"AMBIGUOUS GATEWAY | {self.gateway_key} | no strong evidence | {url[:80]}")
        else:
            confirmed = len(evidence_parts) > 0

        evidence = " | ".join(evidence_parts[:5]) if evidence_parts else ""
        return confirmed, evidence

    def _detect_platform(self, html_lower: str) -> str:
        for platform, keywords in self.ECOMMERCE_PLATFORMS.items():
            for kw in keywords:
                if kw in html_lower:
                    return platform
        return "Desconhecida"

    def _classify_niche(self, html_lower: str) -> str:
        scores = {}
        for niche, keywords in self.NICHE_KEYWORDS.items():
            score = 0
            for kw in keywords:
                count = html_lower.count(kw)
                if count > 0:
                    score += min(count, 5)
            if score > 0:
                scores[niche] = score

        if scores:
            best = max(scores, key=scores.get)
            log.debug(f"NICHE SCORES | top={best}({scores[best]})")
            return best

        return "Loja Geral / Variedades"

    def _extract_title(self, html: str) -> str:
        m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def _extract_meta(self, html: str, name: str) -> str:
        m = re.search(rf'<meta[^>]+name=["\']?{name}["\']?[^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not m:
            m = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']?{name}["\']?', html, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def _extract_emails(self, html: str) -> List[str]:
        emails = set()
        for m in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html):
            email = m.group(0).lower()
            if not any(x in email for x in ["@example", "@test", "@sentry", "@wixpress", ".png", ".jpg", ".gif", "@email.com"]):
                emails.add(email)
        return list(emails)

    def _extract_phones(self, html: str) -> List[str]:
        phones = set()
        for m in re.finditer(r'(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}', html):
            phone = re.sub(r'[^\d+]', '', m.group(0))
            if 10 <= len(phone) <= 13:
                phones.add(phone)
        return list(phones)


# ══════════════════════════════════════════════════════════════════
#                    REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════

class ReportGenerator:
    def __init__(self, gateway_key: str):
        self.gateway_key = gateway_key
        self.output_dir = OUTPUT_DIR if os.path.isdir(OUTPUT_DIR) else FALLBACK_OUTPUT
        os.makedirs(self.output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_all(self, results: List[Dict], scan_info: Dict) -> Dict[str, str]:
        files = {}
        files["TXT"] = self._generate_txt(results, scan_info)
        files["JSON"] = self._generate_json(results, scan_info)
        files["URLS"] = self._generate_urls(results)
        files["LOJAS"] = self._generate_lojas(results)

        for fmt, path in files.items():
            size = os.path.getsize(path) if os.path.isfile(path) else 0
            log.info(f"REPORT | {fmt} | {path} | {size:,} bytes")

        return files

    def _generate_txt(self, results: List[Dict], scan_info: Dict) -> str:
        path = os.path.join(self.output_dir, f"gatehunter_{self.gateway_key.lower()}_{self.timestamp}.txt")
        confirmed = [r for r in results if r.get("gateway_confirmed")]
        stores = [r for r in results if not r.get("gateway_confirmed")]

        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write(f"  GATEHUNTER v{VERSION} - RELATORIO DETALHADO\n")
            f.write(f"  Gateway: {self.gateway_key}\n")
            f.write(f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"  Nicho: {scan_info.get('niche', 'Todos')}\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"  URLs coletadas: {scan_info.get('total_urls', 0)}\n")
            f.write(f"  Sites analisados: {scan_info.get('analyzed', 0)}\n")
            f.write(f"  Gateway confirmada: {len(confirmed)}\n")
            f.write(f"  Lojas sem gateway: {len(stores)}\n")
            f.write(f"  Tempo total: {scan_info.get('elapsed', '0')}s\n\n")

            if confirmed:
                f.write("=" * 70 + "\n")
                f.write("  SITES COM GATEWAY CONFIRMADA\n")
                f.write("=" * 70 + "\n\n")
                for i, r in enumerate(confirmed, 1):
                    f.write(f"  [{i}] {r['url']}\n")
                    f.write(f"      Titulo: {r.get('title', 'N/A')[:80]}\n")
                    f.write(f"      Nicho: {r.get('niche', 'N/A')}\n")
                    f.write(f"      Plataforma: {r.get('platform', 'N/A')}\n")
                    f.write(f"      Score: {r.get('store_score', 0)}\n")
                    f.write(f"      Evidencia: {r.get('gateway_evidence', 'N/A')[:100]}\n")
                    if r.get("emails"):
                        f.write(f"      Emails: {', '.join(r['emails'])}\n")
                    if r.get("phones"):
                        f.write(f"      Telefones: {', '.join(r['phones'])}\n")
                    f.write(f"      Descricao: {r.get('description', 'N/A')[:120]}\n\n")

            if stores:
                f.write("=" * 70 + "\n")
                f.write("  LOJAS SEM GATEWAY CONFIRMADA (score alto)\n")
                f.write("=" * 70 + "\n\n")
                for i, r in enumerate(stores, 1):
                    f.write(f"  [{i}] {r['url']}\n")
                    f.write(f"      Titulo: {r.get('title', 'N/A')[:80]}\n")
                    f.write(f"      Nicho: {r.get('niche', 'N/A')}\n")
                    f.write(f"      Score: {r.get('store_score', 0)}\n\n")

            niches = {}
            for r in results:
                n = r.get("niche", "Outros")
                niches[n] = niches.get(n, 0) + 1
            if niches:
                f.write("=" * 70 + "\n")
                f.write("  CATEGORIAS ENCONTRADAS\n")
                f.write("=" * 70 + "\n\n")
                for n, c in sorted(niches.items(), key=lambda x: -x[1]):
                    bar = "█" * min(c * 2, 40)
                    f.write(f"  {n:35s} {c:3d} {bar}\n")
                f.write("\n")

        return path

    def _generate_json(self, results: List[Dict], scan_info: Dict) -> str:
        path = os.path.join(self.output_dir, f"gatehunter_{self.gateway_key.lower()}_{self.timestamp}.json")
        data = {
            "version": VERSION,
            "gateway": self.gateway_key,
            "niche": scan_info.get("niche", "Todos"),
            "timestamp": datetime.now().isoformat(),
            "scan_info": scan_info,
            "results": results,
            "total": len(results),
            "confirmed": len([r for r in results if r.get("gateway_confirmed")]),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def _generate_urls(self, results: List[Dict]) -> str:
        path = os.path.join(self.output_dir, f"gatehunter_{self.gateway_key.lower()}_{self.timestamp}_all_urls.txt")
        with open(path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(r["url"] + "\n")
        return path

    def _generate_lojas(self, results: List[Dict]) -> str:
        path = os.path.join(self.output_dir, f"gatehunter_{self.gateway_key.lower()}_{self.timestamp}_LOJAS.txt")
        confirmed = [r for r in results if r.get("gateway_confirmed")]
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# LOJAS COM GATEWAY {self.gateway_key.upper()} CONFIRMADA\n")
            f.write(f"# Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"# Total: {len(confirmed)} lojas\n\n")
            for r in confirmed:
                f.write(f"{r['url']} | {r.get('niche', 'N/A')} | {r.get('platform', 'N/A')} | Score: {r.get('store_score', 0)}\n")
        return path


# ══════════════════════════════════════════════════════════════════
#                    GATEHUNTER MAIN CLASS
# ══════════════════════════════════════════════════════════════════

class GateHunter:
    def __init__(self):
        log.start_session()
        log.info("GateHunter initialized")
        self.proxy = ProxyRotator()
        self.requester = SmartRequester(self.proxy)

    def _print_banner(self):
        os.system("clear 2>/dev/null || cls 2>/dev/null")
        banner = f"""
{R}╔══════════════════════════════════════════════════════════════╗{RST}
{R}║{RST}  {BOLD}{R}  ██████{Y}  █████  {C}████████{G} ███████{RST}                               {R}║{RST}
{R}║{RST}  {BOLD}{R} ██      {Y}██   ██    {C}██   {G} ██{RST}                                    {R}║{RST}
{R}║{RST}  {BOLD}{R} ██   ███{Y}███████    {C}██   {G} █████{RST}                                 {R}║{RST}
{R}║{RST}  {BOLD}{R} ██    ██{Y}██   ██    {C}██   {G} ██{RST}                                    {R}║{RST}
{R}║{RST}  {BOLD}{R}  ██████ {Y}██   ██    {C}██   {G} ███████{RST}                               {R}║{RST}
{R}║{RST}  {BOLD}{B} ██   ██{M}██    ██{C}███   ██{G}████████{Y}███████{R}██████{RST}              {R}║{RST}
{R}║{RST}  {BOLD}{B} ██   ██{M}██    ██{C}████  ██{G}   ██   {Y}██     {R}██   ██{RST}             {R}║{RST}
{R}║{RST}  {BOLD}{B} ███████{M}██    ██{C}██ ██ ██{G}   ██   {Y}█████  {R}██████{RST}              {R}║{RST}
{R}║{RST}  {BOLD}{B} ██   ██{M}██    ██{C}██  ████{G}   ██   {Y}██     {R}██   ██{RST}             {R}║{RST}
{R}║{RST}  {BOLD}{B} ██   ██{M} ██████ {C}██   ███{G}   ██   {Y}███████{R}██   ██{RST}             {R}║{RST}
{R}╚══════════════════════════════════════════════════════════════╝{RST}

  {D}v{VERSION} // NETHUNTER SUPREME EDITION // Payment Gateway OSINT{RST}

  {M}┌──────────────────────────────────────────────────────────┐{RST}
  {M}│{RST} {W}Engine  : Brave + DDG + Bing (Rotacao) + Google CSE{RST}      {M}│{RST}
  {M}│{RST} {W}Evasion : curl_cffi Impersonate + Proxy Pool + UA Spoof{RST} {M}│{RST}
  {M}│{RST} {W}Filter  : 4-Layer Validation + Ambiguous Gateway Check{RST}  {M}│{RST}
  {M}│{RST} {W}Output  : {OUTPUT_DIR}{RST}                     {M}│{RST}
  {M}└──────────────────────────────────────────────────────────┘{RST}
"""
        print(banner)

        print(f"  {D}┌{'─'*40}┐{RST}")
        print(f"  {D}│{RST} {W}CONFIGURACAO ATIVA{RST}{' '*22}{D}│{RST}")
        print(f"  {D}├{'─'*40}┤{RST}")
        print(f"  {D}│{RST} {C}Proxies{RST}    : {G}{len(self.proxy.proxies)}{RST}{' '*(27-len(str(len(self.proxy.proxies))))}{D}│{RST}")
        print(f"  {D}│{RST} {C}Threads{RST}    : {G}{MAX_THREADS}{RST}{' '*(27-len(str(MAX_THREADS)))}{D}│{RST}")
        print(f"  {D}│{RST} {C}Timeout{RST}    : {G}{REQUEST_TIMEOUT}s{RST}{' '*(26-len(str(REQUEST_TIMEOUT)))}{D}│{RST}")
        cffi_str = f"{G}OK{RST}" if CFFI_OK else f"{R}NO{RST}"
        print(f"  {D}│{RST} {C}curl_cffi{RST}  : {cffi_str}{' '*(27-2)}{D}│{RST}")
        engines = "Brave + DDG + Bing (Rotacao)"
        if GOOGLE_CSE_API_KEY:
            engines += " + CSE"
        print(f"  {D}│{RST} {C}Engines{RST}    : {G}{engines}{RST}{' '*max(0,27-len(engines))}{D}│{RST}")
        print(f"  {D}│{RST} {C}Debug Log{RST}  : {Y}Ativo{RST}{' '*(22)}{D}│{RST}")
        print(f"  {D}└{'─'*40}┘{RST}")
        print()

    def _show_gateway_menu(self) -> Optional[str]:
        print(f"  {M}┌{'─'*55}┐{RST}")
        print(f"  {M}│{RST} {BOLD}{W}SELECIONE A GATEWAY DE PAGAMENTO{RST}{' '*22}{M}│{RST}")
        print(f"  {M}├{'─'*55}┤{RST}")

        keys = list(GATEWAYS.keys())
        for i, key in enumerate(keys, 1):
            gw = GATEWAYS[key]
            name = f"{key:15s}"
            desc = gw["desc"][:38]
            ambig = f" {Y}*{RST}" if key in AMBIGUOUS_GATEWAYS else "  "
            print(f"  {M}│{RST} [{G}{i:2d}{RST}] {C}{name}{RST}{ambig}{desc}{' '*max(0,36-len(desc))}{M}│{RST}")

        print(f"  {M}├{'─'*55}┤{RST}")
        print(f"  {M}│{RST} [{Y} 0{RST}] {Y}CUSTOM{RST} - Inserir gateway personalizada{' '*13}{M}│{RST}")
        print(f"  {M}│{RST} [{R}99{RST}] {R}SAIR{RST}{' '*49}{M}│{RST}")
        print(f"  {M}└{'─'*55}┘{RST}")
        print(f"  {D}* = Gateway ambigua (validacao extra){RST}")
        print()

        choice = input(f"  {G}GateHunter{RST} > ").strip()

        if choice == "99":
            return None
        elif choice == "0":
            custom = input(f"  {Y}Nome da gateway:{RST} ").strip()
            if custom:
                sigs = input(f"  {Y}Assinaturas (separadas por virgula):{RST} ").strip()
                dorks_input = input(f"  {Y}Dorks (separadas por ;):{RST} ").strip()
                GATEWAYS[custom] = {
                    "desc": f"{custom} - Gateway personalizada",
                    "signatures": [s.strip() for s in sigs.split(",")],
                    "js_domains": [s.strip() for s in sigs.split(",")],
                    "dorks": [d.strip() for d in dorks_input.split(";")] if dorks_input else [f'"{custom}" loja comprar', f'"{custom}" pagamento loja online'],
                }
                return custom
            return None
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(keys):
                    return keys[idx]
            except ValueError:
                pass
            print(f"  {R}[!] Opcao invalida{RST}")
            return None

    def _show_niche_menu(self) -> Tuple[str, List[str]]:
        print()
        print(f"  {M}┌{'─'*55}┐{RST}")
        print(f"  {M}│{RST} {BOLD}{W}FILTRAR POR NICHO (opcional){RST}{' '*27}{M}│{RST}")
        print(f"  {M}├{'─'*55}┤{RST}")

        niche_keys = list(NICHOS.keys())
        for i, key in enumerate(niche_keys):
            niche = NICHOS[key]
            name = f"{key:30s}"
            desc = niche["desc"][:22]
            print(f"  {M}│{RST} [{G}{i:2d}{RST}] {C}{name}{RST} {desc}{' '*max(0,22-len(desc))}{M}│{RST}")

        print(f"  {M}└{'─'*55}┘{RST}")
        print()

        choice = input(f"  {G}Nicho{RST} > ").strip()

        try:
            idx = int(choice)
            if 0 <= idx < len(niche_keys):
                key = niche_keys[idx]
                return key, NICHOS[key]["terms"]
        except ValueError:
            pass

        return "Todos", []

    def _execute_scan(self, gateway_key: str, niche_name: str, niche_terms: List[str]):
        gateway = GATEWAYS[gateway_key]
        start_time = time.time()

        print()
        print(f"  {M}{'='*60}{RST}")
        print(f"  {BOLD}{C}INICIANDO SCAN: {gateway_key}{RST}")
        if niche_name != "Todos":
            print(f"  {BOLD}{Y}NICHO: {niche_name}{RST}")
        if gateway_key in AMBIGUOUS_GATEWAYS:
            print(f"  {BOLD}{Y}MODO: Validacao rigorosa (gateway ambigua){RST}")
        print(f"  {M}{'='*60}{RST}")
        print()

        log.info(f"SCAN START | gateway={gateway_key} | niche={niche_name} | dorks={len(gateway['dorks'])} | ambiguous={gateway_key in AMBIGUOUS_GATEWAYS}")

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  {D}{ts}{RST} [{C}*{RST}] Gateway: {G}{gateway_key}{RST}")
        print(f"  {D}{ts}{RST} [{C}*{RST}] Dorks base: {G}{len(gateway['dorks'])}{RST}")
        print(f"  {D}{ts}{RST} [{C}*{RST}] Nicho: {Y}{niche_name}{RST}")
        print(f"  {D}{ts}{RST} [{C}*{RST}] Assinaturas: {Y}{', '.join(gateway['signatures'])}{RST}")
        print(f"  {D}{ts}{RST} [{C}*{RST}] Proxies: {G}{len(self.proxy.proxies)}{RST}")
        print(f"  {D}{ts}{RST} [{C}*{RST}] Threads: {G}{MAX_THREADS}{RST}")
        print()

        # ── FASE 1: Coletar URLs ──
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  {D}{ts}{RST} [{C}-{RST}] {BOLD}FASE 1/3: Coletando URLs via Dorks (Engine Rotation)...{RST}")
        log.info("PHASE 1 START | Collecting URLs")

        dork_engine = DorkEngine(self.requester)
        valid_urls = dork_engine.collect_urls(gateway["dorks"], niche_terms)

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n  {D}{ts}{RST} [{G}+{RST}] Total URLs unicas: {G}{len(valid_urls)}{RST}")
        log.info(f"PHASE 1 DONE | valid_urls={len(valid_urls)}")

        if not valid_urls:
            print(f"\n  {R}[!] Nenhuma URL encontrada. Tente outra gateway ou nicho.{RST}")
            log.warning("NO URLS FOUND")
            return

        # ── FASE 2: Analisar Sites ──
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n  {D}{ts}{RST} [{C}-{RST}] {BOLD}FASE 2/3: Analisando {len(valid_urls)} sites ({MAX_THREADS} threads)...{RST}")
        log.info(f"PHASE 2 START | Analyzing {len(valid_urls)} sites")

        analyzer = SiteAnalyzer(self.requester, gateway_key)
        results = []
        errors = 0

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_map = {executor.submit(analyzer.analyze, url): url for url in valid_urls}
            for i, future in enumerate(as_completed(future_map), 1):
                url = future_map[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        status = f"{G}CONFIRMED{RST}" if result.get("gateway_confirmed") else f"{Y}STORE{RST}"
                        niche_str = result.get("niche", "N/A")[:30]
                        ts = datetime.now().strftime("%H:%M:%S")
                        print(f"  {D}{ts}{RST} [{i}/{len(valid_urls)}] {status} {C}{result['domain'][:40]}{RST} | {niche_str}")
                    else:
                        ts = datetime.now().strftime("%H:%M:%S")
                        domain = urllib.parse.urlparse(url).netloc[:40]
                        print(f"  {D}{ts}{RST} [{i}/{len(valid_urls)}] {R}REJECTED{RST} {D}{domain}{RST}")
                except Exception as e:
                    errors += 1
                    log.error(f"THREAD ERROR | {url[:80]} | {str(e)[:80]}")

        log.info(f"PHASE 2 DONE | results={len(results)} | errors={errors}")

        # ── FASE 3: Gerar Relatórios ──
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n  {D}{ts}{RST} [{C}-{RST}] {BOLD}FASE 3/3: Gerando relatorios...{RST}")
        log.info("PHASE 3 START | Generating reports")

        elapsed = round(time.time() - start_time, 1)
        scan_info = {
            "gateway": gateway_key,
            "niche": niche_name,
            "total_urls": len(valid_urls),
            "analyzed": len(valid_urls),
            "confirmed": len([r for r in results if r.get("gateway_confirmed")]),
            "stores_only": len([r for r in results if not r.get("gateway_confirmed")]),
            "errors": errors,
            "elapsed": elapsed,
            "requests_total": self.requester.stats["requests"],
            "blocked": self.requester.stats["blocked"],
        }

        report = ReportGenerator(gateway_key)
        files = report.generate_all(results, scan_info)

        # ── RESUMO FINAL ──
        confirmed = [r for r in results if r.get("gateway_confirmed")]
        stores = [r for r in results if not r.get("gateway_confirmed")]

        print()
        print(f"  {M}{'='*60}{RST}")
        print(f"  {BOLD}{G}SCAN COMPLETO!{RST}")
        print(f"  {M}{'='*60}{RST}")
        print()
        print(f"  {W}Gateway{RST}          : {C}{gateway_key}{RST}")
        print(f"  {W}Nicho{RST}            : {Y}{niche_name}{RST}")
        print(f"  {W}Tempo total{RST}      : {C}{elapsed}s{RST}")
        print(f"  {W}URLs coletadas{RST}   : {C}{len(valid_urls)}{RST}")
        print(f"  {W}Confirmadas{RST}      : {G}{len(confirmed)}{RST}")
        print(f"  {W}Lojas (score){RST}    : {Y}{len(stores)}{RST}")
        print(f"  {W}Errors{RST}           : {R}{errors}{RST}")
        print(f"  {W}Requests total{RST}   : {C}{self.requester.stats['requests']}{RST}")
        print(f"  {W}Bloqueios{RST}        : {R}{self.requester.stats['blocked']}{RST}")
        print()

        print(f"  {W}Arquivos gerados:{RST}")
        for fmt, path in files.items():
            size = os.path.getsize(path) if os.path.isfile(path) else 0
            print(f"  [{C}-{RST}] {fmt:10s} = {Y}{path}{RST} ({size:,} bytes)")
        print()

        if confirmed:
            print(f"  {G}TOP SITES CONFIRMADOS:{RST}")
            print(f"  {'─'*55}")
            for i, r in enumerate(confirmed[:15], 1):
                niche_str = r.get("niche", "N/A")[:25]
                print(f"  {i:2d}. {C}{r['domain'][:35]}{RST} | {niche_str}")
            print()

        niches = {}
        for r in results:
            n = r.get("niche", "Outros")
            niches[n] = niches.get(n, 0) + 1
        if niches:
            print(f"  {Y}CATEGORIAS:{RST}")
            for n, c in sorted(niches.items(), key=lambda x: -x[1]):
                bar = f"{G}{'█' * min(c * 2, 30)}{RST}"
                print(f"  {n:35s} {c:3d} {bar}")
            print()

        log.info(f"SCAN COMPLETE | gateway={gateway_key} | confirmed={len(confirmed)} | stores={len(stores)} | elapsed={elapsed}s")

    def run(self):
        while True:
            self._print_banner()
            gateway_key = self._show_gateway_menu()

            if gateway_key is None:
                print(f"\n  {Y}Ate a proxima! GateHunter v{VERSION}{RST}\n")
                break

            niche_name, niche_terms = self._show_niche_menu()
            self._execute_scan(gateway_key, niche_name, niche_terms)

            print(f"  {M}{'='*60}{RST}")
            input(f"  {D}Pressione Enter para voltar ao menu...{RST} ")


# ══════════════════════════════════════════════════════════════════
#                         MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        hunter = GateHunter()
        hunter.run()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}[!] Interrompido pelo usuario.{RST}\n")
    except Exception as e:
        print(f"\n  {R}[FATAL] {e}{RST}")
        log.error(f"FATAL | {traceback.format_exc()}")
