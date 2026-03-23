#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║              GATEHUNTER v3.0 - NETHUNTER EDITION                ║
║         Advanced Payment Gateway Scraper & Analyzer             ║
║                   Kali NetHunter Optimized                      ║
╚══════════════════════════════════════════════════════════════════╝

Ferramenta profissional de OSINT para identificação e catalogação
de LOJAS e E-COMMERCES REAIS que utilizam gateways de pagamento.

v3.0 - Dorks inteligentes + Filtro anti-lixo + Validação rigorosa
Uso educacional e autorizado apenas.
"""

import os
import sys
import re
import json
import time
import random
import hashlib
import signal
import threading
import urllib.parse
import urllib.request
import ssl
import logging
import traceback
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Tuple, Any, Set
import warnings
warnings.filterwarnings("ignore")

# ── Dependências externas ──────────────────────────────────────
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.text import Text
    from rich.prompt import Prompt, IntPrompt
    from rich import box
    RICH_OK = True
except ImportError:
    RICH_OK = False

try:
    from curl_cffi import requests as cffi_requests
    CFFI_OK = True
except ImportError:
    CFFI_OK = False

try:
    from fake_useragent import UserAgent
    UA_GEN = UserAgent(browsers=["chrome", "firefox", "edge", "safari"])
except Exception:
    UA_GEN = None

console = Console() if RICH_OK else None

# ══════════════════════════════════════════════════════════════════
#                     SISTEMA DE DEBUG LOGGING
# ══════════════════════════════════════════════════════════════════

class DebugLogger:
    """Sistema de logging ultra detalhado para diagnóstico."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._log_lock = threading.Lock()

        log_dirs = ["/sdcard/nh_files", os.path.expanduser("~/gatehunter_output")]
        self.log_path = None
        for d in log_dirs:
            try:
                os.makedirs(d, exist_ok=True)
                test_path = os.path.join(d, ".log_test")
                with open(test_path, "w") as f:
                    f.write("test")
                os.remove(test_path)
                self.log_path = os.path.join(d, "gatehunter_debug.log")
                break
            except (PermissionError, OSError):
                continue

        if not self.log_path:
            self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gatehunter_debug.log")

        self.logger = logging.getLogger("GateHunter")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        try:
            fh = logging.FileHandler(self.log_path, mode="a", encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fmt = logging.Formatter(
                "[%(asctime)s] [%(levelname)-8s] [%(threadName)-12s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)
        except Exception:
            pass

        self._write_header()

    def _write_header(self):
        sep = "=" * 80
        self.logger.info(sep)
        self.logger.info("GATEHUNTER v3.0 - DEBUG LOG SESSION STARTED")
        self.logger.info(f"Timestamp    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Python       : {sys.version}")
        self.logger.info(f"Platform     : {sys.platform}")
        self.logger.info(f"PID          : {os.getpid()}")
        self.logger.info(f"Log Path     : {self.log_path}")
        self.logger.info(f"curl_cffi    : {'OK' if CFFI_OK else 'NOT AVAILABLE'}")
        self.logger.info(f"rich         : {'OK' if RICH_OK else 'NOT AVAILABLE'}")
        self.logger.info(f"fake_ua      : {'OK' if UA_GEN else 'NOT AVAILABLE'}")
        self.logger.info(f"CWD          : {os.getcwd()}")
        self.logger.info(sep)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warn(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    def exception(self, msg: str):
        self.logger.exception(msg)

    def log_request(self, method: str, url: str, status: int = 0,
                    proxy_ip: str = "direct", impersonate: str = "none",
                    elapsed: float = 0, error: str = ""):
        if error:
            self.logger.error(
                f"REQ {method} | URL={url[:120]} | STATUS={status} | "
                f"PROXY={proxy_ip} | IMP={impersonate} | TIME={elapsed:.2f}s | ERROR={error[:200]}"
            )
        else:
            self.logger.info(
                f"REQ {method} | URL={url[:120]} | STATUS={status} | "
                f"PROXY={proxy_ip} | IMP={impersonate} | TIME={elapsed:.2f}s"
            )

    def log_dork(self, engine: str, dork: str, urls_found: int, error: str = ""):
        if error:
            self.logger.error(f"DORK [{engine}] query='{dork[:80]}' | URLS=0 | ERROR={error[:200]}")
        else:
            self.logger.info(f"DORK [{engine}] query='{dork[:80]}' | URLS={urls_found}")

    def log_analysis(self, url: str, confirmed: bool, category: str,
                     gateway_matches: list, error: str = ""):
        if error:
            self.logger.error(f"ANALYZE | URL={url[:100]} | ERROR={error[:200]}")
        else:
            status = "CONFIRMED" if confirmed else "UNCONFIRMED"
            self.logger.info(
                f"ANALYZE | URL={url[:100]} | STATUS={status} | "
                f"CAT={category} | MATCHES={gateway_matches}"
            )

    def log_filter(self, url: str, reason: str):
        self.logger.debug(f"FILTERED | URL={url[:100]} | REASON={reason}")

    def log_proxy(self, action: str, proxy_ip: str, detail: str = ""):
        self.logger.debug(f"PROXY {action} | IP={proxy_ip} | {detail}")

    def log_phase(self, phase: str, detail: str = ""):
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"PHASE: {phase} | {detail}")
        self.logger.info(f"{'=' * 60}")

    def log_scan_start(self, gateway_name: str, dorks: list, signatures: list, proxies: int):
        self.logger.info("=" * 80)
        self.logger.info(f"SCAN STARTED: {gateway_name}")
        self.logger.info(f"  Dorks ({len(dorks)}):")
        for i, d in enumerate(dorks, 1):
            self.logger.info(f"    [{i}] {d}")
        self.logger.info(f"  Signatures: {signatures}")
        self.logger.info(f"  Proxies: {proxies}")
        self.logger.info(f"  Threads: {MAX_THREADS}")
        self.logger.info(f"  Timeout: {REQUEST_TIMEOUT}s")
        self.logger.info("=" * 80)

    def log_scan_end(self, gateway_name: str, results: list, stats: dict, scan_time: float):
        confirmed = len([r for r in results if r.get("gateway_confirmed")])
        errors = len([r for r in results if r.get("status") == "ERROR"])
        real_stores = len([r for r in results if r.get("is_real_store")])
        self.logger.info("=" * 80)
        self.logger.info(f"SCAN COMPLETED: {gateway_name}")
        self.logger.info(f"  Total Results  : {len(results)}")
        self.logger.info(f"  Confirmed      : {confirmed}")
        self.logger.info(f"  Real Stores    : {real_stores}")
        self.logger.info(f"  Errors         : {errors}")
        self.logger.info(f"  Scan Time      : {scan_time:.1f}s")
        self.logger.info(f"  HTTP Stats     : {stats}")
        self.logger.info("=" * 80)

    def log_report(self, files: dict):
        self.logger.info("REPORTS GENERATED:")
        for fmt, path in files.items():
            try:
                size = os.path.getsize(path)
                self.logger.info(f"  {fmt.upper()}: {path} ({size:,} bytes)")
            except Exception:
                self.logger.error(f"  {fmt.upper()}: {path} (FILE ERROR)")

    def log_fingerprint(self, headers: dict):
        self.logger.debug(f"FINGERPRINT | UA={headers.get('User-Agent', 'N/A')[:80]}")
        self.logger.debug(f"FINGERPRINT | sec-ch-ua={headers.get('sec-ch-ua', 'N/A')}")
        self.logger.debug(f"FINGERPRINT | platform={headers.get('sec-ch-ua-platform', 'N/A')}")

    def log_store_validation(self, url: str, score: int, signals: list, is_store: bool):
        status = "REAL_STORE" if is_store else "NOT_STORE"
        self.logger.info(
            f"STORE_CHECK | URL={url[:100]} | STATUS={status} | "
            f"SCORE={score} | SIGNALS={signals[:10]}"
        )


# Instância global do logger
dlog = DebugLogger()

# ══════════════════════════════════════════════════════════════════
#                       CONSTANTES GLOBAIS
# ══════════════════════════════════════════════════════════════════

VERSION = "3.0.0"
CODENAME = "NETHUNTER SUPREME"
OUTPUT_DIR = "/sdcard/nh_files"
FALLBACK_OUTPUT = os.path.expanduser("~/gatehunter_output")
PROXIES_PATH_DEFAULT = "/sdcard/nh_files/proxies.txt"
PROXIES_PATH_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")

MAX_THREADS = 15
REQUEST_TIMEOUT = 20
DELAY_MIN = 1.5
DELAY_MAX = 4.0
MAX_RETRIES = 3
MAX_DORK_PAGES = 5
STORE_SCORE_THRESHOLD = 3  # Score mínimo para considerar loja real

# ── Cores ANSI ─────────────────────────────────────────────────
R = "\033[1;31m"
G = "\033[1;32m"
Y = "\033[1;33m"
B = "\033[1;34m"
M = "\033[1;35m"
C = "\033[1;36m"
W = "\033[1;37m"
D = "\033[0;90m"
RST = "\033[0m"
BOLD = "\033[1m"

# ══════════════════════════════════════════════════════════════════
#              BLACKLIST GLOBAL DE DOMÍNIOS (ANTI-LIXO)
# ══════════════════════════════════════════════════════════════════

GLOBAL_BLACKLIST_DOMAINS = {
    # Search engines
    "google.com", "google.com.br", "googleapis.com", "gstatic.com",
    "bing.com", "microsoft.com", "msn.com", "live.com",
    "duckduckgo.com", "yahoo.com", "yandex.com", "baidu.com",
    # Social media
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
    "youtube.com", "reddit.com", "pinterest.com", "tiktok.com",
    "whatsapp.com", "t.me", "telegram.org", "x.com",
    # Blogs / informativos / notícias
    "medium.com", "dev.to", "substack.com", "wordpress.com",
    "blogspot.com", "tumblr.com", "quora.com",
    # Reclamações / reviews
    "reclameaqui.com.br", "trustpilot.com", "glassdoor.com",
    "consumidor.gov.br",
    # Marketplaces (não são lojas que usam gateway)
    "amazon.com", "amazon.com.br", "mercadolivre.com.br",
    "aliexpress.com", "shopee.com.br", "magazineluiza.com.br",
    "americanas.com.br", "casasbahia.com.br", "submarino.com.br",
    # Plataformas / ferramentas
    "github.com", "gitlab.com", "stackoverflow.com", "npmjs.com",
    "pypi.org", "docker.com", "heroku.com", "vercel.app",
    "netlify.app", "cloudflare.com",
    # Wikis / referências
    "wikipedia.org", "w3.org", "mozilla.org",
    # Comparadores / informativos financeiros
    "idinheiro.com.br", "infomoney.com.br", "exame.com",
    "serasaexperian.com.br", "contaazul.com",
    "payproglobal.com", "goconverso.com",
    # Brave
    "brave.com", "bravesoftware.com",
}

# Domínios que são BLOGS/DOCS/INFO sobre gateways (não lojas)
INFORMATIONAL_PATTERNS = [
    "docs.", "blog.", "help.", "support.", "central.", "ajuda.",
    "materiais.", "atendimento.", "api.", "developer.", "dev.",
    "status.", "changelog.", "community.", "forum.",
    "learn.", "academy.", "hub.", "wiki.",
]

# ══════════════════════════════════════════════════════════════════
#                    GATEWAYS DE PAGAMENTO
# ══════════════════════════════════════════════════════════════════
#
# ESTRATÉGIA DE DORKS v3.0:
# - Dorks focam em encontrar LOJAS REAIS que usam a gateway
# - Excluem o site da própria gateway com -site:
# - Buscam por scripts JS, iframes, e checkout URLs no código
# - Combinam com termos de e-commerce (comprar, produto, carrinho)
# ══════════════════════════════════════════════════════════════════

GATEWAYS = {
    "1": {
        "name": "Asaas",
        "dorks": [
            '"checkout.asaas.com" -site:asaas.com -site:github.com',
            '"js.asaas.com" -site:asaas.com comprar produto',
            'inurl:checkout "asaas" comprar -site:asaas.com -blog -docs',
            '"asaas" carrinho comprar produto loja -site:asaas.com -site:reclameaqui.com.br',
            '"Powered by Asaas" OR "Pagamento via Asaas" -site:asaas.com',
            '"asaas.com" loja online produto comprar -site:asaas.com -site:youtube.com',
            'site:com.br "asaas" checkout produto adicionar carrinho',
            '"gateway" "asaas" ecommerce loja virtual produto',
        ],
        "signatures": ["checkout.asaas.com", "js.asaas.com", "api.asaas.com", "asaas.com/c/", "asaas.com/i/"],
        "own_domains": ["asaas.com"],
        "description": "Asaas - Plataforma de cobranças e pagamentos"
    },
    "2": {
        "name": "PagarMe",
        "dorks": [
            '"api.pagar.me" -site:pagar.me -site:stone.com.br comprar',
            '"pagar.me" checkout loja produto comprar -site:pagar.me -blog',
            'inurl:checkout "pagarme" OR "pagar.me" produto -site:pagar.me',
            '"Processado por Pagar.me" OR "Powered by Pagar.me"',
            '"pagar.me" carrinho comprar loja online -site:pagar.me -site:github.com',
            'site:com.br "pagar.me" produto adicionar carrinho',
            '"assets.pagar.me" OR "api.pagar.me" loja ecommerce',
        ],
        "signatures": ["api.pagar.me", "assets.pagar.me", "pagar.me/checkout", "pagarme"],
        "own_domains": ["pagar.me", "stone.com.br", "mundipagg.com"],
        "description": "Pagar.me (Stone) - Gateway de pagamentos"
    },
    "3": {
        "name": "Erede",
        "dorks": [
            '"userede.com.br" checkout loja comprar -site:userede.com.br',
            '"e.rede" pagamento loja produto -site:userede.com.br -blog',
            'inurl:checkout "erede" OR "userede" produto comprar',
            '"Rede Adquirencia" loja online ecommerce',
            '"userede" carrinho comprar -site:userede.com.br -site:itau.com.br',
        ],
        "signatures": ["userede.com.br", "e.rede.com.br", "api2.erede.com.br"],
        "own_domains": ["userede.com.br", "erede.com.br", "itau.com.br"],
        "description": "eRede (Itaú) - Adquirente e gateway"
    },
    "4": {
        "name": "PayFlow",
        "dorks": [
            '"payflow" checkout loja comprar produto -blog',
            '"payflow.com.br" pagamento loja online',
            '"payflow.global" checkout ecommerce',
            'inurl:checkout "payflow" produto comprar carrinho',
        ],
        "signatures": ["payflow.com.br", "payflow.global", "api.payflow"],
        "own_domains": ["payflow.com.br", "payflow.global"],
        "description": "PayFlow - Gateway de pagamentos digital"
    },
    "5": {
        "name": "AppMax",
        "dorks": [
            '"appmax.com.br" checkout comprar produto -site:appmax.com.br',
            '"api.appmax" loja pagamento -site:appmax.com.br',
            '"appmax" carrinho comprar loja -site:appmax.com.br -blog',
            'inurl:checkout "appmax" produto comprar',
        ],
        "signatures": ["appmax.com.br", "api.appmax.com.br", "checkout.appmax"],
        "own_domains": ["appmax.com.br"],
        "description": "AppMax - Plataforma de vendas e pagamentos"
    },
    "6": {
        "name": "MercadoPago",
        "dorks": [
            '"sdk.mercadopago" loja comprar produto -site:mercadopago.com -site:mercadolivre.com.br',
            '"mercadopago.com" checkout loja online produto -site:mercadopago.com -blog',
            '"Processado por Mercado Pago" comprar produto',
            'inurl:checkout "mercadopago" produto loja -site:mercadopago.com',
            'site:com.br "mercadopago" carrinho adicionar comprar produto',
        ],
        "signatures": ["sdk.mercadopago.com", "api.mercadopago.com", "mercadopago.com/checkout"],
        "own_domains": ["mercadopago.com", "mercadopago.com.br", "mercadolivre.com.br"],
        "description": "Mercado Pago - Gateway e carteira digital"
    },
    "7": {
        "name": "PagSeguro",
        "dorks": [
            '"pagseguro.uol.com.br" checkout loja comprar -site:pagseguro.uol.com.br',
            '"stc.pagseguro" OR "ws.pagseguro" loja produto -site:pagseguro.uol.com.br',
            '"PagBank" checkout loja produto comprar -site:pagbank.com.br -blog',
            'inurl:checkout "pagseguro" produto comprar carrinho',
            'site:com.br "pagseguro" carrinho adicionar produto comprar',
        ],
        "signatures": ["stc.pagseguro.uol.com.br", "ws.pagseguro.uol.com.br", "api.pagseguro", "pagbank"],
        "own_domains": ["pagseguro.uol.com.br", "pagbank.com.br", "uol.com.br"],
        "description": "PagSeguro/PagBank - Gateway de pagamentos"
    },
    "8": {
        "name": "Cielo",
        "dorks": [
            '"cieloecommerce" OR "api.cielo" loja comprar produto -site:cielo.com.br',
            '"cielo.com.br" checkout loja produto -site:cielo.com.br -blog',
            '"Cielo" checkout ecommerce loja online comprar -site:cielo.com.br',
            'inurl:checkout "cielo" produto comprar carrinho',
        ],
        "signatures": ["cieloecommerce.cielo.com.br", "api.cielo.com.br", "api2.cielo.com.br"],
        "own_domains": ["cielo.com.br"],
        "description": "Cielo - Maior adquirente do Brasil"
    },
    "9": {
        "name": "Stripe",
        "dorks": [
            '"js.stripe.com" site:com.br comprar produto loja',
            '"checkout.stripe.com" site:com.br loja produto',
            '"Powered by Stripe" site:com.br loja comprar',
            'site:com.br "stripe" checkout produto carrinho comprar',
        ],
        "signatures": ["js.stripe.com", "api.stripe.com", "checkout.stripe.com", "m.stripe.network"],
        "own_domains": ["stripe.com"],
        "description": "Stripe - Gateway global de pagamentos"
    },
    "10": {
        "name": "Hotmart",
        "dorks": [
            '"pay.hotmart.com" comprar curso -site:hotmart.com',
            '"hotmart" checkout comprar produto -site:hotmart.com -blog',
            'inurl:checkout "hotmart" comprar produto digital',
            '"Hotmart" pagamento curso produto -site:hotmart.com -site:youtube.com',
        ],
        "signatures": ["pay.hotmart.com", "api-hot-connect.hotmart.com", "hotmart.com/product/"],
        "own_domains": ["hotmart.com"],
        "description": "Hotmart - Plataforma de produtos digitais"
    },
    "11": {
        "name": "Eduzz",
        "dorks": [
            '"sun.eduzz.com" comprar curso -site:eduzz.com',
            '"eduzz" checkout comprar produto -site:eduzz.com -blog',
            '"Eduzz" pagamento produto digital -site:eduzz.com',
            'inurl:checkout "eduzz" comprar curso',
        ],
        "signatures": ["sun.eduzz.com", "api.eduzz.com", "eduzz.com/checkout"],
        "own_domains": ["eduzz.com"],
        "description": "Eduzz - Plataforma de infoprodutos"
    },
    "12": {
        "name": "Kiwify",
        "dorks": [
            '"pay.kiwify.com.br" comprar -site:kiwify.com.br',
            '"kiwify" checkout comprar produto -site:kiwify.com.br -blog',
            '"Kiwify" pagamento produto digital -site:kiwify.com.br',
            'inurl:checkout "kiwify" comprar curso',
        ],
        "signatures": ["pay.kiwify.com.br", "api.kiwify.com.br", "kiwify.com.br/checkout"],
        "own_domains": ["kiwify.com.br"],
        "description": "Kiwify - Plataforma de vendas digitais"
    },
    "13": {
        "name": "Vindi",
        "dorks": [
            '"api.vindi.com.br" loja assinatura -site:vindi.com.br',
            '"vindi" checkout pagamento loja -site:vindi.com.br -blog',
            '"Vindi" assinatura recorrente loja -site:vindi.com.br',
            'site:com.br "vindi" checkout comprar assinatura',
        ],
        "signatures": ["api.vindi.com.br", "app.vindi.com.br", "vindi.com.br/checkout"],
        "own_domains": ["vindi.com.br"],
        "description": "Vindi - Plataforma de pagamentos recorrentes"
    },
    "14": {
        "name": "Iugu",
        "dorks": [
            '"api.iugu.com" loja pagamento -site:iugu.com',
            '"iugu" checkout loja comprar -site:iugu.com -blog',
            '"alia.iugu.com" pagamento fatura -site:iugu.com',
            'site:com.br "iugu" checkout produto comprar',
        ],
        "signatures": ["api.iugu.com", "alia.iugu.com", "js.iugu.com", "iugu.com/invoices"],
        "own_domains": ["iugu.com"],
        "description": "Iugu - Gateway e plataforma financeira"
    },
    "15": {
        "name": "Getnet",
        "dorks": [
            '"api.getnet.com.br" loja comprar -site:getnet.com.br',
            '"getnet" checkout loja produto -site:getnet.com.br -blog',
            '"checkout.getnet" ecommerce loja -site:getnet.com.br',
            'site:com.br "getnet" checkout produto comprar carrinho',
        ],
        "signatures": ["api.getnet.com.br", "checkout.getnet.com.br", "getnetapi"],
        "own_domains": ["getnet.com.br", "santander.com.br"],
        "description": "Getnet (Santander) - Adquirente e gateway"
    },
    "0": {
        "name": "CUSTOM",
        "dorks": [],
        "signatures": [],
        "own_domains": [],
        "description": "Gateway personalizada (inserir manualmente)"
    },
}

# ── Categorias de sites para classificação ─────────────────────
SITE_CATEGORIES = {
    "loja_roupas": {
        "keywords": ["roupa", "moda", "camiseta", "vestido", "calça", "jeans", "blusa",
                      "fashion", "wear", "clothing", "look", "outfit", "estilo", "feminino",
                      "masculino", "plus size", "lingerie", "underwear", "íntima", "camisaria"],
        "label": "Loja de Roupas / Moda"
    },
    "loja_calcados": {
        "keywords": ["tênis", "tenis", "sapato", "calçado", "bota", "sandália", "chinelo",
                      "sneaker", "shoe", "footwear", "nike", "adidas", "sapatilha"],
        "label": "Loja de Calcados / Tenis"
    },
    "loja_eletronicos": {
        "keywords": ["eletrônico", "celular", "smartphone", "notebook", "computador",
                      "tablet", "fone", "headset", "tech", "tecnologia", "gadget",
                      "acessório", "informática", "hardware", "gamer", "console"],
        "label": "Loja de Eletronicos / Tecnologia"
    },
    "loja_cosmeticos": {
        "keywords": ["cosmético", "maquiagem", "perfume", "beleza", "skincare", "beauty",
                      "creme", "shampoo", "cabelo", "unha", "esmalte", "makeup"],
        "label": "Loja de Cosmeticos / Beleza"
    },
    "loja_suplementos": {
        "keywords": ["suplemento", "whey", "creatina", "proteína", "fitness", "academia",
                      "treino", "bodybuilding", "nutri", "vitamina", "bcaa"],
        "label": "Loja de Suplementos / Fitness"
    },
    "loja_moveis": {
        "keywords": ["móvel", "móveis", "sofá", "mesa", "cadeira", "decoração", "cama",
                      "colchão", "estante", "armário", "furniture", "decor"],
        "label": "Loja de Moveis / Decoracao"
    },
    "loja_pet": {
        "keywords": ["pet", "cachorro", "gato", "ração", "animal", "veterinário",
                      "petshop", "pet shop", "coleira", "brinquedo pet"],
        "label": "Pet Shop / Produtos para Animais"
    },
    "loja_alimentos": {
        "keywords": ["alimento", "comida", "gourmet", "orgânico", "café", "chocolate",
                      "doce", "saudável", "fit", "delivery", "restaurante", "food"],
        "label": "Loja de Alimentos / Food"
    },
    "curso_digital": {
        "keywords": ["curso", "aula", "treinamento", "mentoria", "ebook", "e-book",
                      "infoproduto", "digital", "online", "aprenda", "masterclass",
                      "workshop", "formação", "certificação"],
        "label": "Curso / Produto Digital"
    },
    "saas_software": {
        "keywords": ["software", "saas", "plataforma", "sistema", "app", "ferramenta",
                      "automação", "crm", "erp", "dashboard", "api", "cloud"],
        "label": "SaaS / Software"
    },
    "servico_profissional": {
        "keywords": ["consultoria", "serviço", "agência", "marketing", "design",
                      "desenvolvimento", "freelancer", "assessoria", "contabilidade"],
        "label": "Servico Profissional / Agencia"
    },
    "saude_bem_estar": {
        "keywords": ["saúde", "bem-estar", "terapia", "psicologia", "médico", "clínica",
                      "odontologia", "dentista", "estética", "spa", "yoga", "meditação"],
        "label": "Saude / Bem-Estar"
    },
    "assinatura_clube": {
        "keywords": ["assinatura", "clube", "box", "mensal", "plano", "recorrente",
                      "membership", "premium", "vip", "subscription"],
        "label": "Clube de Assinatura"
    },
    "loja_joias": {
        "keywords": ["joia", "jóia", "anel", "colar", "brinco", "pulseira", "prata",
                      "ouro", "semi-joia", "bijuteria"],
        "label": "Joalheria / Acessorios"
    },
    "loja_infantil": {
        "keywords": ["infantil", "bebê", "criança", "brinquedo", "kids", "baby",
                      "enxoval", "maternidade", "gestante"],
        "label": "Loja Infantil / Baby"
    },
    "educacao": {
        "keywords": ["escola", "faculdade", "universidade", "educação", "ensino",
                      "vestibular", "enem", "concurso", "preparatório"],
        "label": "Educacao / Ensino"
    },
    "automotivo": {
        "keywords": ["carro", "moto", "auto", "peça", "automotivo", "veículo",
                      "pneu", "acessório automotivo", "oficina"],
        "label": "Automotivo / Pecas"
    },
    "esporte": {
        "keywords": ["esporte", "futebol", "basquete", "corrida", "ciclismo",
                      "natação", "surf", "skate", "camping", "outdoor", "aventura"],
        "label": "Esportes / Outdoor"
    },
}

# ── User-Agents premium ───────────────────────────────────────
PREMIUM_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

IMPERSONATE_TARGETS = [
    "chrome120", "chrome119", "chrome116", "chrome110",
    "chrome107", "chrome104", "chrome101", "chrome100",
    "edge101", "edge99",
    "safari17_0", "safari15_5", "safari15_3",
]


# ══════════════════════════════════════════════════════════════════
#                     CLASSES AUXILIARES
# ══════════════════════════════════════════════════════════════════

class ProxyRotator:
    """Gerenciador de proxy rotativa com múltiplos gateways."""

    def __init__(self, proxy_file: str = None):
        self.proxies: List[Dict[str, str]] = []
        self.index = 0
        self.lock = threading.Lock()
        self.failed: Dict[str, int] = {}
        self._load_proxies(proxy_file)

    def _load_proxies(self, proxy_file: str = None):
        paths = [proxy_file, PROXIES_PATH_DEFAULT, PROXIES_PATH_FALLBACK]
        dlog.debug(f"PROXY_LOAD | Tentando caminhos: {paths}")
        for path in paths:
            if path and os.path.isfile(path):
                dlog.info(f"PROXY_LOAD | Arquivo encontrado: {path}")
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split(":")
                        if len(parts) == 4:
                            ip, port, user, passwd = parts
                            proxy_url = f"http://{user}:{passwd}@{ip}:{port}"
                            self.proxies.append({
                                "http": proxy_url, "https": proxy_url,
                                "raw": line, "ip": ip,
                            })
                            dlog.debug(f"PROXY_LOAD | Adicionado: {ip}:{port} (autenticado)")
                        elif len(parts) == 2:
                            ip, port = parts
                            proxy_url = f"http://{ip}:{port}"
                            self.proxies.append({
                                "http": proxy_url, "https": proxy_url,
                                "raw": line, "ip": ip,
                            })
                            dlog.debug(f"PROXY_LOAD | Adicionado: {ip}:{port} (aberto)")
                if self.proxies:
                    dlog.info(f"PROXY_LOAD | Total carregadas: {len(self.proxies)}")
                    break
        if not self.proxies:
            dlog.warn("PROXY_LOAD | Nenhuma proxy carregada! Usando conexao direta.")

    def get_random(self) -> Optional[Dict[str, str]]:
        if not self.proxies:
            return None
        with self.lock:
            available = [p for p in self.proxies if self.failed.get(p["ip"], 0) < 5]
            if not available:
                self.failed.clear()
                available = self.proxies
            return random.choice(available)

    def mark_failed(self, proxy: Dict[str, str]):
        with self.lock:
            self.failed[proxy.get("ip", "")] = self.failed.get(proxy.get("ip", ""), 0) + 1
            dlog.log_proxy("FAILED", proxy.get("ip", ""), f"count={self.failed.get(proxy.get('ip', ''), 0)}")

    def mark_success(self, proxy: Dict[str, str]):
        with self.lock:
            self.failed.pop(proxy.get("ip", ""), None)

    @property
    def count(self) -> int:
        return len(self.proxies)


class FingerprintGenerator:
    """Gera fingerprints realistas para evasão de detecção."""

    ACCEPT_LANGUAGES = [
        "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "pt-BR,pt;q=0.9,en;q=0.8",
        "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    ]

    @classmethod
    def generate(cls) -> Dict[str, str]:
        ua = cls._get_ua()
        chrome_ver = random.choice(["120", "121", "122", "123"])
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(cls.ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": random.choice(["none", "cross-site"]),
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not(A:Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
        }
        referers = ["https://www.google.com/", "https://www.google.com.br/", ""]
        ref = random.choice(referers)
        if ref:
            headers["Referer"] = ref
        dlog.log_fingerprint(headers)
        return headers

    @classmethod
    def _get_ua(cls) -> str:
        if UA_GEN:
            try:
                return UA_GEN.random
            except Exception:
                pass
        return random.choice(PREMIUM_USER_AGENTS)


class SmartRequester:
    """Engine de requisições inteligente com curl_cffi impersonate + fallback."""

    def __init__(self, proxy_rotator: ProxyRotator):
        self.proxy_rotator = proxy_rotator
        self.stats = {"requests": 0, "success": 0, "failed": 0, "blocked": 0}
        self.lock = threading.Lock()

    def get(self, url: str, use_proxy: bool = True, timeout: int = REQUEST_TIMEOUT) -> Optional[Any]:
        """GET com fallback: curl_cffi → urllib."""
        dlog.debug(f"REQUEST START | URL={url[:120]} | use_proxy={use_proxy}")
        for attempt in range(MAX_RETRIES):
            proxy = self.proxy_rotator.get_random() if use_proxy else None
            proxy_ip = proxy.get("ip", "N/A") if proxy else "direct"
            headers = FingerprintGenerator.generate()

            # ── curl_cffi com impersonate ────────────────────────────
            if CFFI_OK:
                imp = random.choice(IMPERSONATE_TARGETS)
                try:
                    proxies = proxy if proxy else None
                    t0 = time.time()
                    resp = cffi_requests.get(
                        url, headers=headers, impersonate=imp,
                        timeout=timeout, proxies=proxies,
                        allow_redirects=True, verify=False,
                    )
                    elapsed = time.time() - t0
                    with self.lock:
                        self.stats["requests"] += 1
                    if resp.status_code == 200:
                        if proxy:
                            self.proxy_rotator.mark_success(proxy)
                        with self.lock:
                            self.stats["success"] += 1
                        dlog.log_request("GET", url, resp.status_code, proxy_ip, imp, elapsed)
                        return resp
                    elif resp.status_code == 429:
                        with self.lock:
                            self.stats["blocked"] += 1
                        if proxy:
                            self.proxy_rotator.mark_failed(proxy)
                        dlog.log_request("GET", url, 429, proxy_ip, imp, elapsed, "RATE_LIMITED")
                        time.sleep(random.uniform(5, 15))
                        continue
                    elif resp.status_code in (403, 503):
                        with self.lock:
                            self.stats["blocked"] += 1
                        dlog.log_request("GET", url, resp.status_code, proxy_ip, imp, elapsed, f"BLOCKED_{resp.status_code}")
                        time.sleep(random.uniform(3, 8))
                        continue
                    else:
                        with self.lock:
                            self.stats["failed"] += 1
                        dlog.log_request("GET", url, resp.status_code, proxy_ip, imp, elapsed, f"HTTP_{resp.status_code}")
                        continue
                except Exception as e:
                    dlog.log_request("GET", url, 0, proxy_ip, imp, 0, f"EXCEPTION: {str(e)[:150]}")
                    if proxy:
                        self.proxy_rotator.mark_failed(proxy)

            # ── urllib fallback ─────────────────────────────
            dlog.debug(f"URLLIB FALLBACK | URL={url[:80]}")
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers=headers)
                opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
                t0 = time.time()
                with opener.open(req, timeout=timeout) as response:
                    data = response.read()
                    elapsed = time.time() - t0
                    with self.lock:
                        self.stats["requests"] += 1
                        self.stats["success"] += 1
                    dlog.log_request("GET-URLLIB", url, response.status, "direct", "urllib", elapsed)

                    class FakeResp:
                        def __init__(self, d, c, u):
                            self.text = d.decode("utf-8", errors="ignore")
                            self.status_code = c
                            self.url = u
                            self.content = d
                    return FakeResp(data, response.status, response.url)
            except Exception as e:
                dlog.log_request("GET-URLLIB", url, 0, "direct", "urllib", 0, f"EXCEPTION: {str(e)[:150]}")
                with self.lock:
                    self.stats["requests"] += 1
                    self.stats["failed"] += 1

            delay = random.uniform(DELAY_MIN * (attempt + 1), DELAY_MAX * (attempt + 1))
            dlog.debug(f"REQUEST RETRY DELAY | {delay:.1f}s before attempt {attempt+2}")
            time.sleep(delay)
        dlog.warn(f"REQUEST FAILED ALL RETRIES | URL={url[:120]}")
        return None


# ══════════════════════════════════════════════════════════════════
#                     MOTOR DE BUSCA (DORKS)
# ══════════════════════════════════════════════════════════════════

class DorkEngine:
    """Motor de busca via dorks com filtro anti-lixo inteligente."""

    def __init__(self, requester: SmartRequester, gateway_own_domains: List[str] = None):
        self.requester = requester
        self.found_urls: set = set()
        self.lock = threading.Lock()
        # Domínios da própria gateway (para excluir)
        self.gateway_own_domains = set(gateway_own_domains or [])

    def set_gateway_domains(self, domains: List[str]):
        """Define os domínios da gateway para excluir."""
        self.gateway_own_domains = set(d.lower() for d in domains)
        dlog.info(f"DORK_ENGINE | Gateway own domains set: {self.gateway_own_domains}")

    def search_duckduckgo(self, dork: str) -> List[str]:
        """Busca no DuckDuckGo HTML."""
        urls = []
        query = urllib.parse.quote_plus(dork)
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        dlog.debug(f"DDG SEARCH | query='{dork[:80]}' | url={search_url[:120]}")

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        resp = self.requester.get(search_url, use_proxy=True)
        if not resp:
            dlog.log_dork("DDG", dork, 0, "No response")
            return urls

        html = resp.text

        # Extrair via uddg redirect
        uddg_urls = re.findall(r'uddg=(https?[^&"\']+)', html)
        for raw_url in uddg_urls:
            clean = urllib.parse.unquote(raw_url).strip()
            clean = self._clean_url(clean)
            if clean and self._is_valid_url(clean):
                with self.lock:
                    if clean not in self.found_urls:
                        self.found_urls.add(clean)
                        urls.append(clean)
                        dlog.debug(f"DDG FOUND | {clean[:120]}")

        # Extrair via href result__a
        href_urls = re.findall(r'class="result__a"[^>]*href="([^"]+)"', html)
        for raw_url in href_urls:
            if "uddg=" in raw_url:
                match = re.search(r'uddg=(https?[^&"\']+)', raw_url)
                if match:
                    clean = urllib.parse.unquote(match.group(1)).strip()
                    clean = self._clean_url(clean)
                    if clean and self._is_valid_url(clean):
                        with self.lock:
                            if clean not in self.found_urls:
                                self.found_urls.add(clean)
                                urls.append(clean)

        dlog.log_dork("DDG", dork, len(urls))
        return urls

    def search_google(self, dork: str, max_pages: int = 3) -> List[str]:
        """Busca no Google."""
        urls = []
        query = urllib.parse.quote_plus(dork)
        dlog.debug(f"GOOGLE SEARCH | query='{dork[:80]}' | pages={max_pages}")

        for page in range(max_pages):
            start = page * 10
            search_url = f"https://www.google.com/search?q={query}&start={start}&num=20&hl=pt-BR&gl=br"

            time.sleep(random.uniform(DELAY_MIN + 1, DELAY_MAX + 2))
            resp = self.requester.get(search_url, use_proxy=True)
            if not resp:
                continue

            html = resp.text

            # Método 1: /url?q= redirect
            g_urls = re.findall(r'/url\?q=(https?://[^&"]+)', html)
            for raw_url in g_urls:
                clean = urllib.parse.unquote(raw_url).strip()
                clean = self._clean_url(clean)
                if clean and self._is_valid_url(clean):
                    with self.lock:
                        if clean not in self.found_urls:
                            self.found_urls.add(clean)
                            urls.append(clean)

            # Método 2: data-href
            d_urls = re.findall(r'data-href="(https?://[^"]+)"', html)
            for raw_url in d_urls:
                clean = self._clean_url(raw_url)
                if clean and self._is_valid_url(clean):
                    with self.lock:
                        if clean not in self.found_urls:
                            self.found_urls.add(clean)
                            urls.append(clean)

            # Método 3: cite tags
            c_urls = re.findall(r'<cite[^>]*>(https?://[^<]+)</cite>', html)
            for raw_url in c_urls:
                clean = self._clean_url(raw_url)
                if clean and self._is_valid_url(clean):
                    with self.lock:
                        if clean not in self.found_urls:
                            self.found_urls.add(clean)
                            urls.append(clean)

        dlog.log_dork("GOOGLE", dork, len(urls))
        return urls

    def search_bing(self, dork: str, max_pages: int = 2) -> List[str]:
        """Busca no Bing."""
        urls = []
        query = urllib.parse.quote_plus(dork)
        dlog.debug(f"BING SEARCH | query='{dork[:80]}' | pages={max_pages}")

        for page in range(max_pages):
            first = page * 10 + 1
            search_url = f"https://www.bing.com/search?q={query}&first={first}&count=20"

            time.sleep(random.uniform(DELAY_MIN + 1, DELAY_MAX + 2))
            resp = self.requester.get(search_url, use_proxy=True)
            if not resp:
                continue

            html = resp.text
            if "captcha" in html.lower() or not ("b_results" in html or "b_algo" in html):
                dlog.warn(f"BING BLOCKED | page={page} | Captcha or no results")
                continue

            # Extrair URLs dos resultados do Bing
            bing_hrefs = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>', html)
            for raw_url in bing_hrefs:
                clean = self._clean_url(raw_url)
                if clean and self._is_valid_url(clean):
                    with self.lock:
                        if clean not in self.found_urls:
                            self.found_urls.add(clean)
                            urls.append(clean)

        dlog.log_dork("BING", dork, len(urls))
        return urls

    def search_all_engines(self, dork: str) -> List[str]:
        """Busca em todos os engines disponíveis."""
        all_urls = []
        dlog.info(f"MULTI-ENGINE SEARCH | dork='{dork[:80]}'")

        # DuckDuckGo (principal)
        try:
            ddg = self.search_duckduckgo(dork)
            all_urls.extend(ddg)
            dlog.info(f"DDG COMPLETE | {len(ddg)} URLs")
        except Exception as e:
            dlog.error(f"DDG EXCEPTION | {str(e)[:150]}")

        time.sleep(random.uniform(2, 4))

        # Google
        try:
            google = self.search_google(dork, max_pages=2)
            all_urls.extend(google)
            dlog.info(f"GOOGLE COMPLETE | {len(google)} URLs")
        except Exception as e:
            dlog.error(f"GOOGLE EXCEPTION | {str(e)[:150]}")

        time.sleep(random.uniform(2, 4))

        # Bing
        try:
            bing = self.search_bing(dork, max_pages=1)
            all_urls.extend(bing)
            dlog.info(f"BING COMPLETE | {len(bing)} URLs")
        except Exception as e:
            dlog.error(f"BING EXCEPTION | {str(e)[:150]}")

        unique = list(set(all_urls))
        dlog.info(f"MULTI-ENGINE TOTAL | raw={len(all_urls)} | unique={len(unique)}")
        return unique

    def _clean_url(self, url: str) -> Optional[str]:
        """Limpa e normaliza URL."""
        if not url:
            return None
        url = url.strip().rstrip("/").rstrip(")")
        url = re.sub(r'["\'>].*$', '', url)
        url = re.sub(r'&amp;.*$', '', url)
        url = re.sub(r'%25.*$', '', url)
        if not url.startswith("http"):
            return None
        if len(url) < 10 or len(url) > 500:
            return None
        return url

    def _is_valid_url(self, url: str) -> bool:
        """Verifica se URL é válida e não está na blacklist."""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                dlog.log_filter(url, "empty_domain")
                return False

            # 1. Blacklist global
            for blocked in GLOBAL_BLACKLIST_DOMAINS:
                if blocked in domain:
                    dlog.log_filter(url, f"global_blacklist:{blocked}")
                    return False

            # 2. Domínios da própria gateway
            for own in self.gateway_own_domains:
                if own in domain:
                    dlog.log_filter(url, f"gateway_own_domain:{own}")
                    return False

            # 3. Subdomínios informativos (docs, blog, help, etc)
            for pattern in INFORMATIONAL_PATTERNS:
                if domain.startswith(pattern):
                    dlog.log_filter(url, f"informational_subdomain:{pattern}")
                    return False

            # 4. URLs que são claramente não-lojas
            path_lower = parsed.path.lower()
            bad_paths = ["/blog", "/docs", "/help", "/support", "/api/",
                         "/developer", "/changelog", "/status", "/terms",
                         "/privacy", "/about", "/careers", "/press",
                         "/wiki", "/forum", "/community"]
            for bp in bad_paths:
                if path_lower.startswith(bp):
                    dlog.log_filter(url, f"bad_path:{bp}")
                    return False

            return True
        except Exception:
            return False


# ══════════════════════════════════════════════════════════════════
#                   ANALISADOR DE SITES (v3.0)
# ══════════════════════════════════════════════════════════════════

class SiteAnalyzer:
    """Analisa e classifica sites com validação rigorosa de loja real."""

    # Sinais que indicam que é uma LOJA REAL / E-COMMERCE
    STORE_SIGNALS = {
        # Elementos de carrinho/compra (peso 3 cada)
        "high": [
            "adicionar ao carrinho", "add to cart", "comprar agora",
            "buy now", "finalizar compra", "checkout", "carrinho de compras",
            "shopping cart", "sacola de compras", "meu carrinho",
            "adicionar à sacola", "comprar", "add-to-cart",
            "btn-comprar", "botao-comprar", "btn_buy",
            "wc-add-to-cart", "product-add-to-cart",
        ],
        # Elementos de produto/preço (peso 2 cada)
        "medium": [
            "r$", "preço", "price", "valor", "parcela", "à vista",
            "frete grátis", "frete", "cep", "calcular frete",
            "produto", "product", "estoque", "disponível",
            "tamanho", "cor", "quantidade", "unidade",
            "promoção", "desconto", "oferta", "sale",
            "categoria", "departamento", "vitrine",
            "lista de desejos", "wishlist", "favoritos",
        ],
        # Plataformas e-commerce (peso 4 cada)
        "platform": [
            "woocommerce", "shopify", "vtex", "magento",
            "nuvemshop", "tiendanube", "tray.com.br",
            "lojaintegrada", "yampi", "cartpanda",
            "opencart", "prestashop", "loja virtual",
        ],
        # Elementos de pagamento/checkout (peso 2 cada)
        "payment": [
            "forma de pagamento", "método de pagamento",
            "cartão de crédito", "boleto", "pix",
            "parcelamento", "parcelas sem juros",
            "pagamento seguro", "ssl", "compra segura",
            "payment method", "credit card",
        ],
    }

    # Sinais NEGATIVOS que indicam que NÃO é loja
    NOT_STORE_SIGNALS = [
        "documentação", "documentation", "api reference",
        "getting started", "developer guide", "sdk",
        "changelog", "release notes", "status page",
        "blog post", "artigo", "notícia", "news",
        "reclame aqui", "reclamação", "complaint",
        "tutorial", "how to", "como usar",
        "termos de uso", "política de privacidade",
        "vagas", "careers", "trabalhe conosco",
        "sobre nós", "about us", "quem somos",
        "central de ajuda", "help center", "faq",
        "comparativo", "review", "análise",
    ]

    def __init__(self, requester: SmartRequester, gateway_signatures: List[str],
                 gateway_own_domains: List[str] = None):
        self.requester = requester
        self.gateway_signatures = [s.lower() for s in gateway_signatures]
        self.gateway_own_domains = set(d.lower() for d in (gateway_own_domains or []))

    def analyze(self, url: str) -> Optional[Dict[str, Any]]:
        """Analisa um site com validação rigorosa."""
        dlog.debug(f"ANALYZE START | URL={url[:120]}")
        try:
            # Verificar domínio antes de fazer request
            domain = urllib.parse.urlparse(url).netloc.lower()

            # Filtrar domínios da própria gateway
            for own in self.gateway_own_domains:
                if own in domain:
                    dlog.log_filter(url, f"analyze_own_domain:{own}")
                    return None

            resp = self.requester.get(url, use_proxy=True, timeout=15)
            if not resp:
                dlog.log_analysis(url, False, "N/A", [], "Timeout ou sem resposta")
                return None  # Não retorna erro, simplesmente ignora

            html = resp.text if hasattr(resp, "text") else ""
            if len(html) < 500:
                dlog.log_filter(url, "html_too_small")
                return None

            html_lower = html.lower()

            # ── Verificar gateway no HTML ──────────────────
            gateway_found = False
            gateway_matches = []
            for sig in self.gateway_signatures:
                # Busca mais rigorosa: procura em scripts, iframes, links
                patterns = [
                    f'src="[^"]*{re.escape(sig)}[^"]*"',
                    f"src='[^']*{re.escape(sig)}[^']*'",
                    f'href="[^"]*{re.escape(sig)}[^"]*"',
                    f'action="[^"]*{re.escape(sig)}[^"]*"',
                    f'data-[^=]*="[^"]*{re.escape(sig)}[^"]*"',
                ]
                # Primeiro tenta match rigoroso (em atributos HTML)
                for pat in patterns:
                    if re.search(pat, html_lower):
                        gateway_found = True
                        if sig not in gateway_matches:
                            gateway_matches.append(sig)
                        break

                # Se não achou em atributos, busca no texto geral
                if not gateway_found and sig in html_lower:
                    # Verifica se não é apenas menção textual
                    # Conta ocorrências - se aparece mais de 1x provavelmente é integrado
                    count = html_lower.count(sig)
                    if count >= 2:
                        gateway_found = True
                        if sig not in gateway_matches:
                            gateway_matches.append(sig)

            # ── Validação de LOJA REAL ──────────────────────
            store_score, store_signals = self._calculate_store_score(html_lower)
            is_real_store = store_score >= STORE_SCORE_THRESHOLD

            dlog.log_store_validation(url, store_score, store_signals, is_real_store)

            # Se não é loja real E não tem gateway confirmada, ignora
            if not gateway_found and not is_real_store:
                dlog.log_filter(url, f"not_store_no_gateway (score={store_score})")
                return None

            # ── Extrair metadados ──────────────────────────
            title = self._extract_tag(html, "title")
            description = self._extract_meta(html, "description")
            keywords = self._extract_meta(html, "keywords")
            og_title = self._extract_meta_property(html, "og:title")
            og_desc = self._extract_meta_property(html, "og:description")
            og_image = self._extract_meta_property(html, "og:image")
            og_type = self._extract_meta_property(html, "og:type")

            # ── Classificar ────────────────────────────────
            category = self._classify_site(title, description, keywords, html_lower)
            technologies = self._detect_technologies(html_lower)
            other_gateways = self._detect_all_gateways(html_lower)
            ecommerce_platform = self._detect_ecommerce_platform(html_lower)

            # ── Extrair contatos ───────────────────────────
            emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)))[:5]
            phones = list(set(re.findall(r'(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}', html)))[:5]
            # Filtrar emails genéricos
            emails = [e for e in emails if not any(x in e.lower() for x in
                      ["@example", "@test", "@sentry", "@wixpress", "noreply", "no-reply"])]

            result = {
                "url": url,
                "domain": domain,
                "title": title or og_title or "N/A",
                "description": description or og_desc or "N/A",
                "keywords": keywords or "N/A",
                "category": category,
                "gateway_confirmed": gateway_found,
                "gateway_matches": gateway_matches,
                "other_gateways": other_gateways,
                "ecommerce_platform": ecommerce_platform,
                "technologies": technologies,
                "has_ssl": url.startswith("https"),
                "emails": emails,
                "phones": phones,
                "og_image": og_image or "N/A",
                "og_type": og_type or "N/A",
                "html_size": len(html),
                "store_score": store_score,
                "store_signals": store_signals[:10],
                "is_real_store": is_real_store,
                "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONFIRMED" if gateway_found else ("POSSIBLE" if is_real_store else "UNCONFIRMED"),
            }

            dlog.log_analysis(url, gateway_found, category, gateway_matches)
            dlog.debug(
                f"ANALYZE DETAIL | domain={domain} | title={title[:60] if title else 'N/A'} | "
                f"platform={ecommerce_platform} | store_score={store_score} | "
                f"is_store={is_real_store} | gateway={gateway_found} | "
                f"techs={technologies[:5]} | emails={len(emails)}"
            )
            return result

        except Exception as e:
            dlog.log_analysis(url, False, "ERROR", [], f"EXCEPTION: {str(e)[:200]}")
            dlog.exception(f"ANALYZE EXCEPTION | URL={url[:100]}")
            return None

    def _calculate_store_score(self, html_lower: str) -> Tuple[int, List[str]]:
        """Calcula score de probabilidade de ser loja real."""
        score = 0
        signals = []

        # Sinais negativos (penalizam)
        for neg in self.NOT_STORE_SIGNALS:
            if neg in html_lower:
                score -= 2
                signals.append(f"-{neg}")

        # Sinais positivos HIGH (peso 3)
        for sig in self.STORE_SIGNALS["high"]:
            if sig in html_lower:
                score += 3
                signals.append(f"+HIGH:{sig}")

        # Sinais positivos MEDIUM (peso 2)
        for sig in self.STORE_SIGNALS["medium"]:
            if sig in html_lower:
                score += 2
                signals.append(f"+MED:{sig}")

        # Sinais de plataforma (peso 4)
        for sig in self.STORE_SIGNALS["platform"]:
            if sig in html_lower:
                score += 4
                signals.append(f"+PLAT:{sig}")

        # Sinais de pagamento (peso 2)
        for sig in self.STORE_SIGNALS["payment"]:
            if sig in html_lower:
                score += 2
                signals.append(f"+PAY:{sig}")

        # Bonus: se tem muitos produtos (padrão de preço R$)
        price_count = len(re.findall(r'r\$\s*\d+', html_lower))
        if price_count >= 3:
            score += 3
            signals.append(f"+PRICES:{price_count}")
        elif price_count >= 1:
            score += 1
            signals.append(f"+PRICE:{price_count}")

        # Bonus: se tem imagens de produto
        img_count = len(re.findall(r'<img[^>]+(?:product|produto|item|thumb)', html_lower))
        if img_count >= 2:
            score += 2
            signals.append(f"+PROD_IMGS:{img_count}")

        return score, signals

    @staticmethod
    def _extract_tag(html: str, tag: str) -> str:
        match = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', html, re.IGNORECASE | re.DOTALL)
        if match:
            text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            return re.sub(r'\s+', ' ', text)[:200]
        return ""

    @staticmethod
    def _extract_meta(html: str, name: str) -> str:
        for pattern in [
            rf'<meta[^>]+name=["\']?{name}["\']?[^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']?{name}["\']?',
        ]:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:300]
        return ""

    @staticmethod
    def _extract_meta_property(html: str, prop: str) -> str:
        for pattern in [
            rf'<meta[^>]+property=["\']?{re.escape(prop)}["\']?[^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']?{re.escape(prop)}["\']?',
        ]:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:300]
        return ""

    @staticmethod
    def _classify_site(title: str, description: str, keywords: str, html_lower: str) -> str:
        text = f"{title} {description} {keywords}".lower()
        scores = {}
        for cat_key, cat_data in SITE_CATEGORIES.items():
            score = sum(3 for kw in cat_data["keywords"] if kw in text)
            # Busca mais limitada no HTML (apenas primeiros 10k chars para performance)
            html_sample = html_lower[:10000]
            score += sum(1 for kw in cat_data["keywords"] if kw in html_sample)
            if score > 0:
                scores[cat_key] = score
        if scores:
            best = max(scores, key=scores.get)
            if scores[best] >= 2:
                return SITE_CATEGORIES[best]["label"]
        return "Loja / E-commerce (Geral)"

    @staticmethod
    def _detect_technologies(html_lower: str) -> List[str]:
        techs = []
        tech_map = {
            "wordpress": "WordPress", "wp-content": "WordPress",
            "woocommerce": "WooCommerce", "shopify": "Shopify",
            "magento": "Magento", "prestashop": "PrestaShop",
            "opencart": "OpenCart", "vtex": "VTEX",
            "nuvemshop": "Nuvemshop", "tray.com.br": "Tray",
            "lojaintegrada": "Loja Integrada", "wix.com": "Wix",
            "squarespace": "Squarespace", "react": "React",
            "next.js": "Next.js", "nuxt": "Nuxt.js",
            "laravel": "Laravel", "bootstrap": "Bootstrap",
            "tailwind": "Tailwind CSS", "jquery": "jQuery",
            "cloudflare": "Cloudflare", "gtm.js": "Google Tag Manager",
            "gtag": "Google Analytics", "fbq(": "Facebook Pixel",
            "hotjar": "Hotjar", "recaptcha": "reCAPTCHA",
        }
        for key, name in tech_map.items():
            if key in html_lower and name not in techs:
                techs.append(name)
        return techs

    @staticmethod
    def _detect_all_gateways(html_lower: str) -> List[str]:
        found = []
        sigs = {
            "Asaas": ["checkout.asaas.com", "js.asaas.com", "api.asaas.com"],
            "PagarMe": ["api.pagar.me", "assets.pagar.me"],
            "eRede": ["userede.com.br", "e.rede.com.br"],
            "MercadoPago": ["sdk.mercadopago.com", "api.mercadopago.com"],
            "PagSeguro": ["stc.pagseguro.uol", "ws.pagseguro"],
            "Cielo": ["cieloecommerce.cielo", "api.cielo.com.br"],
            "Stripe": ["js.stripe.com", "api.stripe.com"],
            "PayPal": ["paypal.com/sdk", "paypalobjects.com"],
            "Getnet": ["api.getnet.com.br", "checkout.getnet"],
            "Iugu": ["api.iugu.com", "js.iugu.com"],
            "Vindi": ["api.vindi.com.br", "app.vindi.com.br"],
            "AppMax": ["appmax.com.br"],
            "Hotmart": ["pay.hotmart.com"],
            "Eduzz": ["sun.eduzz.com"],
            "Kiwify": ["pay.kiwify.com.br"],
        }
        for gw, gs in sigs.items():
            if any(s in html_lower for s in gs) and gw not in found:
                found.append(gw)
        return found

    @staticmethod
    def _detect_ecommerce_platform(html_lower: str) -> str:
        platforms = {
            "WooCommerce": ["woocommerce", "wc-cart", "wc-add-to-cart"],
            "Shopify": ["cdn.shopify.com", "shopify.com/s/"],
            "VTEX": ["vtex.com", "vteximg.com", "vtexcommerce"],
            "Magento": ["magento", "mage/cookies"],
            "Nuvemshop": ["nuvemshop", "tiendanube"],
            "Tray": ["tray.com.br", "traycorp"],
            "Loja Integrada": ["lojaintegrada"],
            "PrestaShop": ["prestashop"],
            "OpenCart": ["opencart"],
            "Wix": ["wix.com/", "parastorage.com"],
            "Yampi": ["yampi.com.br", "yampi.io"],
            "Cartpanda": ["cartpanda"],
            "Bagy": ["bagy.com.br"],
            "Dooca": ["dooca.com.br"],
        }
        for name, sigs in platforms.items():
            if any(s in html_lower for s in sigs):
                return name
        return "Desconhecida"



