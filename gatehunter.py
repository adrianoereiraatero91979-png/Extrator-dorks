#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║              GATEHUNTER v5.0 - NETHUNTER SUPREME EDITION         ║
║         Advanced Payment Gateway OSINT & Store Finder            ║
║                   Kali NetHunter Optimized                       ║
╚══════════════════════════════════════════════════════════════════╝

v5.0 - Multi-engine (DDG HTML + Google.com.br + Bing + Google CSE API)
       Dorks simples e abrangentes + Busca SEM proxy + Validação 3 camadas
       Debug logs completo em /sdcard/nh_files/logs_gate_hunter.txt
Uso educacional e autorizado apenas.
"""

import os, sys, re, json, time, random, signal, threading
import urllib.parse, urllib.request, ssl, logging, traceback
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Tuple, Any, Set
import warnings
warnings.filterwarnings("ignore")

try:
    from curl_cffi import requests as cffi_requests
    CFFI_OK = True
except ImportError:
    CFFI_OK = False

try:
    from fake_useragent import UserAgent
    UA_GEN = UserAgent(browsers=["chrome", "edge"], os=["windows", "macos"])
except Exception:
    UA_GEN = None

# ── Cores ANSI ────────────────────────────────────────────────
R = "\033[1;31m"; G = "\033[1;32m"; Y = "\033[1;33m"; B = "\033[1;34m"
M = "\033[1;35m"; C = "\033[1;36m"; W = "\033[1;37m"; D = "\033[0;37m"
BOLD = "\033[1m"; RST = "\033[0m"

# ══════════════════════════════════════════════════════════════════
#                     CONSTANTES & CONFIG
# ══════════════════════════════════════════════════════════════════

VERSION = "5.0.0"
OUTPUT_DIR = "/sdcard/nh_files"
FALLBACK_OUTPUT = os.path.expanduser("~/gatehunter_output")
LOG_PATH = os.path.join(OUTPUT_DIR, "logs_gate_hunter.txt")
LOG_PATH_FALLBACK = os.path.join(FALLBACK_OUTPUT, "logs_gate_hunter.txt")
PROXIES_PATH_DEFAULT = os.path.join(OUTPUT_DIR, "proxies.txt")
PROXIES_PATH_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")

# Google CSE API (opcional - usuário pode configurar)
GOOGLE_CSE_API_KEY = os.environ.get("GOOGLE_CSE_API_KEY", "")
GOOGLE_CSE_CX = os.environ.get("GOOGLE_CSE_CX", "")

MAX_THREADS = 12
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
SEARCH_DELAY_MIN = 3.0
SEARCH_DELAY_MAX = 6.0
STORE_SCORE_THRESHOLD = 6

IMPERSONATE_TARGETS = [
    "chrome120", "chrome119", "chrome116", "chrome110",
    "edge101", "safari15_5", "safari17_0",
]

PREMIUM_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

# ══════════════════════════════════════════════════════════════════
#                 BLACKLIST MASSIVA DE DOMÍNIOS
# ══════════════════════════════════════════════════════════════════

DOMAIN_BLACKLIST = {
    # Redes sociais / mídia
    "youtube.com", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "tiktok.com", "pinterest.com", "reddit.com", "quora.com",
    "medium.com", "tumblr.com", "whatsapp.com", "telegram.org", "discord.com",
    # Buscadores
    "google.com", "google.com.br", "bing.com", "yahoo.com", "duckduckgo.com",
    "baidu.com", "yandex.com", "startpage.com",
    # Dev / Code
    "github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com",
    "stackexchange.com", "npmjs.com", "pypi.org", "packagist.org",
    "codepen.io", "jsfiddle.net", "replit.com", "dev.to", "hashnode.com",
    # Docs / Wiki
    "wikipedia.org", "wikimedia.org", "w3schools.com", "mdn.mozilla.org",
    "docs.python.org", "readthedocs.io", "readme.io", "gitbook.io",
    # Reclamação / Review
    "reclameaqui.com.br", "trustpilot.com", "glassdoor.com", "indeed.com",
    "consumidor.gov.br", "procon.sp.gov.br",
    # Notícias / Mídia
    "globo.com", "uol.com.br", "folha.uol.com.br", "estadao.com.br",
    "terra.com.br", "ig.com.br", "r7.com", "bbc.com", "cnn.com",
    "forbes.com", "bloomberg.com", "reuters.com", "techcrunch.com",
    # Governo
    "gov.br", "gov.com", "senado.leg.br", "camara.leg.br",
    # Educação
    "edu.br", "coursera.org", "udemy.com", "edx.org",
    # Plataformas de e-commerce (são plataformas, não lojas)
    "nuvemshop.com.br", "tray.com.br", "loja-integrada.com.br",
    "lojaintegrada.com.br", "vtex.com", "shopify.com",
    "wix.com", "wordpress.com", "wordpress.org", "squarespace.com",
    # Gateways (o próprio site da gateway)
    "asaas.com", "pagar.me", "pagarme.com.br", "stone.com.br",
    "cielo.com.br", "userede.com.br", "rede.com.br",
    "mercadopago.com.br", "mercadolivre.com.br",
    "paypal.com", "stripe.com", "pagseguro.uol.com.br", "pagseguro.com.br",
    "getnet.com.br", "iugu.com", "vindi.com.br", "vindi-dev.com",
    "hotmart.com", "eduzz.com", "kiwify.com.br", "appmax.com.br",
    "payflow.com", "checkout.com",
    # Ferramentas / SaaS
    "hubspot.com", "salesforce.com", "zendesk.com", "intercom.com",
    "mailchimp.com", "sendgrid.com", "twilio.com", "cloudflare.com",
    "aws.amazon.com", "azure.microsoft.com", "cloud.google.com",
    "heroku.com", "vercel.com", "netlify.com", "digitalocean.com",
    # Comparadores / Afiliados
    "b2bstack.com.br", "capterra.com.br", "g2.com", "trustradius.com",
    "comparaja.com.br", "buscape.com.br", "zoom.com.br",
    # Outros
    "play.google.com", "apps.apple.com", "chrome.google.com",
    "archive.org", "web.archive.org", "slideshare.net",
    "scribd.com", "issuu.com", "academia.edu",
    "pluga.co", "zapier.com", "ifttt.com", "n8n.io",
    "nfe.io", "jivochat.com.br", "rdstation.com",
    "v4company.com", "resultadosdigitais.com.br", "rockcontent.com",
    "sebrae.com.br", "endeavor.org.br",
    "fintech.global", "crunchbase.com", "pitchbook.com",
    "investidores.com.br", "infomoney.com.br",
}

INFORMATIONAL_SUBDOMAINS = {
    "docs.", "doc.", "blog.", "help.", "support.", "suporte.",
    "api.", "developer.", "developers.", "dev.", "status.",
    "community.", "forum.", "faq.", "kb.", "wiki.",
    "learn.", "academy.", "training.", "tutorial.",
    "atendimento.", "central.", "materiais.", "conteudo.",
    "portal.", "admin.", "dashboard.", "app.", "cdn.",
    "mail.", "email.", "smtp.", "ftp.", "git.",
}

BAD_PATH_PATTERNS = {
    "/blog", "/docs", "/doc/", "/help", "/support", "/suporte",
    "/api/", "/developer", "/tutorial", "/academy",
    "/about", "/sobre", "/pricing", "/precos", "/contato",
    "/terms", "/privacy", "/legal", "/changelog",
    "/careers", "/vagas", "/trabalhe-conosco",
    "/press", "/imprensa", "/newsroom",
    "/partner", "/parceiro", "/afiliado",
    "/case", "/cases", "/depoimento",
}

# ══════════════════════════════════════════════════════════════════
#              GATEWAYS - DORKS SIMPLES E ABRANGENTES
# ══════════════════════════════════════════════════════════════════
# REGRA: dorks simples, sem múltiplos intext:, focadas em contexto de loja

GATEWAYS = {
    "Asaas": {
        "desc": "Asaas - Plataforma de cobranças e pagamentos",
        "signatures": ["asaas.com", "js.asaas.com", "checkout.asaas.com", "api.asaas.com"],
        "dorks": [
            '"asaas" comprar produto loja -site:asaas.com',
            '"asaas" carrinho pagamento -site:asaas.com -site:github.com',
            '"asaas" ecommerce loja virtual -site:asaas.com -blog',
            '"checkout.asaas" loja -site:asaas.com',
            '"asaas" "adicionar ao carrinho" -site:asaas.com',
            '"asaas" "finalizar compra" -site:asaas.com',
            '"pagamento" "asaas" loja online site:com.br -site:asaas.com',
            '"asaas" woocommerce loja -site:github.com -site:wordpress.org',
        ],
    },
    "PagarMe": {
        "desc": "Pagar.me (Stone) - Gateway de pagamentos",
        "signatures": ["pagar.me", "api.pagar.me", "js.pagar.me", "pagarme"],
        "dorks": [
            '"pagar.me" comprar loja online -site:pagar.me -site:stone.com.br',
            '"pagarme" carrinho pagamento -site:pagar.me -site:github.com',
            '"pagar.me" ecommerce produto -site:pagar.me -blog',
            '"pagar.me" "finalizar compra" -site:pagar.me',
            '"pagar.me" "adicionar ao carrinho" -site:pagar.me',
            '"pagarme" checkout loja virtual -site:pagar.me -site:stone.com.br',
            '"pagar.me" woocommerce loja -site:github.com',
            '"pagar.me" nuvemshop loja -site:pagar.me',
        ],
    },
    "Erede": {
        "desc": "eRede (Itaú) - Adquirente e gateway",
        "signatures": ["userede.com.br", "e.rede.com.br", "erede"],
        "dorks": [
            '"erede" comprar loja online -site:userede.com.br -site:rede.com.br',
            '"userede" pagamento ecommerce -site:userede.com.br',
            '"e-rede" checkout loja -site:rede.com.br',
            '"erede" "finalizar compra" -site:userede.com.br',
            '"erede" woocommerce loja -site:github.com',
            '"erede" loja virtual produto -site:rede.com.br -blog',
        ],
    },
    "PayFlow": {
        "desc": "PayFlow - Gateway de pagamentos digital",
        "signatures": ["payflow.com.br", "payflow", "api.payflow"],
        "dorks": [
            '"payflow" comprar loja online pagamento',
            '"payflow" checkout ecommerce produto',
            '"payflow" "finalizar compra" loja',
            '"payflow" carrinho pagamento loja virtual',
        ],
    },
    "AppMax": {
        "desc": "AppMax - Plataforma de vendas e pagamentos",
        "signatures": ["appmax.com.br", "api.appmax", "appmax"],
        "dorks": [
            '"appmax" comprar loja online -site:appmax.com.br',
            '"appmax" checkout pagamento -site:appmax.com.br',
            '"appmax" ecommerce produto -site:appmax.com.br -blog',
            '"appmax" "finalizar compra" -site:appmax.com.br',
            '"appmax" loja virtual carrinho -site:appmax.com.br',
        ],
    },
    "MercadoPago": {
        "desc": "Mercado Pago - Gateway e carteira digital",
        "signatures": ["mercadopago.com", "api.mercadopago.com", "sdk.mercadopago"],
        "dorks": [
            '"mercado pago" comprar loja online -site:mercadolivre.com.br -site:mercadopago.com.br',
            '"mercadopago" checkout loja -site:mercadolivre.com.br',
            '"mercado pago" ecommerce produto -site:mercadopago.com.br -blog',
            '"mercado pago" "finalizar compra" loja -site:mercadolivre.com.br',
            '"mercado pago" carrinho loja virtual -site:mercadopago.com.br',
            '"mercadopago" woocommerce loja -site:github.com',
        ],
    },
    "PagSeguro": {
        "desc": "PagSeguro/PagBank - Gateway de pagamentos",
        "signatures": ["pagseguro.uol.com.br", "api.pagseguro", "stc.pagseguro"],
        "dorks": [
            '"pagseguro" comprar loja online -site:pagseguro.uol.com.br',
            '"pagseguro" checkout ecommerce -site:pagseguro.com.br -blog',
            '"pagseguro" "finalizar compra" loja -site:pagseguro.uol.com.br',
            '"pagseguro" carrinho produto -site:pagseguro.com.br',
            '"pagbank" loja online comprar -site:pagseguro.uol.com.br',
            '"pagseguro" woocommerce loja -site:github.com',
        ],
    },
    "Cielo": {
        "desc": "Cielo - Maior adquirente do Brasil",
        "signatures": ["cielo.com.br", "api.cielo", "api2.cielo", "cieloecommerce"],
        "dorks": [
            '"cielo" comprar loja online -site:cielo.com.br',
            '"cielo" checkout ecommerce produto -site:cielo.com.br -blog',
            '"cielo" "finalizar compra" loja -site:cielo.com.br',
            '"cieloecommerce" loja -site:cielo.com.br',
            '"cielo" carrinho pagamento loja virtual -site:cielo.com.br',
            '"cielo" woocommerce loja -site:github.com',
        ],
    },
    "Stripe": {
        "desc": "Stripe - Gateway global de pagamentos",
        "signatures": ["stripe.com", "js.stripe.com", "api.stripe.com", "checkout.stripe"],
        "dorks": [
            '"stripe" comprar loja online brasil -site:stripe.com',
            '"stripe" checkout ecommerce -site:stripe.com -site:github.com',
            '"stripe" "finalizar compra" loja -site:stripe.com',
            '"js.stripe.com" loja -site:stripe.com -site:github.com',
            '"stripe" carrinho produto loja -site:stripe.com -blog',
        ],
    },
    "Hotmart": {
        "desc": "Hotmart - Plataforma de produtos digitais",
        "signatures": ["hotmart.com", "pay.hotmart.com", "api.hotmart"],
        "dorks": [
            '"hotmart" comprar curso online -site:hotmart.com',
            '"hotmart" checkout pagamento -site:hotmart.com -blog',
            '"pay.hotmart" produto -site:hotmart.com',
            '"hotmart" "comprar agora" -site:hotmart.com',
            '"hotmart" plataforma venda -site:hotmart.com -site:github.com',
        ],
    },
    "Eduzz": {
        "desc": "Eduzz - Plataforma de infoprodutos",
        "signatures": ["eduzz.com", "api.eduzz.com", "checkout.eduzz"],
        "dorks": [
            '"eduzz" comprar curso -site:eduzz.com',
            '"eduzz" checkout pagamento -site:eduzz.com -blog',
            '"eduzz" "comprar agora" produto -site:eduzz.com',
            '"eduzz" plataforma venda online -site:eduzz.com',
        ],
    },
    "Kiwify": {
        "desc": "Kiwify - Plataforma de vendas digitais",
        "signatures": ["kiwify.com.br", "pay.kiwify", "api.kiwify"],
        "dorks": [
            '"kiwify" comprar curso -site:kiwify.com.br',
            '"kiwify" checkout pagamento -site:kiwify.com.br',
            '"kiwify" "comprar agora" -site:kiwify.com.br',
            '"kiwify" produto digital venda -site:kiwify.com.br -blog',
        ],
    },
    "Vindi": {
        "desc": "Vindi - Plataforma de pagamentos recorrentes",
        "signatures": ["vindi.com.br", "api.vindi.com.br", "app.vindi"],
        "dorks": [
            '"vindi" pagamento recorrente loja -site:vindi.com.br',
            '"vindi" assinatura plano -site:vindi.com.br -blog',
            '"vindi" checkout pagamento -site:vindi.com.br',
            '"vindi" cobranca recorrente -site:vindi.com.br -site:github.com',
            '"vindi" plataforma pagamento -site:vindi.com.br -tutorial',
        ],
    },
    "Iugu": {
        "desc": "Iugu - Gateway e plataforma financeira",
        "signatures": ["iugu.com", "api.iugu.com", "js.iugu.com"],
        "dorks": [
            '"iugu" comprar loja online -site:iugu.com',
            '"iugu" checkout pagamento -site:iugu.com -blog',
            '"iugu" ecommerce produto -site:iugu.com',
            '"iugu" "finalizar compra" -site:iugu.com',
            '"js.iugu.com" loja -site:iugu.com -site:github.com',
        ],
    },
    "Getnet": {
        "desc": "Getnet (Santander) - Adquirente e gateway",
        "signatures": ["getnet.com.br", "api.getnet", "checkout.getnet"],
        "dorks": [
            '"getnet" comprar loja online -site:getnet.com.br',
            '"getnet" checkout ecommerce -site:getnet.com.br -blog',
            '"getnet" pagamento loja virtual -site:getnet.com.br',
            '"getnet" "finalizar compra" -site:getnet.com.br',
            '"getnet" woocommerce loja -site:github.com',
        ],
    },
}

# ══════════════════════════════════════════════════════════════════
#                      DEBUG LOGGER
# ══════════════════════════════════════════════════════════════════

class DebugLogger:
    def __init__(self):
        self.log_path = None
        self.logger = logging.getLogger("GateHunter")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(threadName)-12s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        for path in [LOG_PATH, LOG_PATH_FALLBACK]:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                file_handler = logging.FileHandler(path, mode="a", encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                self.log_path = path
                break
            except Exception:
                continue

    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)

    def start_session(self):
        self.info("=" * 80)
        self.info(f"GATEHUNTER v{VERSION} - DEBUG LOG INICIADO")
        self.info(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Log path: {self.log_path}")
        self.info(f"Python: {sys.version}")
        self.info(f"Platform: {sys.platform}")
        self.info(f"curl_cffi: {CFFI_OK}")
        self.info(f"Google CSE API: {'Configurada' if GOOGLE_CSE_API_KEY else 'Nao configurada'}")
        self.info("=" * 80)

log = DebugLogger()

# ══════════════════════════════════════════════════════════════════
#                    PROXY ROTATOR
# ══════════════════════════════════════════════════════════════════

class ProxyRotator:
    def __init__(self):
        self.proxies = []
        self.lock = threading.Lock()
        self.index = 0
        self.failures = {}
        self._load()

    def _load(self):
        for path in [PROXIES_PATH_DEFAULT, PROXIES_PATH_FALLBACK]:
            if os.path.isfile(path):
                log.info(f"Loading proxies from: {path}")
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split(":")
                        if len(parts) >= 4:
                            ip, port, user, pwd = parts[0], parts[1], parts[2], ":".join(parts[3:])
                            proxy = {"ip": ip, "port": port, "user": user, "pass": pwd}
                            self.proxies.append(proxy)
                            log.debug(f"PROXY LOADED | ip={ip} | port={port}")
                        elif len(parts) == 2:
                            self.proxies.append({"ip": parts[0], "port": parts[1], "user": "", "pass": ""})
                            log.debug(f"PROXY LOADED | ip={parts[0]} | port={parts[1]}")
                log.info(f"Total proxies loaded: {len(self.proxies)}")
                return
        log.warning("No proxy file found")

    def get(self) -> Optional[Dict]:
        if not self.proxies:
            return None
        with self.lock:
            proxy = self.proxies[self.index % len(self.proxies)]
            self.index += 1
            log.debug(f"PROXY SELECTED | ip={proxy['ip']}")
            return proxy

    def get_url(self, proxy: Dict) -> str:
        if proxy["user"]:
            return f"http://{proxy['user']}:{proxy['pass']}@{proxy['ip']}:{proxy['port']}"
        return f"http://{proxy['ip']}:{proxy['port']}"

    def mark_fail(self, proxy: Dict):
        key = proxy["ip"]
        self.failures[key] = self.failures.get(key, 0) + 1
        log.debug(f"PROXY FAIL | ip={key} | failures={self.failures[key]}")

# ══════════════════════════════════════════════════════════════════
#                  FINGERPRINT GENERATOR
# ══════════════════════════════════════════════════════════════════

class FingerprintGenerator:
    PLATFORMS = [
        {"ua_platform": '"Windows"', "sec_ch_ua_mobile": "?0", "platform": "Windows"},
        {"ua_platform": '"macOS"', "sec_ch_ua_mobile": "?0", "platform": "macOS"},
        {"ua_platform": '"Linux"', "sec_ch_ua_mobile": "?0", "platform": "Linux"},
    ]

    def generate(self) -> Dict[str, str]:
        plat = random.choice(self.PLATFORMS)
        if UA_GEN:
            try: ua = UA_GEN.random
            except: ua = random.choice(PREMIUM_USER_AGENTS)
        else:
            ua = random.choice(PREMIUM_USER_AGENTS)
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua-Platform": plat["ua_platform"],
            "Sec-Ch-Ua-Mobile": plat["sec_ch_ua_mobile"],
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
        }
        log.debug(f"FINGERPRINT | UA={ua[:80]} | Platform={plat['ua_platform']}")
        return headers

fingerprint = FingerprintGenerator()

# ══════════════════════════════════════════════════════════════════
#                    SMART REQUESTER
# ══════════════════════════════════════════════════════════════════

class SmartRequester:
    """HTTP requester com curl_cffi impersonate + fallback urllib"""

    def __init__(self, proxy_rotator: ProxyRotator):
        self.proxy = proxy_rotator
        self.stats = {"requests": 0, "success": 0, "failed": 0, "blocked": 0}
        self.lock = threading.Lock()

    def get(self, url: str, use_proxy: bool = True, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
        """Faz GET request. use_proxy=False para buscas (IP direto é melhor)"""
        with self.lock:
            self.stats["requests"] += 1

        headers = fingerprint.generate()
        proxy_info = None
        proxy_url = None

        if use_proxy:
            proxy_info = self.proxy.get()
            if proxy_info:
                proxy_url = self.proxy.get_url(proxy_info)

        # Tentar com curl_cffi primeiro
        if CFFI_OK:
            imp = random.choice(IMPERSONATE_TARGETS)
            try:
                t0 = time.time()
                kwargs = {"impersonate": imp, "timeout": timeout, "headers": headers, "allow_redirects": True}
                if proxy_url:
                    kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
                r = cffi_requests.get(url, **kwargs)
                elapsed = time.time() - t0
                log.debug(f"HTTP GET | status={r.status_code} | proxy={'direct' if not proxy_info else proxy_info['ip']} | imp={imp} | time={elapsed:.2f}s | url={url[:120]}")

                if r.status_code == 429:
                    with self.lock:
                        self.stats["blocked"] += 1
                    if proxy_info:
                        self.proxy.mark_fail(proxy_info)
                    return None
                if r.status_code == 200:
                    with self.lock:
                        self.stats["success"] += 1
                    return r.text
                return r.text if r.status_code < 400 else None
            except Exception as e:
                log.debug(f"HTTP ERROR | curl_cffi | {type(e).__name__}: {str(e)[:100]} | url={url[:100]}")
                if proxy_info:
                    self.proxy.mark_fail(proxy_info)

        # Fallback: urllib
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers=headers)
            if proxy_url:
                handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                opener = urllib.request.build_opener(handler)
            else:
                opener = urllib.request.build_opener()
            t0 = time.time()
            resp = opener.open(req, timeout=timeout)
            html = resp.read().decode("utf-8", errors="ignore")
            elapsed = time.time() - t0
            log.debug(f"HTTP GET | status={resp.status} | urllib | time={elapsed:.2f}s | url={url[:120]}")
            with self.lock:
                self.stats["success"] += 1
            return html
        except Exception as e:
            log.debug(f"HTTP ERROR | urllib | {type(e).__name__}: {str(e)[:100]} | url={url[:100]}")
            with self.lock:
                self.stats["failed"] += 1
            return None

# ══════════════════════════════════════════════════════════════════
#                    DORK ENGINE v5
# ══════════════════════════════════════════════════════════════════

class DorkEngine:
    """Multi-engine: DDG HTML + Google.com.br + Bing + Google CSE API"""

    def __init__(self, requester: SmartRequester):
        self.req = requester

    def search_all(self, dork: str, max_per_engine: int = 30) -> Set[str]:
        """Busca em todos os engines disponíveis"""
        all_urls = set()

        # Engine 1: DuckDuckGo HTML (SEM proxy - IP direto é melhor)
        ddg_urls = self._search_ddg(dork, max_per_engine)
        log.info(f"DORK DDG | results={len(ddg_urls)} | dork={dork[:80]}")
        all_urls.update(ddg_urls)
        time.sleep(random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX))

        # Engine 2: Google.com.br (SEM proxy)
        google_urls = self._search_google(dork, max_per_engine)
        log.info(f"DORK Google | results={len(google_urls)} | dork={dork[:80]}")
        all_urls.update(google_urls)
        time.sleep(random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX))

        # Engine 3: Bing (SEM proxy)
        bing_urls = self._search_bing(dork, max_per_engine)
        log.info(f"DORK Bing | results={len(bing_urls)} | dork={dork[:80]}")
        all_urls.update(bing_urls)

        # Engine 4: Google CSE API (se configurada)
        if GOOGLE_CSE_API_KEY and GOOGLE_CSE_CX:
            time.sleep(1)
            cse_urls = self._search_google_cse(dork, max_per_engine)
            log.info(f"DORK CSE | results={len(cse_urls)} | dork={dork[:80]}")
            all_urls.update(cse_urls)

        return all_urls

    def _search_ddg(self, query: str, max_results: int = 30) -> Set[str]:
        """DuckDuckGo HTML - SEM proxy, IP direto"""
        urls = set()
        try:
            # Usar DDG HTML (não Lite - mais confiável)
            encoded = urllib.parse.quote(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded}"
            headers = {
                "User-Agent": random.choice(PREMIUM_USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            }
            req = urllib.request.Request(search_url, headers=headers)
            try:
                resp = urllib.request.urlopen(req, timeout=15)
                html = resp.read().decode("utf-8", errors="ignore")
                log.debug(f"DDG HTML | status={resp.status} | length={len(html)}")
            except Exception as e:
                log.debug(f"DDG HTML failed, trying Lite | {e}")
                # Fallback para DDG Lite
                search_url = f"https://lite.duckduckgo.com/lite/?q={encoded}"
                req = urllib.request.Request(search_url, headers=headers)
                resp = urllib.request.urlopen(req, timeout=15)
                html = resp.read().decode("utf-8", errors="ignore")
                log.debug(f"DDG Lite | status={resp.status} | length={len(html)}")

            # Extrair URLs do DDG
            for m in re.finditer(r'uddg=(https?%3A[^&"\']+)', html):
                u = urllib.parse.unquote(m.group(1))
                if "duckduckgo" not in u:
                    urls.add(u)

            # Padrão alternativo
            for m in re.finditer(r'href="(https?://(?!duckduckgo)[^"]+)"[^>]*class="result', html):
                urls.add(m.group(1))

            log.debug(f"DDG extracted {len(urls)} URLs")

            # Tentar página 2 se tiver resultados
            if urls and len(urls) >= 8:
                time.sleep(2)
                try:
                    search_url2 = f"https://html.duckduckgo.com/html/?q={encoded}&s=30&dc=31"
                    req2 = urllib.request.Request(search_url2, headers=headers)
                    resp2 = urllib.request.urlopen(req2, timeout=15)
                    html2 = resp2.read().decode("utf-8", errors="ignore")
                    for m in re.finditer(r'uddg=(https?%3A[^&"\']+)', html2):
                        u = urllib.parse.unquote(m.group(1))
                        if "duckduckgo" not in u:
                            urls.add(u)
                    log.debug(f"DDG page 2: total {len(urls)} URLs")
                except:
                    pass

        except Exception as e:
            log.error(f"DDG search error: {e}")
        return urls

    def _search_google(self, query: str, max_results: int = 30) -> Set[str]:
        """Google.com.br - SEM proxy, com consent cookie"""
        urls = set()
        try:
            encoded = urllib.parse.quote(query)
            for start in [0, 10]:
                search_url = f"https://www.google.com.br/search?q={encoded}&num=20&start={start}&hl=pt-BR&gl=br"
                headers = {
                    "User-Agent": random.choice(PREMIUM_USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                    "Cookie": "CONSENT=YES+cb.20210720-17-p0.en+FX+410; SOCS=CAISHAgBEhJnd3NfMjAyNDA4MTUtMF9SQzIaAmVuIAEaBgiA_LSmBg; NID=511=test",
                }

                html = None
                # Tentar com curl_cffi (melhor TLS fingerprint)
                if CFFI_OK:
                    try:
                        imp = random.choice(["chrome120", "chrome119", "chrome116"])
                        r = cffi_requests.get(search_url, impersonate=imp, timeout=15, headers=headers)
                        html = r.text
                        log.debug(f"Google | status={r.status_code} | imp={imp} | page={start//10} | length={len(html)}")
                        if r.status_code == 429:
                            log.warning("Google 429 - rate limited")
                            break
                    except Exception as e:
                        log.debug(f"Google curl_cffi error: {e}")

                # Fallback urllib
                if not html:
                    try:
                        req = urllib.request.Request(search_url, headers=headers)
                        resp = urllib.request.urlopen(req, timeout=15)
                        html = resp.read().decode("utf-8", errors="ignore")
                        log.debug(f"Google urllib | status={resp.status} | page={start//10} | length={len(html)}")
                    except Exception as e:
                        log.debug(f"Google urllib error: {e}")
                        continue

                if not html:
                    continue

                # Extrair URLs - múltiplos padrões
                page_urls = set()

                # Padrão 1: /url?q= (formato clássico)
                for m in re.finditer(r'/url\?q=(https?://[^&"]+)', html):
                    u = urllib.parse.unquote(m.group(1))
                    if not any(x in u for x in ["google.com", "gstatic", "schema.org", "youtube.com/results", "accounts.google"]):
                        page_urls.add(u)

                # Padrão 2: data-href
                for m in re.finditer(r'data-href="(https?://[^"]+)"', html):
                    page_urls.add(m.group(1))

                # Padrão 3: links diretos em resultados
                for m in re.finditer(r'<a[^>]+href="(https?://(?!www\.google|accounts\.google|support\.google|maps\.google|webcache\.google|translate\.google|play\.google)[^"]+)"[^>]*(?:data-|ping=)', html):
                    page_urls.add(m.group(1))

                # Padrão 4: cite tags (URLs visíveis nos resultados)
                for m in re.finditer(r'<cite[^>]*>(.*?)</cite>', html):
                    text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    if re.match(r'https?://', text):
                        page_urls.add(text.split(' ')[0])

                new_count = len(page_urls - urls)
                urls.update(page_urls)
                log.debug(f"Google page {start//10}: {new_count} new URLs (total: {len(urls)})")

                if start == 0 and new_count > 0:
                    time.sleep(random.uniform(2, 4))
                else:
                    break

        except Exception as e:
            log.error(f"Google search error: {e}")
        return urls

    def _search_bing(self, query: str, max_results: int = 30) -> Set[str]:
        """Bing - SEM proxy"""
        urls = set()
        try:
            encoded = urllib.parse.quote(query)
            for first in [1, 11, 21]:
                search_url = f"https://www.bing.com/search?q={encoded}&first={first}&count=10"
                headers = {
                    "User-Agent": random.choice(PREMIUM_USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "pt-BR,pt;q=0.9",
                }

                html = None
                if CFFI_OK:
                    try:
                        r = cffi_requests.get(search_url, impersonate="edge101", timeout=15, headers=headers)
                        html = r.text
                        log.debug(f"Bing | status={r.status_code} | page={first//10} | length={len(html)}")
                    except:
                        pass

                if not html:
                    try:
                        req = urllib.request.Request(search_url, headers=headers)
                        resp = urllib.request.urlopen(req, timeout=15)
                        html = resp.read().decode("utf-8", errors="ignore")
                    except:
                        continue

                if not html:
                    continue

                page_urls = set()
                # Links de resultado do Bing
                for m in re.finditer(r'<h2><a[^>]+href="(https?://(?!www\.bing|login\.live|go\.microsoft|microsoft\.com)[^"]+)"', html):
                    page_urls.add(m.group(1))
                # Cite tags
                for m in re.finditer(r'<cite>(.*?)</cite>', html):
                    text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    if text.startswith("http"):
                        page_urls.add(text)

                new_count = len(page_urls - urls)
                urls.update(page_urls)
                log.debug(f"Bing page {first//10}: {new_count} new URLs (total: {len(urls)})")

                if new_count == 0:
                    break
                time.sleep(random.uniform(2, 3))

        except Exception as e:
            log.error(f"Bing search error: {e}")
        return urls

    def _search_google_cse(self, query: str, max_results: int = 30) -> Set[str]:
        """Google Custom Search Engine API - resultados limpos em JSON"""
        urls = set()
        if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX:
            return urls
        try:
            for start in [1, 11]:
                api_url = (
                    f"https://www.googleapis.com/customsearch/v1"
                    f"?key={GOOGLE_CSE_API_KEY}&cx={GOOGLE_CSE_CX}"
                    f"&q={urllib.parse.quote(query)}&start={start}&num=10&gl=br&lr=lang_pt"
                )
                req = urllib.request.Request(api_url)
                resp = urllib.request.urlopen(req, timeout=15)
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                for item in items:
                    urls.add(item["link"])
                log.debug(f"Google CSE | start={start} | results={len(items)}")
                if len(items) < 10:
                    break
                time.sleep(1)
        except Exception as e:
            log.error(f"Google CSE error: {e}")
        return urls

# ══════════════════════════════════════════════════════════════════
#                     URL FILTER
# ══════════════════════════════════════════════════════════════════

class URLFilter:
    """Filtra URLs indesejadas antes da análise"""

    @staticmethod
    def is_valid(url: str) -> Tuple[bool, str]:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            path = parsed.path.lower()

            # Verificar blacklist de domínios
            for bl in DOMAIN_BLACKLIST:
                if domain == bl or domain.endswith("." + bl):
                    log.debug(f"FILTERED | reason=blacklist:{bl} | url={url[:100]}")
                    return False, f"blacklist:{bl}"

            # Verificar subdomínios informativos
            for sub in INFORMATIONAL_SUBDOMAINS:
                if domain.startswith(sub):
                    log.debug(f"FILTERED | reason=informational_subdomain:{sub} | url={url[:100]}")
                    return False, f"subdomain:{sub}"

            # Verificar paths ruins
            for bp in BAD_PATH_PATTERNS:
                if bp in path:
                    log.debug(f"FILTERED | reason=bad_path:{bp} | url={url[:100]}")
                    return False, f"bad_path:{bp}"

            # Filtrar URLs sem domínio real
            if "." not in domain:
                return False, "no_tld"

            # Filtrar URLs com fragmentos de busca (cite tags do Bing)
            if " › " in url or "..." in url:
                # Reconstruir URL do Bing cite
                clean = url.split(" › ")[0].split("...")[0].strip()
                if clean.startswith("http"):
                    return True, "cleaned"
                return False, "bing_cite_fragment"

            return True, "ok"
        except:
            return False, "parse_error"

    @staticmethod
    def deduplicate_by_domain(urls: Set[str]) -> List[str]:
        """Mantém apenas 1 URL por domínio"""
        seen_domains = set()
        unique = []
        for url in sorted(urls):
            try:
                domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    unique.append(url)
            except:
                continue
        return unique

# ══════════════════════════════════════════════════════════════════
#                    SITE ANALYZER
# ══════════════════════════════════════════════════════════════════

class SiteAnalyzer:
    """Analisa sites para confirmar gateway e classificar como loja"""

    ECOMMERCE_PLATFORMS = {
        "WooCommerce": [r"woocommerce", r"wc-cart", r"add-to-cart", r"wp-content/plugins/woocommerce"],
        "Shopify": [r"cdn\.shopify\.com", r"shopify-section", r"myshopify"],
        "VTEX": [r"vtex\.com", r"vteximg", r"vtexcommerce"],
        "Magento": [r"magento", r"mage-", r"Magento_"],
        "PrestaShop": [r"prestashop", r"presta-"],
        "OpenCart": [r"opencart", r"route=product"],
        "Nuvemshop": [r"nuvemshop", r"tiendanube", r"lojanuvem"],
        "Tray": [r"tray\.com\.br", r"traycorp"],
        "Loja Integrada": [r"lojaintegrada", r"loja-integrada"],
        "Yampi": [r"yampi\.com\.br", r"yampi\.io"],
        "Cartpanda": [r"cartpanda"],
        "Hotmart": [r"hotmart\.com", r"pay\.hotmart"],
    }

    STORE_POSITIVE_SIGNALS = [
        (r'R\$\s*\d+[.,]\d{2}', 5, "price_brl"),
        (r'class="[^"]*price[^"]*"', 4, "price_class"),
        (r'adicionar.*carrinho|add.to.cart|comprar.agora|buy.now', 5, "buy_button"),
        (r'carrinho|cart|sacola|bag', 3, "cart"),
        (r'checkout|finalizar.compra|fechar.pedido', 4, "checkout"),
        (r'frete|shipping|entrega|envio|sedex|correios', 4, "shipping"),
        (r'cep|zip.code|calcular.frete', 3, "shipping_calc"),
        (r'produto|product|item', 2, "product"),
        (r'estoque|stock|disponivel|disponibilidade', 2, "stock"),
        (r'tamanho|size|cor|color|variacao|variation', 2, "variations"),
        (r'avaliacao|review|estrela|rating', 2, "reviews"),
        (r'cupom|coupon|desconto|discount|promocao', 2, "promo"),
        (r'pix|boleto|cartao.de.credito|credit.card|debito', 3, "payment_method"),
        (r'parcela|installment|parcelamento|vezes.sem.juros', 3, "installments"),
        (r'minha.conta|my.account|meus.pedidos|my.orders', 2, "user_account"),
        (r'politica.de.troca|devolucao|refund|exchange', 2, "return_policy"),
    ]

    STORE_NEGATIVE_SIGNALS = [
        (r'documentacao|documentation|api.reference|endpoint', -10, "documentation"),
        (r'tutorial|how.to|como.usar|passo.a.passo|step.by.step', -8, "tutorial"),
        (r'blog|artigo|article|post|noticias|news', -6, "blog"),
        (r'central.de.ajuda|help.center|suporte|support.ticket', -8, "support"),
        (r'comparativo|comparison|versus|vs\.|alternativas', -6, "comparison"),
        (r'integrar|integracao|integration|sdk|api.key|webhook', -8, "integration"),
        (r'cadastre-se.gratis|free.trial|teste.gratis|sign.up.free', -5, "saas_signup"),
        (r'planos.e.precos|pricing|nossos.planos|our.plans', -5, "pricing_page"),
        (r'sobre.nos|about.us|quem.somos|nossa.historia', -4, "about_page"),
        (r'vagas|careers|trabalhe.conosco|join.our.team', -8, "careers"),
        (r'case.de.sucesso|success.story|depoimento|testimonial', -4, "case_study"),
    ]

    def __init__(self, requester: SmartRequester, gateway_sigs: List[str]):
        self.req = requester
        self.sigs = [s.lower() for s in gateway_sigs]

    def analyze(self, url: str) -> Optional[Dict]:
        """Analisa um site: confirma gateway + classifica como loja"""
        try:
            log.debug(f"ANALYZING | url={url[:100]}")
            html = self.req.get(url, use_proxy=True, timeout=REQUEST_TIMEOUT)
            if not html:
                log.debug(f"ANALYZE FAIL | no response | url={url[:80]}")
                return None

            html_lower = html.lower()
            result = {
                "url": url,
                "domain": urllib.parse.urlparse(url).netloc.lower().replace("www.", ""),
                "title": self._extract_title(html),
                "description": self._extract_meta(html, "description"),
                "keywords": self._extract_meta(html, "keywords"),
                "gateway_confirmed": False,
                "gateway_matches": [],
                "is_real_store": False,
                "store_score": 0,
                "store_signals": [],
                "category": "",
                "platform": "Desconhecida",
                "technologies": [],
                "ssl": url.startswith("https"),
                "emails": self._extract_emails(html),
                "phones": self._extract_phones(html),
                "html_size": len(html),
                "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # 1. Confirmar gateway
            result["gateway_confirmed"], result["gateway_matches"] = self._confirm_gateway(html, html_lower)

            # 2. Detectar plataforma
            result["platform"], result["technologies"] = self._detect_platform(html_lower)

            # 3. Calcular store score
            result["store_score"], result["store_signals"] = self._calculate_store_score(html_lower)
            result["is_real_store"] = result["store_score"] >= STORE_SCORE_THRESHOLD

            # 4. Classificar categoria
            result["category"] = self._classify_category(html_lower, result)

            # 5. Status final
            if result["gateway_confirmed"] and result["is_real_store"]:
                result["status"] = "LOJA_CONFIRMADA"
            elif result["gateway_confirmed"]:
                result["status"] = "GATEWAY_SIM_LOJA_NAO"
            elif result["is_real_store"]:
                result["status"] = "LOJA_SIM_GATEWAY_NAO"
            else:
                result["status"] = "NAO_CONFIRMADO"

            log.info(f"ANALYZED | {result['status']} | score={result['store_score']} | gw={'SIM' if result['gateway_confirmed'] else 'NAO'} | {result['domain']} | {result['category']}")
            return result

        except Exception as e:
            log.error(f"ANALYZE ERROR | {type(e).__name__}: {str(e)[:100]} | url={url[:80]}")
            return None

    def _confirm_gateway(self, html: str, html_lower: str) -> Tuple[bool, List[str]]:
        """Confirma presença da gateway no código fonte"""
        matches = []

        # Zona 1: Scripts (src)
        for m in re.finditer(r'<script[^>]*src=["\']([^"\']+)["\']', html, re.I):
            src = m.group(1).lower()
            for sig in self.sigs:
                if sig in src:
                    matches.append(f"JS_SRC:{sig}")

        # Zona 2: Iframes
        for m in re.finditer(r'<iframe[^>]*src=["\']([^"\']+)["\']', html, re.I):
            src = m.group(1).lower()
            for sig in self.sigs:
                if sig in src:
                    matches.append(f"IFRAME:{sig}")

        # Zona 3: Forms (action)
        for m in re.finditer(r'<form[^>]*action=["\']([^"\']+)["\']', html, re.I):
            action = m.group(1).lower()
            for sig in self.sigs:
                if sig in action:
                    matches.append(f"FORM:{sig}")

        # Zona 4: Links (href)
        for m in re.finditer(r'href=["\']([^"\']*(?:checkout|pay|pagamento)[^"\']*)["\']', html, re.I):
            href = m.group(1).lower()
            for sig in self.sigs:
                if sig in href:
                    matches.append(f"LINK:{sig}")

        # Zona 5: Inline scripts (variáveis JS)
        for m in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.I | re.S):
            content = m.group(1).lower()[:5000]
            for sig in self.sigs:
                if sig in content:
                    matches.append(f"INLINE_JS:{sig}")
                    break

        # Zona 6: Meta tags e data attributes
        for m in re.finditer(r'(?:data-|content=)["\']([^"\']+)["\']', html, re.I):
            val = m.group(1).lower()
            for sig in self.sigs:
                if sig in val and len(val) < 500:
                    matches.append(f"META:{sig}")

        # Zona 7: Texto visível (menos confiável, precisa de mais ocorrências)
        for sig in self.sigs:
            count = html_lower.count(sig)
            if count >= 3:
                matches.append(f"TEXT({count}x):{sig}")

        unique_matches = list(set(matches))
        confirmed = len(unique_matches) > 0
        return confirmed, unique_matches[:10]

    def _detect_platform(self, html_lower: str) -> Tuple[str, List[str]]:
        platform = "Desconhecida"
        techs = []
        for name, patterns in self.ECOMMERCE_PLATFORMS.items():
            for pat in patterns:
                if re.search(pat, html_lower):
                    platform = name
                    break
            if platform != "Desconhecida":
                break
        # Detectar tecnologias
        tech_patterns = {
            "WordPress": r"wp-content|wordpress",
            "React": r"react|__next",
            "Vue.js": r"vue\.js|v-bind|v-model",
            "Angular": r"ng-app|angular",
            "jQuery": r"jquery",
            "Bootstrap": r"bootstrap",
            "Google Tag Manager": r"googletagmanager|gtm\.js",
            "Google Analytics": r"google-analytics|gtag\(",
            "Facebook Pixel": r"fbq\(|facebook\.net/en_US/fbevents",
            "Cloudflare": r"cloudflare|cf-ray",
        }
        for tech, pat in tech_patterns.items():
            if re.search(pat, html_lower):
                techs.append(tech)
        return platform, techs

    def _calculate_store_score(self, html_lower: str) -> Tuple[int, List[str]]:
        score = 0
        signals = []
        for pattern, points, name in self.STORE_POSITIVE_SIGNALS:
            matches = re.findall(pattern, html_lower[:100000])
            if matches:
                score += points
                signals.append(f"+{points}:{name}({len(matches)})")
        for pattern, points, name in self.STORE_NEGATIVE_SIGNALS:
            if re.search(pattern, html_lower[:100000]):
                score += points
                signals.append(f"{points}:{name}")
        # Bonus por plataforma e-commerce
        for name, patterns in self.ECOMMERCE_PLATFORMS.items():
            for pat in patterns:
                if re.search(pat, html_lower):
                    score += 5
                    signals.append(f"+5:platform:{name}")
                    break
            break
        return score, signals

    def _classify_category(self, html_lower: str, result: Dict) -> str:
        if not result["is_real_store"]:
            return f"Nao e loja (score: {result['store_score']})"

        categories = {
            "Moda / Roupas": r"roupa|camiseta|vestido|calca|blusa|moda|fashion|jeans|saia|bermuda",
            "Calcados / Tenis": r"tenis|sapato|sandalia|bota|calcado|sneaker|shoe",
            "Eletronicos / Tecnologia": r"celular|smartphone|notebook|computador|tablet|fone|eletronico|tech",
            "Casa / Decoracao": r"decoracao|movel|sofa|cama|mesa|cadeira|cortina|tapete|casa",
            "Beleza / Cosmeticos": r"perfume|maquiagem|cosmetico|creme|shampoo|beleza|skincare",
            "Saude / Suplementos": r"suplemento|vitamina|whey|proteina|saude|fitness|natural",
            "Pet Shop / Animais": r"pet|racao|cachorro|gato|animal|veterinar",
            "Alimentos / Bebidas": r"alimento|comida|bebida|cafe|vinho|cerveja|gourmet|organico",
            "Joias / Acessorios": r"joia|anel|colar|brinco|pulseira|relogio|acessorio|bijuteria",
            "Esportes / Fitness": r"esporte|academia|treino|yoga|corrida|bicicleta|futebol",
            "Livros / Educacao": r"livro|book|ebook|curso|educacao|apostila|material.didatico",
            "Brinquedos / Infantil": r"brinquedo|infantil|crianca|bebe|kids|toy",
            "Automotivo": r"automotivo|carro|moto|peca|acessorio.automotivo|pneu",
            "Curso / Produto Digital": r"curso.online|infoproduto|mentoria|treinamento|aula",
            "Servicos / Assinatura": r"assinatura|plano|mensalidade|servico|subscription",
        }
        for cat, pattern in categories.items():
            if re.search(pattern, html_lower[:50000]):
                return cat
        return "Loja Online / E-commerce"

    def _extract_title(self, html: str) -> str:
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
        return m.group(1).strip()[:200] if m else "N/A"

    def _extract_meta(self, html: str, name: str) -> str:
        m = re.search(rf'<meta[^>]*name=["\'](?:og:)?{name}["\'][^>]*content=["\']([^"\']+)', html, re.I)
        if not m:
            m = re.search(rf'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\'](?:og:)?{name}', html, re.I)
        return m.group(1).strip()[:300] if m else "N/A"

    def _extract_emails(self, html: str) -> List[str]:
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html[:100000]))
        return [e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.svg', '.css', '.js'))][:5]

    def _extract_phones(self, html: str) -> List[str]:
        phones = set()
        for m in re.finditer(r'(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}', html[:100000]):
            phone = m.group().strip()
            if len(re.sub(r'\D', '', phone)) >= 10:
                phones.add(phone)
        return list(phones)[:5]

# ══════════════════════════════════════════════════════════════════
#                   REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, gateway: str, results: List[Dict], stats: Dict, elapsed: float) -> Dict[str, str]:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"gatehunter_{gateway.lower()}_{ts}"
        files = {}

        # Separar lojas confirmadas
        lojas = [r for r in results if r.get("status") == "LOJA_CONFIRMADA"]
        gw_only = [r for r in results if r.get("status") == "GATEWAY_SIM_LOJA_NAO"]
        loja_only = [r for r in results if r.get("status") == "LOJA_SIM_GATEWAY_NAO"]

        # 1. Relatório TXT completo
        txt_path = os.path.join(self.output_dir, f"{prefix}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{'='*70}\n")
            f.write(f"  GATEHUNTER v{VERSION} - RELATORIO COMPLETO\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"Gateway        : {gateway}\n")
            f.write(f"Data           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tempo total    : {elapsed:.1f}s\n")
            f.write(f"URLs analisadas: {len(results)}\n")
            f.write(f"Lojas confirm. : {len(lojas)}\n")
            f.write(f"Gateway s/ loja: {len(gw_only)}\n")
            f.write(f"Loja s/ gateway: {len(loja_only)}\n")
            f.write(f"Requests total : {stats.get('requests', 0)}\n")
            f.write(f"Bloqueios      : {stats.get('blocked', 0)}\n\n")

            if lojas:
                f.write(f"\n{'='*70}\n")
                f.write(f"  LOJAS CONFIRMADAS (Gateway + E-commerce)\n")
                f.write(f"{'='*70}\n\n")
                for i, r in enumerate(lojas, 1):
                    f.write(f"  [{i:3d}] {r['url']}\n")
                    f.write(f"        Titulo    : {r['title'][:80]}\n")
                    f.write(f"        Categoria : {r['category']}\n")
                    f.write(f"        Plataforma: {r['platform']}\n")
                    f.write(f"        Score     : {r['store_score']}\n")
                    f.write(f"        Gateway   : {', '.join(r['gateway_matches'][:3])}\n")
                    if r['emails']:
                        f.write(f"        Emails    : {', '.join(r['emails'])}\n")
                    if r['phones']:
                        f.write(f"        Telefones : {', '.join(r['phones'])}\n")
                    f.write(f"\n")

            if gw_only:
                f.write(f"\n{'='*70}\n")
                f.write(f"  SITES COM GATEWAY (nao confirmados como loja)\n")
                f.write(f"{'='*70}\n\n")
                for i, r in enumerate(gw_only, 1):
                    f.write(f"  [{i:3d}] {r['url']}\n")
                    f.write(f"        Titulo    : {r['title'][:80]}\n")
                    f.write(f"        Score     : {r['store_score']}\n")
                    f.write(f"        Gateway   : {', '.join(r['gateway_matches'][:3])}\n\n")

            if loja_only:
                f.write(f"\n{'='*70}\n")
                f.write(f"  LOJAS SEM GATEWAY CONFIRMADA\n")
                f.write(f"{'='*70}\n\n")
                for i, r in enumerate(loja_only, 1):
                    f.write(f"  [{i:3d}] {r['url']}\n")
                    f.write(f"        Titulo    : {r['title'][:80]}\n")
                    f.write(f"        Categoria : {r['category']}\n")
                    f.write(f"        Score     : {r['store_score']}\n\n")

        files["txt"] = txt_path
        log.info(f"REPORT TXT | {txt_path} | {os.path.getsize(txt_path)} bytes")

        # 2. JSON completo
        json_path = os.path.join(self.output_dir, f"{prefix}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": VERSION,
                "gateway": gateway,
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "stats": stats,
                "total_results": len(results),
                "stores_found": len(lojas),
                "results": results,
            }, f, ensure_ascii=False, indent=2)
        files["json"] = json_path
        log.info(f"REPORT JSON | {json_path} | {os.path.getsize(json_path)} bytes")

        # 3. Lista de todas as URLs
        urls_path = os.path.join(self.output_dir, f"{prefix}_all_urls.txt")
        with open(urls_path, "w") as f:
            for r in results:
                f.write(f"{r['url']}\n")
        files["urls"] = urls_path

        # 4. Lista de LOJAS confirmadas
        lojas_path = os.path.join(self.output_dir, f"{prefix}_LOJAS.txt")
        with open(lojas_path, "w", encoding="utf-8") as f:
            f.write(f"# LOJAS CONFIRMADAS - {gateway} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(lojas)} lojas\n\n")
            for r in lojas:
                f.write(f"{r['url']} | {r['category']} | {r['platform']} | Score:{r['store_score']}\n")
        files["lojas"] = lojas_path
        log.info(f"REPORT LOJAS | {lojas_path} | {len(lojas)} lojas")

        return files

# ══════════════════════════════════════════════════════════════════
#                    GATEHUNTER MAIN CLASS
# ══════════════════════════════════════════════════════════════════

class GateHunter:
    def __init__(self):
        self.proxy = ProxyRotator()
        self.requester = SmartRequester(self.proxy)
        self.dork_engine = DorkEngine(self.requester)
        self.url_filter = URLFilter()
        self.output_dir = OUTPUT_DIR if os.path.isdir(OUTPUT_DIR) else FALLBACK_OUTPUT
        os.makedirs(self.output_dir, exist_ok=True)
        self.report = ReportGenerator(self.output_dir)
        log.info(f"GateHunter initialized | output={self.output_dir} | proxies={len(self.proxy.proxies)}")

    def show_banner(self):
        banner = f"""
{R}╔══════════════════════════════════════════════════════════════╗{RST}
{R}║{RST}  {C}  ██████   █████  ████████ ███████{RST}                          {R}║{RST}
{R}║{RST}  {C} ██       ██   ██    ██    ██     {RST}                          {R}║{RST}
{R}║{RST}  {C} ██   ███ ███████    ██    █████  {RST}                          {R}║{RST}
{R}║{RST}  {C} ██    ██ ██   ██    ██    ██     {RST}                          {R}║{RST}
{R}║{RST}  {C}  ██████  ██   ██    ██    ███████{RST}                          {R}║{RST}
{R}║{RST}  {Y} ██   ██ ██    ██ ███    ██ ████████ ███████ ██████  {RST}       {R}║{RST}
{R}║{RST}  {Y} ██   ██ ██    ██ ████   ██    ██    ██      ██   ██ {RST}       {R}║{RST}
{R}║{RST}  {Y} ███████ ██    ██ ██ ██  ██    ██    █████   ██████  {RST}       {R}║{RST}
{R}║{RST}  {Y} ██   ██ ██    ██ ██  ██ ██    ██    ██      ██   ██ {RST}       {R}║{RST}
{R}║{RST}  {Y} ██   ██  ██████  ██   ████    ██    ███████ ██   ██ {RST}       {R}║{RST}
{R}║{RST}                                                              {R}║{RST}
{R}║{RST}  {W}v{VERSION}{RST} // {G}NETHUNTER SUPREME EDITION{RST} // {M}Payment Gateway OSINT{RST} {R}║{RST}
{R}╠══════════════════════════════════════════════════════════════╣{RST}
{R}║{RST} {C}Engine{RST}  : curl_cffi Impersonate + Multi-Thread + Proxy Pool  {R}║{RST}
{R}║{RST} {C}Evasion{RST} : TLS Fingerprint + Header Spoof + UA Rotation      {R}║{RST}
{R}║{RST} {C}Search{RST}  : DDG HTML + Google.com.br + Bing (Multi-Engine)     {R}║{RST}
{R}║{RST} {C}Filter{RST}  : 3-Layer Validation + Store Score + Blacklist       {R}║{RST}
{R}║{RST} {C}Output{RST}  : {self.output_dir}/ (TXT + JSON + URLs)  {R}║{RST}
{R}║{RST} {C}Logs{RST}    : {log.log_path or 'N/A'}  {R}║{RST}
{R}╚══════════════════════════════════════════════════════════════╝{RST}
"""
        print(banner)

    def show_config(self):
        print(f"\n{M}┌─────────────────────────────────────────┐{RST}")
        print(f"{M}│{RST}  {W}CONFIGURACAO ATIVA{RST}                       {M}│{RST}")
        print(f"{M}├─────────────────────────────────────────┤{RST}")
        print(f"{M}│{RST}  {C}Proxies Carregadas{RST}  :  {G}{len(self.proxy.proxies)}{RST}               {M}│{RST}")
        print(f"{M}│{RST}  {C}Threads{RST}             :  {G}{MAX_THREADS}{RST}              {M}│{RST}")
        print(f"{M}│{RST}  {C}Timeout{RST}             :  {G}{REQUEST_TIMEOUT}s{RST}             {M}│{RST}")
        print(f"{M}│{RST}  {C}curl_cffi{RST}           :  {G if CFFI_OK else R}{'OK' if CFFI_OK else 'N/A'}{RST}              {M}│{RST}")
        cse = f"{G}OK{RST}" if GOOGLE_CSE_API_KEY else f"{Y}N/A{RST}"
        print(f"{M}│{RST}  {C}Google CSE API{RST}      :  {cse}             {M}│{RST}")
        engines = "DDG + Google + Bing"
        if GOOGLE_CSE_API_KEY:
            engines += " + CSE"
        print(f"{M}│{RST}  {C}Engines{RST}             :  {G}{engines}{RST}  {M}│{RST}")
        print(f"{M}│{RST}  {C}Busca via{RST}           :  {G}IP Direto (sem proxy){RST}  {M}│{RST}")
        print(f"{M}│{RST}  {C}Analise via{RST}         :  {G}Proxy Pool{RST}            {M}│{RST}")
        print(f"{M}└─────────────────────────────────────────┘{RST}")

    def show_menu(self):
        print(f"\n{M}┌─────────────────────────────────────────────────────────────┐{RST}")
        print(f"{M}│{RST}  {W}SELECIONE A GATEWAY DE PAGAMENTO{RST}                            {M}│{RST}")
        print(f"{M}├─────────────────────────────────────────────────────────────┤{RST}")
        gw_list = list(GATEWAYS.keys())
        for i, gw in enumerate(gw_list, 1):
            desc = GATEWAYS[gw]["desc"]
            print(f"{M}│{RST}  {G}[{i:2d}]{RST}  {W}{gw:15s}{RST} {D}{desc}{RST}")
        print(f"{M}├─────────────────────────────────────────────────────────────┤{RST}")
        print(f"{M}│{RST}  {Y}[ 0]{RST}  {W}CUSTOM{RST} - Inserir gateway personalizada                 {M}│{RST}")
        print(f"{M}│{RST}  {R}[99]{RST}  {W}SAIR{RST}                                                   {M}│{RST}")
        print(f"{M}└─────────────────────────────────────────────────────────────┘{RST}")
        return gw_list

    def get_custom_gateway(self) -> Optional[Dict]:
        print(f"\n{C}[*] Gateway Personalizada{RST}")
        name = input(f"{G}Nome da gateway: {RST}").strip()
        if not name:
            return None
        sigs_raw = input(f"{G}Assinaturas (separadas por virgula): {RST}").strip()
        sigs = [s.strip() for s in sigs_raw.split(",") if s.strip()]
        if not sigs:
            print(f"{R}[!] Necessario pelo menos uma assinatura{RST}")
            return None
        dorks_raw = input(f"{G}Dorks (separadas por | ou Enter para auto): {RST}").strip()
        if dorks_raw:
            dorks = [d.strip() for d in dorks_raw.split("|") if d.strip()]
        else:
            dorks = [
                f'"{sigs[0]}" comprar loja online',
                f'"{sigs[0]}" checkout pagamento',
                f'"{sigs[0]}" ecommerce produto',
                f'"{sigs[0]}" "finalizar compra"',
                f'"{sigs[0]}" carrinho loja virtual',
            ]
        return {"name": name, "desc": f"{name} - Gateway personalizada", "signatures": sigs, "dorks": dorks}

    def _execute_scan(self, gateway_name: str, gateway_data: Dict):
        """Executa o scan completo para uma gateway"""
        start_time = time.time()
        dorks = gateway_data["dorks"]
        sigs = gateway_data["signatures"]

        log.info("=" * 60)
        log.info(f"SCAN START | gateway={gateway_name} | dorks={len(dorks)} | sigs={len(sigs)} | proxies={len(self.proxy.proxies)}")
        for i, d in enumerate(dorks):
            log.info(f"  DORK[{i}] = {d}")
        log.info("=" * 60)

        print(f"\n{'='*60}")
        print(f"  {G}INICIANDO SCAN: {W}{gateway_name}{RST}")
        print(f"{'='*60}\n")
        print(f"  {C}Gateway{RST}     : {gateway_name}")
        print(f"  {C}Dorks{RST}       : {len(dorks)}")
        print(f"  {C}Assinaturas{RST} : {', '.join(sigs[:4])}")
        print(f"  {C}Proxies{RST}     : {len(self.proxy.proxies)}")
        print(f"  {C}Threads{RST}     : {MAX_THREADS}")
        print()

        # ── FASE 1: Coletar URLs via Dorks ──
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{ts} {B}[-]{RST} FASE 1/3: Coletando URLs via Dorks (Multi-Engine)...")
        log.info("PHASE | 1/3 | Coletando URLs via Dorks (Multi-Engine)")

        raw_urls = set()
        for i, dork in enumerate(dorks):
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"{ts} {B}[-]{RST} Dork [{i+1}/{len(dorks)}]: {dork[:60]}...")
            log.info(f"PHASE | DORK {i+1}/{len(dorks)} | {dork[:80]}")

            dork_urls = self.dork_engine.search_all(dork)
            new_urls = dork_urls - raw_urls
            raw_urls.update(dork_urls)

            ts = datetime.now().strftime("%H:%M:%S")
            print(f"{ts} {G}[+]{RST}   -> {len(new_urls)} URLs novas encontradas")

            if i < len(dorks) - 1:
                time.sleep(random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX))

        # ── Filtrar URLs ──
        valid_urls = []
        for url in raw_urls:
            is_valid, reason = self.url_filter.is_valid(url)
            if is_valid:
                valid_urls.append(url)

        # Deduplicar por domínio
        unique_urls = self.url_filter.deduplicate_by_domain(set(valid_urls))

        ts = datetime.now().strftime("%H:%M:%S")
        log.info(f"DORK SUMMARY | raw={len(raw_urls)} | filtered={len(valid_urls)} | unique_domains={len(unique_urls)}")
        print(f"\n{ts} {G}[+]{RST} Total URLs brutas: {len(raw_urls)}")
        print(f"{ts} {G}[+]{RST} Após filtro: {len(valid_urls)}")
        print(f"{ts} {G}[+]{RST} Domínios únicos: {len(unique_urls)}")

        if not unique_urls:
            print(f"\n{R}[!] Nenhuma URL encontrada após filtragem{RST}")
            print(f"{Y}[*] Tente uma gateway diferente ou dorks customizadas{RST}")
            log.warning("No URLs found after filtering")
            elapsed = time.time() - start_time
            self.report.generate(gateway_name, [], self.requester.stats, elapsed)
            return

        # ── FASE 2: Analisar Sites ──
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n{ts} {B}[-]{RST} FASE 2/3: Analisando {len(unique_urls)} sites ({MAX_THREADS} threads)...")
        log.info(f"PHASE | 2/3 | Analisando {len(unique_urls)} sites ({MAX_THREADS} threads)")

        analyzer = SiteAnalyzer(self.requester, sigs)
        results = []
        confirmed_count = 0

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as pool:
            futures = {pool.submit(analyzer.analyze, url): url for url in unique_urls}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        status_color = G if result["status"] == "LOJA_CONFIRMADA" else (Y if "SIM" in result["status"] else D)
                        ts = datetime.now().strftime("%H:%M:%S")
                        confirmed_count += 1
                        print(f"{ts} {status_color}[{confirmed_count}/{len(unique_urls)}]{RST} {result['status']} {result['domain']} | {result['category']}")
                except Exception as e:
                    log.error(f"Future error: {e}")

        # ── FASE 3: Gerar Relatórios ──
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n{ts} {B}[-]{RST} FASE 3/3: Gerando relatórios...")
        log.info("PHASE | 3/3 | Gerando relatórios")

        elapsed = time.time() - start_time
        files = self.report.generate(gateway_name, results, self.requester.stats, elapsed)

        # ── Resumo Final ──
        lojas = [r for r in results if r.get("status") == "LOJA_CONFIRMADA"]
        gw_only = [r for r in results if r.get("status") == "GATEWAY_SIM_LOJA_NAO"]

        print(f"\n{'='*60}")
        print(f"  {G}SCAN COMPLETO!{RST}")
        print(f"{'='*60}")
        print(f"  {C}Gateway{RST}         : {G}{gateway_name}{RST}")
        print(f"  {C}Tempo total{RST}     : {G}{elapsed:.1f}s{RST}")
        print(f"  {C}URLs analisadas{RST} : {W}{len(results)}{RST}")
        print(f"  {C}Lojas confirm.{RST} : {G}{len(lojas)}{RST}")
        print(f"  {C}Gateway s/loja{RST} : {Y}{len(gw_only)}{RST}")
        print(f"  {C}Requests total{RST} : {W}{self.requester.stats['requests']}{RST}")
        print(f"  {C}Bloqueios{RST}      : {R}{self.requester.stats['blocked']}{RST}")

        print(f"\n  {W}Arquivos gerados:{RST}")
        for key, path in files.items():
            size = os.path.getsize(path) if os.path.exists(path) else 0
            print(f"  {G}[-]{RST}   {key.upper():10s} = {path} ({size:,} bytes)")

        if lojas:
            print(f"\n  {G}TOP LOJAS CONFIRMADAS:{RST}")
            for i, r in enumerate(lojas[:15], 1):
                print(f"  {G}{i:3d}. {W}{r['domain']:35s}{RST} | {C}{r['category']}{RST}")

        # Categorias
        cats = {}
        for r in results:
            cat = r.get("category", "N/A")
            cats[cat] = cats.get(cat, 0) + 1
        if cats:
            print(f"\n  {M}CATEGORIAS:{RST}")
            for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:8]:
                bar = "█" * min(count, 30)
                print(f"  {W}{cat:35s}{RST} {G}{count:3d}{RST} {C}{bar}{RST}")

        print(f"\n{'='*60}")
        log.info(f"SCAN COMPLETE | gateway={gateway_name} | elapsed={elapsed:.1f}s | results={len(results)} | lojas={len(lojas)}")

    def run(self):
        """Loop principal do menu"""
        log.start_session()
        self.show_banner()
        self.show_config()

        while True:
            gw_list = self.show_menu()
            try:
                choice = input(f"\n{G}GateHunter > {RST}").strip()
                if choice == "99":
                    print(f"\n{M}[*] Ate a proxima! GateHunter out.{RST}\n")
                    break
                elif choice == "0":
                    custom = self.get_custom_gateway()
                    if custom:
                        self._execute_scan(custom["name"], custom)
                elif choice.isdigit() and 1 <= int(choice) <= len(gw_list):
                    gw_name = gw_list[int(choice) - 1]
                    self._execute_scan(gw_name, GATEWAYS[gw_name])
                else:
                    print(f"{R}[!] Opcao invalida{RST}")
            except KeyboardInterrupt:
                print(f"\n{Y}[!] Ctrl+C detectado. Voltando ao menu...{RST}")
            except Exception as e:
                print(f"{R}[!] Erro: {e}{RST}")
                log.error(f"Menu error: {traceback.format_exc()}")

            # Reset stats para próximo scan
            self.requester.stats = {"requests": 0, "success": 0, "failed": 0, "blocked": 0}
            input(f"\n{D}Pressione Enter para voltar ao menu...{RST}")

# ══════════════════════════════════════════════════════════════════
#                          MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    try:
        hunter = GateHunter()
        hunter.run()
    except KeyboardInterrupt:
        print(f"\n{M}[*] Encerrado pelo usuario.{RST}")
    except Exception as e:
        print(f"\n{R}[!] Erro fatal: {e}{RST}")
        log.error(f"FATAL: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