# ══════════════════════════════════════════════════════════════════
#                    RELATÓRIO & EXPORTAÇÃO
# ══════════════════════════════════════════════════════════════════

class ReportGenerator:
    """Gera relatórios ultra detalhados."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_full_report(self, gateway_name: str, results: List[Dict],
                              stats: Dict, scan_time: float) -> Dict[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', gateway_name.lower())
        files = {}

        txt_path = os.path.join(self.output_dir, f"gatehunter_{safe_name}_{timestamp}.txt")
        self._write_txt(txt_path, gateway_name, results, stats, scan_time)
        files["txt"] = txt_path

        json_path = os.path.join(self.output_dir, f"gatehunter_{safe_name}_{timestamp}.json")
        self._write_json(json_path, gateway_name, results, stats, scan_time)
        files["json"] = json_path

        urls_path = os.path.join(self.output_dir, f"gatehunter_{safe_name}_urls_{timestamp}.txt")
        self._write_urls(urls_path, results)
        files["urls"] = urls_path

        confirmed_path = os.path.join(self.output_dir, f"gatehunter_{safe_name}_confirmed_{timestamp}.txt")
        self._write_confirmed(confirmed_path, results)
        files["confirmed"] = confirmed_path

        stores_path = os.path.join(self.output_dir, f"gatehunter_{safe_name}_stores_{timestamp}.txt")
        self._write_stores_only(stores_path, results)
        files["stores"] = stores_path

        return files

    def _write_txt(self, path, gw_name, results, stats, scan_time):
        confirmed = [r for r in results if r.get("gateway_confirmed")]
        stores = [r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")]
        unconfirmed = [r for r in results if not r.get("gateway_confirmed") and r.get("status") != "ERROR"]
        errors = [r for r in results if r.get("status") == "ERROR"]

        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("     GATEHUNTER v3.0 - NETHUNTER SUPREME EDITION - RELATORIO COMPLETO\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"  Gateway Alvo       : {gw_name}\n")
            f.write(f"  Data/Hora          : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"  Tempo de Scan      : {scan_time:.1f} segundos\n")
            f.write(f"  URLs Analisadas    : {len(results)}\n")
            f.write(f"  Gateway Confirmada : {len(confirmed)}\n")
            f.write(f"  Lojas Reais        : {len(stores)}\n")
            f.write(f"  Nao Confirmadas    : {len(unconfirmed)}\n")
            f.write(f"  Erros              : {len(errors)}\n")
            f.write(f"  Requests Total     : {stats.get('requests', 0)}\n")
            f.write(f"  Requests OK        : {stats.get('success', 0)}\n")
            f.write(f"  Requests Falha     : {stats.get('failed', 0)}\n")
            f.write(f"  Bloqueios (429)    : {stats.get('blocked', 0)}\n")

            # LOJAS REAIS CONFIRMADAS
            if stores:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"  LOJAS REAIS COM {gw_name.upper()} ({len(stores)})\n")
                f.write("=" * 80 + "\n\n")

                for i, s in enumerate(stores, 1):
                    f.write(f"  [{i:03d}] {'=' * 70}\n")
                    f.write(f"  URL              : {s.get('url', 'N/A')}\n")
                    f.write(f"  Dominio          : {s.get('domain', 'N/A')}\n")
                    f.write(f"  Titulo           : {s.get('title', 'N/A')}\n")
                    f.write(f"  Descricao        : {s.get('description', 'N/A')}\n")
                    f.write(f"  Categoria        : {s.get('category', 'N/A')}\n")
                    f.write(f"  Status           : LOJA REAL CONFIRMADA\n")
                    f.write(f"  Store Score      : {s.get('store_score', 0)}\n")
                    f.write(f"  Gateway Match    : {', '.join(s.get('gateway_matches', []))}\n")
                    f.write(f"  Outras Gates     : {', '.join(s.get('other_gateways', [])) or 'Nenhuma'}\n")
                    f.write(f"  Plataforma       : {s.get('ecommerce_platform', 'N/A')}\n")
                    f.write(f"  Tecnologias      : {', '.join(s.get('technologies', [])) or 'N/A'}\n")
                    f.write(f"  SSL              : {'Sim' if s.get('has_ssl') else 'Nao'}\n")
                    f.write(f"  Emails           : {', '.join(s.get('emails', [])) or 'N/A'}\n")
                    f.write(f"  Telefones        : {', '.join(s.get('phones', [])) or 'N/A'}\n")
                    f.write(f"  OG Image         : {s.get('og_image', 'N/A')}\n")
                    f.write(f"  HTML Size        : {s.get('html_size', 0):,} bytes\n")
                    f.write(f"  Analisado em     : {s.get('analyzed_at', 'N/A')}\n")
                    f.write(f"  Store Signals    : {', '.join(s.get('store_signals', [])[:5])}\n\n")

            # OUTROS CONFIRMADOS (não necessariamente lojas)
            other_confirmed = [r for r in confirmed if not r.get("is_real_store")]
            if other_confirmed:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"  OUTROS SITES COM {gw_name.upper()} - NAO CLASSIFICADOS COMO LOJA ({len(other_confirmed)})\n")
                f.write("=" * 80 + "\n\n")
                for i, s in enumerate(other_confirmed, 1):
                    f.write(f"  [{i:03d}] {s.get('url', 'N/A')}\n")
                    f.write(f"         {s.get('title', 'N/A')[:60]} | {s.get('category', 'N/A')} | Score={s.get('store_score', 0)}\n")

            # Estatísticas por categoria
            f.write("\n" + "=" * 80 + "\n")
            f.write("  ESTATISTICAS POR CATEGORIA (LOJAS REAIS)\n")
            f.write("=" * 80 + "\n\n")
            cat_count = {}
            for s in stores:
                cat = s.get("category", "Outros")
                cat_count[cat] = cat_count.get(cat, 0) + 1
            for cat, count in sorted(cat_count.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {cat:<40} : {count:>4} {'#' * min(count * 2, 40)}\n")

            # Estatísticas por plataforma
            f.write("\n" + "=" * 80 + "\n")
            f.write("  ESTATISTICAS POR PLATAFORMA E-COMMERCE\n")
            f.write("=" * 80 + "\n\n")
            plat_count = {}
            for s in stores:
                plat = s.get("ecommerce_platform", "Desconhecida")
                plat_count[plat] = plat_count.get(plat, 0) + 1
            for plat, count in sorted(plat_count.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {plat:<40} : {count:>4} {'#' * min(count * 2, 40)}\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("  FIM DO RELATORIO - GATEHUNTER v3.0 NETHUNTER SUPREME EDITION\n")
            f.write("=" * 80 + "\n")

    def _write_json(self, path, gw_name, results, stats, scan_time):
        stores = [r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")]
        report = {
            "tool": "GateHunter v3.0 - NetHunter Supreme Edition",
            "gateway": gw_name,
            "timestamp": datetime.now().isoformat(),
            "scan_time_seconds": round(scan_time, 1),
            "statistics": {
                "total_analyzed": len(results),
                "confirmed": len([r for r in results if r.get("gateway_confirmed")]),
                "real_stores": len(stores),
                "errors": len([r for r in results if r.get("status") == "ERROR"]),
                "requests": stats,
            },
            "real_stores": stores,
            "all_results": results,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def _write_urls(self, path, results):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# GateHunter v3.0 - Todas URLs - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(results)}\n\n")
            for r in results:
                status = r.get("status", "?")
                store = "LOJA" if r.get("is_real_store") else ""
                f.write(f"{r.get('url', '')} | {status} | {store} | {r.get('category', 'N/A')}\n")

    def _write_confirmed(self, path, results):
        confirmed = [r for r in results if r.get("gateway_confirmed")]
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# GateHunter v3.0 - CONFIRMADAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(confirmed)}\n\n")
            for r in confirmed:
                store_tag = "[LOJA]" if r.get("is_real_store") else "[OUTRO]"
                f.write(f"{store_tag} {r.get('url', '')} | {r.get('title', 'N/A')[:50]} | {r.get('category', 'N/A')}\n")

    def _write_stores_only(self, path, results):
        """Arquivo exclusivo com LOJAS REAIS apenas."""
        stores = [r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")]
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# GateHunter v3.0 - LOJAS REAIS CONFIRMADAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(stores)}\n")
            f.write(f"# Apenas sites com carrinho/produtos/precos reais detectados\n\n")
            for i, r in enumerate(stores, 1):
                f.write(f"[{i:03d}] {r.get('url', '')}\n")
                f.write(f"      Titulo    : {r.get('title', 'N/A')[:60]}\n")
                f.write(f"      Categoria : {r.get('category', 'N/A')}\n")
                f.write(f"      Plataforma: {r.get('ecommerce_platform', 'N/A')}\n")
                f.write(f"      Score     : {r.get('store_score', 0)}\n")
                f.write(f"      Emails    : {', '.join(r.get('emails', [])) or 'N/A'}\n")
                f.write(f"      Phones    : {', '.join(r.get('phones', [])) or 'N/A'}\n\n")


# ══════════════════════════════════════════════════════════════════
#                     INTERFACE DO TERMINAL
# ══════════════════════════════════════════════════════════════════

def print_banner():
    banner = f"""
{M}╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   {C}   ██████╗  █████╗ ████████╗███████╗                              {M}║
║   {C}  ██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝                              {M}║
║   {C}  ██║  ███╗███████║   ██║   █████╗                                {M}║
║   {C}  ██║   ██║██╔══██║   ██║   ██╔══╝                                {M}║
║   {C}  ╚██████╔╝██║  ██║   ██║   ███████╗                              {M}║
║   {C}   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝                              {M}║
║   {Y}  ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗             {M}║
║   {Y}  ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗            {M}║
║   {Y}  ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝            {M}║
║   {Y}  ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗            {M}║
║   {Y}  ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║            {M}║
║   {Y}  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝            {M}║
║                                                                      ║
║  {W}  v{VERSION} {D}// {C}NETHUNTER SUPREME EDITION{D} // {G}Payment Gateway OSINT  {M}║
║  {D}  ─────────────────────────────────────────────────────────────── {M}║
║  {W}  Engine  : {G}curl_cffi Impersonate + Multi-Thread + Proxy Pool  {M}  ║
║  {W}  Evasion : {G}TLS Fingerprint + Header Spoof + UA Rotation      {M}  ║
║  {W}  Search  : {G}DuckDuckGo + Google + Bing (Multi-Engine)         {M}  ║
║  {W}  Filter  : {G}Anti-Lixo + Store Validator + Domain Blacklist    {M}  ║
║  {W}  Output  : {G}/sdcard/nh_files/ (TXT + JSON + URLs + Stores)    {M}  ║
║  {W}  Debug   : {G}/sdcard/nh_files/gatehunter_debug.log             {M}  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝{RST}
"""
    print(banner)


def print_gateway_menu():
    print(f"\n{M}  ╔══════════════════════════════════════════════════════════════╗{RST}")
    print(f"{M}  ║  {W}SELECIONE A GATEWAY DE PAGAMENTO                          {M}║{RST}")
    print(f"{M}  ╠══════════════════════════════════════════════════════════════╣{RST}")
    for key in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]:
        gw = GATEWAYS[key]
        print(f"{M}  ║  {G}[{key:>2}]{RST}  {W}{gw['name']:<15}{D} {gw['description']:<38}{M}║{RST}")
    print(f"{M}  ╠══════════════════════════════════════════════════════════════╣{RST}")
    print(f"{M}  ║  {Y}[ 0]{RST}  {W}CUSTOM - Inserir gateway personalizada             {M}║{RST}")
    print(f"{M}  ║  {R}[99]{RST}  {W}SAIR                                              {M}║{RST}")
    print(f"{M}  ╚══════════════════════════════════════════════════════════════╝{RST}")


def print_config(proxy_count):
    print(f"\n{D}  ┌─────────────────────────────────────────────────────────┐{RST}")
    print(f"{D}  │ {W}CONFIGURACAO ATIVA                                       {D}│{RST}")
    print(f"{D}  ├─────────────────────────────────────────────────────────┤{RST}")
    print(f"{D}  │ {C}Proxies Carregadas  : {G}{proxy_count:>4}                           {D}│{RST}")
    print(f"{D}  │ {C}Threads             : {G}{MAX_THREADS:>4}                           {D}│{RST}")
    print(f"{D}  │ {C}Timeout             : {G}{REQUEST_TIMEOUT:>4}s                          {D}│{RST}")
    print(f"{D}  │ {C}curl_cffi           : {(G if CFFI_OK else R)}{'OK' if CFFI_OK else 'N/A':>4}                           {D}│{RST}")
    print(f"{D}  │ {C}Engines             : {G}DDG + Google + Bing             {D}│{RST}")
    print(f"{D}  │ {C}Store Validator     : {G}ON (score >= {STORE_SCORE_THRESHOLD})                  {D}│{RST}")
    print(f"{D}  │ {C}Anti-Lixo Filter    : {G}ON (blacklist + patterns)       {D}│{RST}")
    print(f"{D}  └─────────────────────────────────────────────────────────┘{RST}")


def plog(msg, status="info"):
    icons = {"info": f"{C}[*]{RST}", "ok": f"{G}[+]{RST}", "warn": f"{Y}[!]{RST}",
             "error": f"{R}[-]{RST}", "scan": f"{M}[~]{RST}", "store": f"{G}[LOJA]{RST}"}
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {D}{ts}{RST} {icons.get(status, icons['info'])} {msg}")


# ══════════════════════════════════════════════════════════════════
#                     MOTOR PRINCIPAL
# ══════════════════════════════════════════════════════════════════

class GateHunter:

    def __init__(self):
        dlog.info("GateHunter INIT | Inicializando componentes v3.0...")
        self.proxy_rotator = ProxyRotator()
        self.requester = SmartRequester(self.proxy_rotator)
        self.dork_engine = DorkEngine(self.requester)
        dlog.info(f"GateHunter INIT | ProxyRotator={self.proxy_rotator.count} proxies")

        self.output_dir = OUTPUT_DIR
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            test_f = os.path.join(self.output_dir, ".test")
            with open(test_f, "w") as f:
                f.write("t")
            os.remove(test_f)
        except (PermissionError, OSError):
            self.output_dir = FALLBACK_OUTPUT
            os.makedirs(self.output_dir, exist_ok=True)
            plog(f"Usando dir alternativo: {self.output_dir}", "warn")

        self.report_gen = ReportGenerator(self.output_dir)

    def run(self):
        while True:
            os.system("clear" if os.name != "nt" else "cls")
            print_banner()
            print_config(self.proxy_rotator.count)
            print_gateway_menu()

            try:
                choice = input(f"\n  {M}GateHunter{RST} {D}>{RST} {W}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n  {Y}Saindo...{RST}\n")
                sys.exit(0)

            if choice == "99":
                print(f"\n  {Y}Ate a proxima! GateHunter v{VERSION}{RST}\n")
                sys.exit(0)

            if choice == "0":
                self._custom_gateway()
                continue

            if choice in GATEWAYS:
                self._execute_scan(GATEWAYS[choice])
            else:
                plog("Opcao invalida!", "error")
                time.sleep(1.5)

    def _custom_gateway(self):
        print(f"\n  {C}GATEWAY PERSONALIZADA{RST}")
        print(f"  {D}{'─' * 50}{RST}")
        try:
            name = input(f"  {W}Nome da Gateway: {G}").strip()
            if not name:
                return
            sig = input(f"  {W}Assinatura/dominio (ex: minhagw.com): {G}").strip()
            if not sig:
                return
            dork_input = input(f"  {W}Dork customizada (Enter para auto): {G}").strip()

            if dork_input:
                dorks = [dork_input]
            else:
                dorks = [
                    f'"{sig}" checkout comprar produto loja -site:{sig} -blog',
                    f'"{sig}" carrinho comprar loja online -site:{sig}',
                    f'"{sig}" pagamento ecommerce loja -site:{sig} -site:github.com',
                    f'"{sig}" produto adicionar carrinho -site:{sig}',
                ]
            gateway = {
                "name": name, "dorks": dorks,
                "signatures": [sig, name.lower()],
                "own_domains": [sig],
                "description": f"Gateway customizada: {name}",
            }
            self._execute_scan(gateway)
        except (KeyboardInterrupt, EOFError):
            return

    def _execute_scan(self, gateway):
        name = gateway["name"]
        dorks = gateway["dorks"]
        signatures = gateway["signatures"]
        own_domains = gateway.get("own_domains", [])

        # Configurar o DorkEngine com os domínios da gateway
        self.dork_engine.set_gateway_domains(own_domains)

        dlog.log_scan_start(name, dorks, signatures, self.proxy_rotator.count)

        print(f"\n{'=' * 70}")
        print(f"  {C}INICIANDO SCAN: {W}{name}{RST}")
        print(f"{'=' * 70}")
        plog(f"Gateway: {name}", "info")
        plog(f"Dorks: {len(dorks)}", "info")
        plog(f"Assinaturas: {', '.join(signatures)}", "info")
        plog(f"Dominios bloqueados: {', '.join(own_domains)}", "info")
        plog(f"Proxies: {self.proxy_rotator.count}", "info")
        plog(f"Threads: {MAX_THREADS}", "info")
        plog(f"Store Score Min: {STORE_SCORE_THRESHOLD}", "info")
        print()

        start_time = time.time()

        # ── FASE 1: Coleta via Dorks ──────────────────────
        dlog.log_phase("FASE 1/3", f"Coletando URLs via Dorks para {name}")
        plog("FASE 1/3: Coletando URLs via Dorks (Multi-Engine)...", "scan")
        all_urls = []

        for i, dork in enumerate(dorks, 1):
            plog(f"Dork [{i}/{len(dorks)}]: {dork[:60]}...", "scan")
            try:
                urls = self.dork_engine.search_all_engines(dork)
                all_urls.extend(urls)
                plog(f"  -> {len(urls)} URLs validas encontradas", "ok")
            except Exception as e:
                plog(f"  -> Erro: {str(e)[:40]}", "error")
                dlog.error(f"DORK EXCEPTION | dork={dork[:60]} | {str(e)[:150]}")
            time.sleep(random.uniform(1, 3))

        unique_urls = list(set(all_urls))

        # Deduplicar por domínio (manter apenas 1 URL por domínio)
        seen_domains = set()
        deduped_urls = []
        for url in unique_urls:
            try:
                domain = urllib.parse.urlparse(url).netloc.lower()
                # Remover www. para dedup
                domain_clean = domain.replace("www.", "")
                if domain_clean not in seen_domains:
                    seen_domains.add(domain_clean)
                    deduped_urls.append(url)
                else:
                    dlog.log_filter(url, f"duplicate_domain:{domain_clean}")
            except Exception:
                deduped_urls.append(url)

        print()
        plog(f"URLs brutas: {len(all_urls)} | Unicas: {len(unique_urls)} | Dedup: {len(deduped_urls)}", "ok")
        dlog.info(f"FASE 1 COMPLETE | raw={len(all_urls)} | unique={len(unique_urls)} | dedup={len(deduped_urls)}")

        if not deduped_urls:
            plog("Nenhuma URL encontrada. Tente outra gateway ou dork.", "warn")
            input(f"\n  {D}Enter para voltar...{RST}")
            return

        # ── FASE 2: Análise profunda ──────────────────────
        dlog.log_phase("FASE 2/3", f"Analisando {len(deduped_urls)} sites com {MAX_THREADS} threads")
        print()
        plog(f"FASE 2/3: Analisando {len(deduped_urls)} sites ({MAX_THREADS} threads)...", "scan")
        plog(f"Filtro anti-lixo: ON | Store Validator: ON (score >= {STORE_SCORE_THRESHOLD})", "info")

        analyzer = SiteAnalyzer(self.requester, signatures, own_domains)
        results = []
        confirmed_count = 0
        store_count = 0
        analyzed_count = 0
        filtered_count = 0

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(analyzer.analyze, url): url for url in deduped_urls}
            for future in as_completed(futures):
                analyzed_count += 1
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        if result.get("gateway_confirmed"):
                            confirmed_count += 1
                            if result.get("is_real_store"):
                                store_count += 1
                                plog(
                                    f"[{analyzed_count}/{len(deduped_urls)}] {G}LOJA REAL{RST} "
                                    f"{result.get('domain', '')[:30]} | "
                                    f"{result.get('category', 'N/A')} | "
                                    f"Score={result.get('store_score', 0)} | "
                                    f"Plat={result.get('ecommerce_platform', '?')}",
                                    "store"
                                )
                            else:
                                plog(
                                    f"[{analyzed_count}/{len(deduped_urls)}] {C}CONFIRMADO{RST} "
                                    f"{result.get('domain', '')[:30]} | "
                                    f"{result.get('category', 'N/A')} | "
                                    f"Score={result.get('store_score', 0)}",
                                    "ok"
                                )
                        elif analyzed_count % 5 == 0:
                            plog(
                                f"[{analyzed_count}/{len(deduped_urls)}] Analisando... "
                                f"({store_count} lojas | {confirmed_count} confirmados)",
                                "scan"
                            )
                    else:
                        filtered_count += 1
                except Exception:
                    pass

        scan_time = time.time() - start_time

        # ── FASE 3: Relatórios ────────────────────────
        dlog.log_phase("FASE 3/3", "Gerando relatorios")
        print()
        plog("FASE 3/3: Gerando relatorios...", "scan")

        files = self.report_gen.generate_full_report(
            gateway_name=name, results=results,
            stats=self.requester.stats, scan_time=scan_time,
        )
        dlog.log_report(files)
        dlog.log_scan_end(name, results, self.requester.stats, scan_time)

        # ── Resumo final ─────────────────────────────────────
        stores_r = [r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")]
        confirmed_r = [r for r in results if r.get("gateway_confirmed")]
        other_r = [r for r in confirmed_r if not r.get("is_real_store")]

        print(f"\n{'=' * 70}")
        print(f"  {G}SCAN COMPLETO!{RST}")
        print(f"{'=' * 70}")
        print(f"  {W}Gateway            : {C}{name}{RST}")
        print(f"  {W}Tempo total        : {C}{scan_time:.1f}s{RST}")
        print(f"  {W}URLs analisadas    : {C}{len(deduped_urls)}{RST}")
        print(f"  {W}Filtradas (lixo)   : {Y}{filtered_count}{RST}")
        print(f"  {W}Gateway confirmada : {G}{len(confirmed_r)}{RST}")
        print(f"  {W}LOJAS REAIS        : {G}{BOLD}{len(stores_r)}{RST}")
        print(f"  {W}Outros confirmados : {C}{len(other_r)}{RST}")
        print(f"  {W}Requests total     : {C}{self.requester.stats.get('requests', 0)}{RST}")
        print(f"  {W}Bloqueios          : {R}{self.requester.stats.get('blocked', 0)}{RST}")
        print(f"\n  {W}Arquivos gerados:{RST}")
        for fmt, path in files.items():
            size = os.path.getsize(path) if os.path.exists(path) else 0
            icon = G if "store" in fmt else C
            print(f"  {icon}[+]{RST} {fmt.upper():>12} : {C}{path}{RST} ({size:,} bytes)")

        if stores_r:
            print(f"\n  {G}{BOLD}TOP LOJAS REAIS ENCONTRADAS:{RST}")
            print(f"  {D}{'─' * 65}{RST}")
            for i, s in enumerate(stores_r[:20], 1):
                print(
                    f"  {G}{i:>3}.{RST} {s.get('domain', 'N/A'):<30} "
                    f"{D}|{RST} {s.get('category', 'N/A'):<25} "
                    f"{D}|{RST} {s.get('ecommerce_platform', '?')}"
                )

            cat_count = {}
            for s in stores_r:
                cat = s.get("category", "Outros")
                cat_count[cat] = cat_count.get(cat, 0) + 1
            print(f"\n  {M}CATEGORIAS (LOJAS REAIS):{RST}")
            print(f"  {D}{'─' * 65}{RST}")
            for cat, count in sorted(cat_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  {W}{cat:<35}{RST} {C}{count:>3}{RST} {G}{'█' * min(count, 30)}{RST}")

        print(f"\n  {D}Debug Log: {dlog.log_path}{RST}")
        print(f"\n{'=' * 70}\n")
        input(f"  {D}Pressione Enter para voltar ao menu...{RST}")


# ══════════════════════════════════════════════════════════════════
#                         MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    signal.signal(signal.SIGINT, lambda s, f: (print(f"\n\n  {Y}Interrompido. Saindo...{RST}\n"), sys.exit(0)))
    dlog.info("MAIN | GateHunter v{} starting...".format(VERSION))

    try:
        hunter = GateHunter()
        dlog.info(f"MAIN | Output dir: {hunter.output_dir}")
        dlog.info(f"MAIN | Debug log: {dlog.log_path}")
        hunter.run()
    except KeyboardInterrupt:
        dlog.info("MAIN | Interrupted by user (Ctrl+C)")
        print(f"\n\n  {Y}Ate a proxima! GateHunter v{VERSION}{RST}\n")
        sys.exit(0)
    except Exception as e:
        dlog.critical(f"MAIN | FATAL ERROR: {str(e)}")
        dlog.exception("MAIN | Traceback completo:")
        print(f"\n  {R}Erro fatal: {e}{RST}\n")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
