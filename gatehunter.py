#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║              GATEHUNTER v4.0 - NETHUNTER SUPREME EDITION         ║
║         Advanced Payment Gateway OSINT & Store Finder            ║
║                   Kali NetHunter Optimized                       ║
╚══════════════════════════════════════════════════════════════════╝

Ferramenta profissional de OSINT para identificação e catalogação
de LOJAS e E-COMMERCES REAIS que utilizam gateways de pagamento.

v4.0 - Dorks por assinatura JS + Blacklist massiva + Validação 3 camadas
       + Debug logs em /sdcard/nh_files/logs_gate_hunter.txt
Uso educacional e autorizado apenas.
"""

import os
import sys
import re
import json
import time
import random
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
R = "\033[1;31m"
G = "\033[1;32m"
Y = "\033[1;33m"
B = "\033[1;34m"
M = "\033[1;35m"
C = "\033[1;36m"
W = "\033[1;37m"
D = "\033[0;37m"
BOLD = "\033[1m"
RST = "\033[0m"

# ══════════════════════════════════════════════════════════════════
#                     CONSTANTES & CONFIG
# ══════════════════════════════════════════════════════════════════

VERSION = "4.0.0"
OUTPUT_DIR = "/sdcard/nh_files"
FALLBACK_OUTPUT = os.path.expanduser("~/gatehunter_output")
LOG_PATH = os.path.join(OUTPUT_DIR, "logs_gate_hunter.txt")
LOG_PATH_FALLBACK = os.path.join(FALLBACK_OUTPUT, "logs_gate_hunter.txt")
PROXIES_PATH_DEFAULT = os.path.join(OUTPUT_DIR, "proxies.txt")
PROXIES_PATH_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.txt")

MAX_THREADS = 12
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
DELAY_MIN = 2.0
DELAY_MAX = 5.0
STORE_SCORE_THRESHOLD = 8

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

# Domínios que NUNCA são lojas reais
GLOBAL_BLACKLIST_DOMAINS = [
    # Search engines & social
    "google.com", "google.com.br", "bing.com", "yahoo.com", "duckduckgo.com",
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "tiktok.com", "pinterest.com", "reddit.com", "quora.com",
    # Video & media
    "youtube.com", "vimeo.com", "dailymotion.com", "spotify.com",
    # Dev & code
    "github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com",
    "stackexchange.com", "npmjs.com", "pypi.org", "packagist.org",
    # Docs & wikis
    "wikipedia.org", "wikimedia.org", "medium.com", "dev.to", "hashnode.dev",
    # Reclamações & reviews
    "reclameaqui.com.br", "trustpilot.com", "glassdoor.com",
    # Governo & edu
    ".gov.br", ".edu.br", ".mil.br",
    # Marketplaces (não são lojas individuais)
    "mercadolivre.com.br", "amazon.com.br", "amazon.com", "aliexpress.com",
    "shopee.com.br", "magazineluiza.com.br", "americanas.com.br",
    # Plataformas e-commerce (são a plataforma, não a loja)
    "nuvemshop.com.br", "tiendanube.com", "tray.com.br", "traycorp.com.br",
    "lojaintegrada.com.br", "wbuy.com.br", "bagy.com.br", "dooca.com.br",
    "yampi.com.br", "cartpanda.com", "shopify.com", "vtex.com",
    "wix.com", "squarespace.com", "godaddy.com", "hostgator.com.br",
    "locaweb.com.br", "hostinger.com.br", "wordpress.com", "wordpress.org",
    # Blogs financeiros & informativos
    "fintech.com.br", "idinheiro.com.br", "infomoney.com.br",
    "serasaexperian.com.br", "contabilizei.com.br", "sebrae.com.br",
    "ecommercebrasil.com.br", "ecommercenews.com.br", "meioemensagem.com.br",
    "resultadosdigitais.com.br", "rockcontent.com", "neilpatel.com",
    "hubspot.com", "semrush.com", "ahrefs.com",
    # Diretórios de gateways & comparativos
    "paymentgateways.org", "malga.io", "finstack.com.br",
    "capterra.com.br", "b2bstack.com.br", "trustradius.com",
    # Suporte & knowledge bases
    "zendesk.com", "freshdesk.com", "intercom.com", "helpscout.com",
    "readme.io", "gitbook.io", "notion.so",
    # Outros
    "archive.org", "web.archive.org", "slideshare.net", "scribd.com",
    "issuu.com", "academia.edu", "researchgate.net",
    "apify.com", "crawlee.dev", "scrapingbee.com",
]

# Domínios informativos por padrão de subdomínio
INFORMATIONAL_SUBDOMAINS = [
    "docs.", "doc.", "blog.", "help.", "support.", "suporte.",
    "api.", "developer.", "developers.", "dev.", "status.",
    "community.", "comunidade.", "forum.", "faq.",
    "academy.", "learn.", "tutorial.", "atendimento.",
    "central.", "ajuda.", "base.", "basedeconhecimento.",
    "conteudo.", "materiais.", "material.", "recursos.",
    "knowledge.", "knowledgebase.", "kb.", "wiki.",
    "changelog.", "release.", "updates.", "news.",
    "careers.", "vagas.", "jobs.", "about.",
]

# ══════════════════════════════════════════════════════════════════
#              GATEWAYS COM DORKS POR ASSINATURA JS
# ══════════════════════════════════════════════════════════════════

GATEWAYS = {
    "1": {
        "name": "Asaas",
        "description": "Asaas - Plataforma de cobranças e pagamentos",
        # Assinaturas técnicas (scripts JS, iframes, APIs)
        "js_signatures": [
            "checkout.asaas.com", "js.asaas.com", "www.asaas.com/c/",
            "api.asaas.com", "cdn.asaas.com",
        ],
        "text_signatures": ["asaas"],
        # Domínios da própria gateway (para excluir)
        "own_domains": [
            "asaas.com", "asaas.com.br",
        ],
        # Dorks focadas em encontrar LOJAS REAIS (não docs/blogs)
        "dorks": [
            'intext:"checkout.asaas.com" -site:asaas.com -site:github.com -blog -docs -tutorial',
            'intext:"js.asaas.com" -site:asaas.com -site:github.com -site:medium.com',
            '"asaas.com/c/" comprar produto loja -site:asaas.com -blog -tutorial -docs',
            'intext:"asaas" intext:"carrinho" intext:"comprar" -site:asaas.com -blog',
            'intext:"asaas" intext:"R$" intext:"adicionar" -site:asaas.com -site:youtube.com',
            'inurl:checkout intext:"asaas" -site:asaas.com -site:github.com -docs',
        ],
    },
    "2": {
        "name": "PagarMe",
        "description": "Pagar.me (Stone) - Gateway de pagamentos",
        "js_signatures": [
            "api.pagar.me", "assets.pagar.me", "checkout.pagar.me",
            "js.pagar.me", "sdk.pagar.me",
        ],
        "text_signatures": ["pagar.me", "pagarme"],
        "own_domains": [
            "pagar.me", "pagarme.com.br", "stone.com.br",
            "docs.pagar.me", "conteudo.stone.com.br",
            "pagarme-website.pagar.me",
        ],
        "dorks": [
            'intext:"api.pagar.me" -site:pagar.me -site:stone.com.br -site:github.com -docs -blog',
            'intext:"checkout.pagar.me" -site:pagar.me -site:github.com -tutorial',
            'intext:"pagar.me" intext:"carrinho" intext:"comprar" -site:pagar.me -site:stone.com.br -blog',
            'intext:"pagar.me" intext:"R$" intext:"produto" -site:pagar.me -site:nuvemshop.com.br -blog',
            'intext:"pagarme" inurl:checkout -site:pagar.me -site:github.com -docs',
            'intext:"assets.pagar.me" -site:pagar.me -site:github.com -site:medium.com',
        ],
    },
    "3": {
        "name": "eRede",
        "description": "eRede (Itaú) - Adquirente e gateway",
        "js_signatures": [
            "userede.com.br", "e.rede.com.br", "api.userede.com.br",
            "developercielo.github.io/erede",
        ],
        "text_signatures": ["userede", "e.rede"],
        "own_domains": ["userede.com.br", "rede.com.br"],
        "dorks": [
            'intext:"userede.com.br" -site:userede.com.br -site:rede.com.br -site:github.com -blog -docs',
            'intext:"e.rede.com.br" intext:"comprar" -site:rede.com.br -blog -tutorial',
            'intext:"userede" intext:"carrinho" intext:"R$" -site:userede.com.br -blog',
            'intext:"erede" intext:"checkout" intext:"produto" -site:rede.com.br -docs',
        ],
    },
    "4": {
        "name": "PayFlow",
        "description": "PayFlow - Gateway de pagamentos digital",
        "js_signatures": ["payflow.com.br", "api.payflow.com.br"],
        "text_signatures": ["payflow"],
        "own_domains": ["payflow.com.br"],
        "dorks": [
            'intext:"payflow.com.br" -site:payflow.com.br -site:github.com -blog -docs',
            'intext:"payflow" intext:"checkout" intext:"comprar" -site:payflow.com.br -blog',
            'intext:"payflow" intext:"carrinho" intext:"R$" -site:payflow.com.br',
        ],
    },
    "5": {
        "name": "AppMax",
        "description": "AppMax - Plataforma de vendas e pagamentos",
        "js_signatures": ["appmax.com.br", "api.appmax.com.br", "checkout.appmax.com.br"],
        "text_signatures": ["appmax"],
        "own_domains": ["appmax.com.br"],
        "dorks": [
            'intext:"appmax.com.br" -site:appmax.com.br -site:github.com -blog -docs',
            'intext:"checkout.appmax" -site:appmax.com.br -site:github.com',
            'intext:"appmax" intext:"comprar" intext:"R$" -site:appmax.com.br -blog',
        ],
    },
    "6": {
        "name": "MercadoPago",
        "description": "Mercado Pago - Gateway e carteira digital",
        "js_signatures": [
            "sdk.mercadopago.com", "api.mercadopago.com",
            "www.mercadopago.com.br/checkout", "http-js.mlstatic.com",
        ],
        "text_signatures": ["mercadopago", "mercado pago"],
        "own_domains": ["mercadopago.com.br", "mercadopago.com", "mercadolivre.com.br", "mlstatic.com"],
        "dorks": [
            'intext:"sdk.mercadopago.com" -site:mercadopago.com -site:mercadolivre.com.br -site:github.com -docs',
            'intext:"mercadopago" intext:"carrinho" intext:"comprar" -site:mercadopago.com -site:mercadolivre.com.br -blog',
            'intext:"mercadopago" intext:"R$" intext:"produto" -site:mercadopago.com -blog -tutorial',
            'intext:"api.mercadopago" inurl:checkout -site:mercadopago.com -site:github.com',
        ],
    },
    "7": {
        "name": "PagSeguro",
        "description": "PagSeguro/PagBank - Gateway de pagamentos",
        "js_signatures": [
            "stc.pagseguro.uol.com.br", "ws.pagseguro.uol.com.br",
            "api.pagseguro.com", "checkout.pagseguro.com.br",
        ],
        "text_signatures": ["pagseguro", "pagbank"],
        "own_domains": ["pagseguro.uol.com.br", "pagseguro.com", "pagbank.com.br", "developer.pagbank.com.br"],
        "dorks": [
            'intext:"stc.pagseguro.uol" -site:pagseguro.uol.com.br -site:pagbank.com.br -site:github.com -docs',
            'intext:"pagseguro" intext:"carrinho" intext:"comprar" -site:pagseguro.uol.com.br -blog',
            'intext:"pagseguro" intext:"R$" intext:"produto" -site:pagseguro.uol.com.br -blog -tutorial',
            'intext:"checkout.pagseguro" -site:pagseguro.uol.com.br -site:github.com -docs',
        ],
    },
    "8": {
        "name": "Cielo",
        "description": "Cielo - Maior adquirente do Brasil",
        "js_signatures": [
            "cieloecommerce.cielo.com.br", "api.cielo.com.br",
            "api2.cielo.com.br", "checkout.cielo.com.br",
        ],
        "text_signatures": ["cielo"],
        "own_domains": ["cielo.com.br", "developercielo.github.io"],
        "dorks": [
            'intext:"cieloecommerce.cielo" -site:cielo.com.br -site:github.com -docs -blog',
            'intext:"api.cielo.com.br" intext:"comprar" -site:cielo.com.br -blog -tutorial',
            'intext:"cielo" intext:"carrinho" intext:"R$" -site:cielo.com.br -site:github.com -blog',
            'intext:"checkout.cielo" -site:cielo.com.br -site:github.com -docs',
        ],
    },
    "9": {
        "name": "Stripe",
        "description": "Stripe - Gateway global de pagamentos",
        "js_signatures": [
            "js.stripe.com", "api.stripe.com", "checkout.stripe.com",
            "m.stripe.network",
        ],
        "text_signatures": ["stripe"],
        "own_domains": ["stripe.com", "stripe.dev"],
        "dorks": [
            'intext:"js.stripe.com" site:.com.br -site:stripe.com -site:github.com -docs -blog',
            'intext:"stripe" intext:"carrinho" intext:"comprar" site:.com.br -site:stripe.com -blog',
            'intext:"checkout.stripe.com" site:.com.br -site:stripe.com -site:github.com',
            'intext:"stripe" intext:"R$" intext:"produto" site:.com.br -site:stripe.com -blog',
        ],
    },
    "10": {
        "name": "Hotmart",
        "description": "Hotmart - Plataforma de produtos digitais",
        "js_signatures": ["pay.hotmart.com", "api-hot-connect.hotmart.com"],
        "text_signatures": ["hotmart"],
        "own_domains": ["hotmart.com", "hotmart.com.br"],
        "dorks": [
            'intext:"pay.hotmart.com" -site:hotmart.com -site:github.com -blog -docs',
            'intext:"hotmart" intext:"comprar" intext:"curso" -site:hotmart.com -blog -tutorial',
            'intext:"hotmart" intext:"checkout" -site:hotmart.com -site:github.com -docs',
        ],
    },
    "11": {
        "name": "Eduzz",
        "description": "Eduzz - Plataforma de infoprodutos",
        "js_signatures": ["sun.eduzz.com", "api.eduzz.com", "checkout.eduzz.com"],
        "text_signatures": ["eduzz"],
        "own_domains": ["eduzz.com", "eduzz.com.br"],
        "dorks": [
            'intext:"sun.eduzz.com" -site:eduzz.com -site:github.com -blog -docs',
            'intext:"eduzz" intext:"comprar" intext:"curso" -site:eduzz.com -blog',
            'intext:"checkout.eduzz" -site:eduzz.com -site:github.com',
        ],
    },
    "12": {
        "name": "Kiwify",
        "description": "Kiwify - Plataforma de vendas digitais",
        "js_signatures": ["pay.kiwify.com.br", "api.kiwify.com.br"],
        "text_signatures": ["kiwify"],
        "own_domains": ["kiwify.com.br"],
        "dorks": [
            'intext:"pay.kiwify.com.br" -site:kiwify.com.br -site:github.com -blog -docs',
            'intext:"kiwify" intext:"comprar" intext:"curso" -site:kiwify.com.br -blog',
            'intext:"kiwify" intext:"checkout" -site:kiwify.com.br -site:github.com',
        ],
    },
    "13": {
        "name": "Vindi",
        "description": "Vindi - Plataforma de pagamentos recorrentes",
        "js_signatures": ["api.vindi.com.br", "app.vindi.com.br", "js.vindi.com.br"],
        "text_signatures": ["vindi"],
        "own_domains": ["vindi.com.br"],
        "dorks": [
            'intext:"api.vindi.com.br" -site:vindi.com.br -site:github.com -blog -docs',
            'intext:"vindi" intext:"assinar" intext:"plano" -site:vindi.com.br -blog',
            'intext:"vindi" intext:"pagamento" intext:"recorrente" -site:vindi.com.br -blog -tutorial',
        ],
    },
    "14": {
        "name": "Iugu",
        "description": "Iugu - Gateway e plataforma financeira",
        "js_signatures": ["api.iugu.com", "js.iugu.com", "alia.iugu.com"],
        "text_signatures": ["iugu"],
        "own_domains": ["iugu.com", "iugu.com.br"],
        "dorks": [
            'intext:"js.iugu.com" -site:iugu.com -site:github.com -blog -docs',
            'intext:"api.iugu.com" -site:iugu.com -site:github.com -blog',
            'intext:"iugu" intext:"comprar" intext:"R$" -site:iugu.com -blog -tutorial',
        ],
    },
    "15": {
        "name": "Getnet",
        "description": "Getnet (Santander) - Adquirente e gateway",
        "js_signatures": ["api.getnet.com.br", "checkout.getnet.com.br"],
        "text_signatures": ["getnet"],
        "own_domains": ["getnet.com.br"],
        "dorks": [
            'intext:"api.getnet.com.br" -site:getnet.com.br -site:github.com -blog -docs',
            'intext:"getnet" intext:"checkout" intext:"comprar" -site:getnet.com.br -blog',
            'intext:"getnet" intext:"carrinho" intext:"R$" -site:getnet.com.br -blog -tutorial',
        ],
    },
}

# ══════════════════════════════════════════════════════════════════
#                  CATEGORIAS DE CLASSIFICAÇÃO
# ══════════════════════════════════════════════════════════════════

SITE_CATEGORIES = {
    "moda": {"label": "Loja de Roupas / Moda", "keywords": [
        "roupa", "camiseta", "vestido", "calça", "blusa", "moda",
        "fashion", "jeans", "saia", "bermuda", "lingerie", "underwear",
        "camisola", "pijama", "biquini", "maiô", "acessório",
    ]},
    "calcados": {"label": "Loja de Calçados / Tênis", "keywords": [
        "tênis", "sapato", "sandália", "bota", "chinelo", "calçado",
        "sneaker", "shoe", "nike", "adidas", "puma", "vans",
    ]},
    "eletronicos": {"label": "Loja de Eletrônicos / Tecnologia", "keywords": [
        "celular", "smartphone", "notebook", "computador", "tablet",
        "fone", "headphone", "eletrônico", "informática", "tech",
        "gadget", "câmera", "monitor", "teclado", "mouse",
    ]},
    "cosmeticos": {"label": "Loja de Cosméticos / Beleza", "keywords": [
        "cosmético", "maquiagem", "perfume", "skincare", "beleza",
        "beauty", "creme", "shampoo", "cabelo", "unha", "esmalte",
    ]},
    "suplementos": {"label": "Loja de Suplementos / Saúde", "keywords": [
        "suplemento", "whey", "creatina", "vitamina", "proteína",
        "fitness", "academia", "treino", "saúde", "natural",
    ]},
    "alimentos": {"label": "Loja de Alimentos / Bebidas", "keywords": [
        "alimento", "comida", "bebida", "café", "vinho", "cerveja",
        "chocolate", "doce", "gourmet", "orgânico", "delivery",
    ]},
    "moveis": {"label": "Loja de Móveis / Decoração", "keywords": [
        "móvel", "sofá", "mesa", "cadeira", "decoração", "cama",
        "colchão", "estante", "armário", "tapete", "cortina",
    ]},
    "pet": {"label": "Pet Shop / Produtos para Animais", "keywords": [
        "pet", "cachorro", "gato", "ração", "petshop", "animal",
        "veterinário", "coleira", "brinquedo pet",
    ]},
    "esportes": {"label": "Loja de Esportes / Fitness", "keywords": [
        "esporte", "futebol", "basquete", "corrida", "bicicleta",
        "academia", "yoga", "pilates", "natação", "camping",
    ]},
    "joias": {"label": "Joalheria / Bijuteria", "keywords": [
        "joia", "anel", "colar", "brinco", "pulseira", "relógio",
        "ouro", "prata", "bijuteria", "semijoias",
    ]},
    "infantil": {"label": "Loja Infantil / Brinquedos", "keywords": [
        "infantil", "criança", "bebê", "brinquedo", "kids", "baby",
        "carrinho", "boneca", "lego", "berço", "enxoval",
    ]},
    "auto": {"label": "Auto Peças / Acessórios Automotivos", "keywords": [
        "auto peça", "automotivo", "carro", "moto", "pneu",
        "óleo", "filtro", "acessório automotivo", "veículo",
    ]},
    "livros": {"label": "Livraria / Papelaria", "keywords": [
        "livro", "livraria", "papelaria", "caderno", "caneta",
        "leitura", "editora", "revista", "manga", "hq",
    ]},
    "digital": {"label": "Produtos Digitais / Cursos", "keywords": [
        "curso", "ebook", "mentoria", "treinamento", "aula",
        "online", "digital", "infoproduto", "masterclass",
    ]},
    "casa": {"label": "Casa / Utilidades Domésticas", "keywords": [
        "casa", "cozinha", "banheiro", "limpeza", "organização",
        "utilidade", "doméstico", "eletrodoméstico", "panela",
    ]},
    "saude": {"label": "Farmácia / Saúde", "keywords": [
        "farmácia", "remédio", "medicamento", "saúde", "bem-estar",
        "ortopédico", "hospitalar", "médico",
    ]},
    "agro": {"label": "Agro / Produtos Rurais", "keywords": [
        "agro", "rural", "fazenda", "semente", "fertilizante",
        "trator", "irrigação", "pecuária", "agrícola",
    ]},
    "sex_shop": {"label": "Sex Shop / Adulto", "keywords": [
        "sex shop", "adulto", "sensual", "lingerie sensual",
        "vibrador", "prazer", "erótico",
    ]},
}

# ══════════════════════════════════════════════════════════════════
#                     DEBUG LOGGER
# ══════════════════════════════════════════════════════════════════

class DebugLogger:
    """Sistema de logging completo para debug."""

    def __init__(self):
        self.log_path = self._init_log_path()
        self.logger = logging.getLogger("GateHunter")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # File handler
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            fh = logging.FileHandler(self.log_path, mode="a", encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fmt = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(threadName)-12s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)
        except Exception as e:
            print(f"  {Y}[!] Erro ao criar log: {e}{RST}")

        # Console handler (apenas warnings+)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        self.logger.addHandler(ch)

        self.info(f"{'='*80}")
        self.info(f"GATEHUNTER v{VERSION} - DEBUG LOG INICIADO")
        self.info(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Log path: {self.log_path}")
        self.info(f"Python: {sys.version}")
        self.info(f"Platform: {sys.platform}")
        self.info(f"curl_cffi: {CFFI_OK}")
        self.info(f"{'='*80}")

    def _init_log_path(self) -> str:
        for path in [LOG_PATH, LOG_PATH_FALLBACK]:
            try:
                d = os.path.dirname(path)
                os.makedirs(d, exist_ok=True)
                with open(path, "a") as f:
                    f.write("")
                return path
            except (PermissionError, OSError):
                continue
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs_gate_hunter.txt")

    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warn(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def critical(self, msg): self.logger.critical(msg)
    def exception(self, msg): self.logger.exception(msg)

    def log_request(self, method, url, status, proxy, imp, elapsed, error=None):
        msg = f"HTTP {method} | status={status} | proxy={proxy} | imp={imp} | time={elapsed:.2f}s | url={url[:120]}"
        if error:
            msg += f" | error={error}"
        self.debug(msg)

    def log_dork(self, engine, dork, count, error=None):
        msg = f"DORK {engine} | results={count} | dork={dork[:80]}"
        if error:
            msg += f" | error={error}"
        self.info(msg)

    def log_filter(self, url, reason):
        self.debug(f"FILTERED | reason={reason} | url={url[:120]}")

    def log_analysis(self, url, confirmed, category, matches, error=None):
        msg = f"ANALYSIS | confirmed={confirmed} | cat={category} | matches={matches} | url={url[:100]}"
        if error:
            msg += f" | error={error}"
        self.info(msg)

    def log_store_validation(self, url, score, signals, is_store):
        self.info(f"STORE_VALID | score={score} | is_store={is_store} | signals={len(signals)} | url={url[:100]}")
        if signals:
            self.debug(f"STORE_SIGNALS | {', '.join(signals[:10])}")

    def log_scan_start(self, gw, dorks, sigs, proxies):
        self.info(f"{'='*60}")
        self.info(f"SCAN START | gateway={gw} | dorks={len(dorks)} | sigs={len(sigs)} | proxies={proxies}")
        for i, d in enumerate(dorks):
            self.info(f"  DORK[{i}] = {d[:100]}")
        self.info(f"{'='*60}")

    def log_scan_end(self, gw, results, stats, elapsed):
        confirmed = len([r for r in results if r.get("gateway_confirmed")])
        stores = len([r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")])
        self.info(f"{'='*60}")
        self.info(f"SCAN END | gateway={gw} | total={len(results)} | confirmed={confirmed} | stores={stores} | time={elapsed:.1f}s")
        self.info(f"STATS | requests={stats.get('requests',0)} | success={stats.get('success',0)} | failed={stats.get('failed',0)} | blocked={stats.get('blocked',0)}")
        self.info(f"{'='*60}")

    def log_phase(self, phase, desc):
        self.info(f"PHASE | {phase} | {desc}")

    def log_report(self, files):
        for fmt, path in files.items():
            size = os.path.getsize(path) if os.path.exists(path) else 0
            self.info(f"REPORT | {fmt} | {path} | {size} bytes")

    def log_proxy(self, action, ip, detail=""):
        self.debug(f"PROXY {action} | ip={ip} | {detail}")

    def log_fingerprint(self, headers):
        self.debug(f"FINGERPRINT | UA={headers.get('User-Agent','?')[:60]} | Platform={headers.get('sec-ch-ua-platform','?')}")


# Instanciar logger global
dlog = DebugLogger()



# ══════════════════════════════════════════════════════════════════
#                    PROXY ROTATOR
# ══════════════════════════════════════════════════════════════════

class ProxyRotator:
    """Gerenciador de proxy pool com rotação e failover."""

    def __init__(self):
        self.proxies: List[Dict] = []
        self.current_idx = 0
        self.failed: Set[str] = set()
        self.lock = threading.Lock()
        self._load_proxies()

    def _load_proxies(self):
        for path in [PROXIES_PATH_DEFAULT, PROXIES_PATH_FALLBACK]:
            if os.path.exists(path):
                dlog.info(f"Loading proxies from: {path}")
                with open(path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split(":")
                        if len(parts) >= 4:
                            proxy = {
                                "ip": parts[0],
                                "port": parts[1],
                                "user": parts[2],
                                "pass": parts[3],
                            }
                            self.proxies.append(proxy)
                            dlog.log_proxy("LOADED", parts[0], f"port={parts[1]}")
                if self.proxies:
                    dlog.info(f"Total proxies loaded: {len(self.proxies)}")
                    return
        dlog.warn("No proxy file found - running without proxies")

    def get_proxy(self) -> Optional[Dict]:
        if not self.proxies:
            return None
        with self.lock:
            available = [p for p in self.proxies if p["ip"] not in self.failed]
            if not available:
                dlog.warn("All proxies failed, resetting pool")
                self.failed.clear()
                available = self.proxies
            proxy = random.choice(available)
            url = f"http://{proxy['user']}:{proxy['pass']}@{proxy['ip']}:{proxy['port']}"
            dlog.log_proxy("SELECTED", proxy["ip"])
            return {"http": url, "https": url, "ip": proxy["ip"]}

    def mark_failed(self, ip: str):
        with self.lock:
            self.failed.add(ip)
            dlog.log_proxy("FAILED", ip, f"total_failed={len(self.failed)}")

    @property
    def count(self) -> int:
        return len(self.proxies)


# ══════════════════════════════════════════════════════════════════
#                  FINGERPRINT GENERATOR
# ══════════════════════════════════════════════════════════════════

class FingerprintGenerator:
    """Gera fingerprints realistas para evasão de detecção."""

    PLATFORMS = [
        ("Windows", '"Windows"'),
        ("macOS", '"macOS"'),
        ("Linux", '"Linux"'),
    ]

    CHROME_VERSIONS = [
        ('"Chromium";v="120", "Google Chrome";v="120", "Not:A-Brand";v="99"', "120"),
        ('"Chromium";v="121", "Google Chrome";v="121", "Not A(Brand";v="99"', "121"),
        ('"Chromium";v="119", "Google Chrome";v="119", "Not?A_Brand";v="24"', "119"),
    ]

    LANGUAGES = ["pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7", "pt-BR,pt;q=0.9,en;q=0.8", "en-US,en;q=0.9,pt-BR;q=0.8"]

    def generate(self) -> Dict[str, str]:
        platform_name, platform_val = random.choice(self.PLATFORMS)
        brands, ver = random.choice(self.CHROME_VERSIONS)
        lang = random.choice(self.LANGUAGES)

        if UA_GEN:
            try:
                ua = UA_GEN.random
            except Exception:
                ua = random.choice(PREMIUM_USER_AGENTS)
        else:
            ua = random.choice(PREMIUM_USER_AGENTS)

        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": lang,
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": brands,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": platform_val,
            "Cache-Control": "max-age=0",
        }
        dlog.log_fingerprint(headers)
        return headers


# ══════════════════════════════════════════════════════════════════
#                   SMART REQUESTER
# ══════════════════════════════════════════════════════════════════

class SmartRequester:
    """Motor de requisições com curl_cffi impersonate, proxy rotation e retries."""

    def __init__(self, proxy_rotator: ProxyRotator, fingerprint_gen: FingerprintGenerator):
        self.proxy = proxy_rotator
        self.fp = fingerprint_gen
        self.stats = {"requests": 0, "success": 0, "failed": 0, "blocked": 0}
        self.lock = threading.Lock()

    def _update_stats(self, key):
        with self.lock:
            self.stats[key] = self.stats.get(key, 0) + 1

    def get(self, url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
        self._update_stats("requests")
        headers = self.fp.generate()
        proxy_info = self.proxy.get_proxy()
        proxy_dict = None
        proxy_ip = "direct"

        if proxy_info:
            proxy_dict = {"http": proxy_info["http"], "https": proxy_info["https"]}
            proxy_ip = proxy_info["ip"]

        # Tentar com curl_cffi (TLS impersonate)
        if CFFI_OK:
            imp = random.choice(IMPERSONATE_TARGETS)
            for attempt in range(MAX_RETRIES):
                t0 = time.time()
                try:
                    resp = cffi_requests.get(
                        url, headers=headers, timeout=timeout,
                        impersonate=imp, proxies=proxy_dict,
                        allow_redirects=True, verify=False,
                    )
                    elapsed = time.time() - t0
                    dlog.log_request("GET", url, resp.status_code, proxy_ip, imp, elapsed)

                    if resp.status_code == 429:
                        self._update_stats("blocked")
                        dlog.warn(f"Rate limited (429) on {url[:80]}")
                        if proxy_info:
                            self.proxy.mark_failed(proxy_ip)
                        time.sleep(random.uniform(5, 10))
                        # Trocar proxy
                        proxy_info = self.proxy.get_proxy()
                        if proxy_info:
                            proxy_dict = {"http": proxy_info["http"], "https": proxy_info["https"]}
                            proxy_ip = proxy_info["ip"]
                        continue

                    if resp.status_code == 200:
                        self._update_stats("success")
                        return resp.text

                    if resp.status_code in (403, 503):
                        dlog.warn(f"Blocked ({resp.status_code}) on {url[:80]}, attempt {attempt+1}")
                        time.sleep(random.uniform(3, 6))
                        imp = random.choice(IMPERSONATE_TARGETS)
                        continue

                    self._update_stats("success")
                    return resp.text

                except Exception as e:
                    elapsed = time.time() - t0
                    dlog.log_request("GET", url, "ERR", proxy_ip, imp, elapsed, str(e)[:80])
                    if proxy_info:
                        self.proxy.mark_failed(proxy_ip)
                    if attempt < MAX_RETRIES - 1:
                        proxy_info = self.proxy.get_proxy()
                        if proxy_info:
                            proxy_dict = {"http": proxy_info["http"], "https": proxy_info["https"]}
                            proxy_ip = proxy_info["ip"]
                        time.sleep(random.uniform(2, 4))

        # Fallback com urllib
        dlog.debug(f"Fallback urllib for {url[:80]}")
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                elapsed = time.time() - t0
                dlog.log_request("GET-urllib", url, resp.status, "direct", "none", elapsed)
                self._update_stats("success")
                return html
        except Exception as e:
            dlog.log_request("GET-urllib", url, "ERR", "direct", "none", 0, str(e)[:80])

        self._update_stats("failed")
        return None



# ══════════════════════════════════════════════════════════════════
#                    URL FILTER (CAMADA 1)
# ══════════════════════════════════════════════════════════════════

class URLFilter:
    """Filtro de URLs em 3 camadas para eliminar falsos positivos."""

    def __init__(self, gateway_config: Dict):
        self.gw = gateway_config
        self.own_domains = set(gateway_config.get("own_domains", []))
        # Construir blacklist completa
        self.blacklist = set(GLOBAL_BLACKLIST_DOMAINS)
        # Adicionar domínios da própria gateway
        for d in self.own_domains:
            self.blacklist.add(d)
            # Adicionar subdomínios comuns da gateway
            for sub in ["docs", "blog", "api", "dev", "developer", "help",
                        "support", "status", "conteudo", "materiais", "cdn",
                        "checkout", "assets", "js", "sdk", "pagarme-website"]:
                self.blacklist.add(f"{sub}.{d}")

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower().replace("www.", "")
        except Exception:
            return ""

    def _extract_base_domain(self, domain: str) -> str:
        """Extrai o domínio base (ex: docs.pagar.me -> pagar.me)."""
        parts = domain.split(".")
        if len(parts) >= 3:
            # Tratar .com.br, .org.br etc
            if parts[-2] in ("com", "org", "net", "edu", "gov") and parts[-1] == "br":
                return ".".join(parts[-3:])
            return ".".join(parts[-2:])
        return domain

    def is_valid(self, url: str) -> Tuple[bool, str]:
        """Retorna (is_valid, reason) - reason vazio se válido."""
        if not url or not url.startswith("http"):
            return False, "invalid_url"

        domain = self._extract_domain(url)
        base_domain = self._extract_base_domain(domain)

        # Check 1: Blacklist global
        for bl in self.blacklist:
            if bl.startswith("."):
                if domain.endswith(bl) or base_domain.endswith(bl):
                    return False, f"blacklist_suffix:{bl}"
            elif domain == bl or base_domain == bl or domain.endswith(f".{bl}"):
                return False, f"blacklist:{bl}"

        # Check 2: Subdomínios informativos
        for sub in INFORMATIONAL_SUBDOMAINS:
            if domain.startswith(sub):
                return False, f"informational_subdomain:{sub}"

        # Check 3: Padrões de URL informativos
        path_lower = url.lower()
        bad_patterns = [
            "/blog/", "/blog?", "/docs/", "/docs?", "/doc/",
            "/help/", "/faq/", "/faq?", "/tutorial/", "/tutorial?",
            "/api/", "/reference/", "/developer/", "/developers/",
            "/knowledgebase", "/knowledge-base", "/knowledge_base",
            "/support/", "/suporte/", "/atendimento/",
            "/articles/", "/article/", "/hc/", "/community/",
            "/comunidade/", "/forum/", "/changelog/",
            "/about/", "/sobre/", "/contato/", "/contact/",
            "/pricing/", "/precos/", "/planos/",
            "/wiki/", "/guide/", "/guia/",
        ]
        for pat in bad_patterns:
            if pat in path_lower:
                return False, f"bad_path:{pat}"

        # Check 4: Domínio é da própria gateway
        for own in self.own_domains:
            if domain == own or domain.endswith(f".{own}"):
                return False, f"own_gateway_domain:{own}"

        return True, ""


# ══════════════════════════════════════════════════════════════════
#                      DORK ENGINE
# ══════════════════════════════════════════════════════════════════

class DorkEngine:
    """Motor de busca multi-engine (DuckDuckGo + Google + Bing)."""

    def __init__(self, requester: SmartRequester, url_filter: URLFilter):
        self.req = requester
        self.url_filter = url_filter

    def _extract_urls_from_html(self, html: str) -> Set[str]:
        """Extrai URLs reais de resultados de busca."""
        urls = set()
        if not html:
            return urls

        # Padrão 1: DuckDuckGo uddg redirect
        for match in re.finditer(r'uddg=([^&"]+)', html):
            try:
                decoded = urllib.parse.unquote(match.group(1))
                if decoded.startswith("http") and "duckduckgo" not in decoded:
                    urls.add(decoded.split("&")[0])
            except Exception:
                pass

        # Padrão 2: Links href genéricos
        for match in re.finditer(r'href="(https?://[^"]+)"', html):
            url = match.group(1)
            # Filtrar URLs de search engines
            skip_domains = ["google.", "bing.", "duckduckgo.", "yahoo.",
                            "microsofttranslator.", "webcache.", "translate."]
            if not any(d in url.lower() for d in skip_domains):
                urls.add(url.split("#")[0])

        # Padrão 3: Bing cite tags
        for match in re.finditer(r'<cite[^>]*>(https?://[^<]+)</cite>', html):
            urls.add(match.group(1).split("#")[0])

        return urls

    def search_duckduckgo(self, dork: str, max_pages: int = 3) -> Set[str]:
        """Busca no DuckDuckGo HTML (lite)."""
        all_urls = set()
        dlog.debug(f"DDG search: {dork[:80]}")

        for page in range(max_pages):
            query = urllib.parse.quote_plus(dork)
            if page == 0:
                url = f"https://lite.duckduckgo.com/lite/?q={query}"
            else:
                url = f"https://lite.duckduckgo.com/lite/?q={query}&s={page * 30}&o=json&dc={page * 30 + 1}"

            html = self.req.get(url)
            if html:
                found = self._extract_urls_from_html(html)
                new = found - all_urls
                all_urls.update(found)
                dlog.debug(f"DDG page {page}: {len(new)} new URLs")
                if len(new) == 0 and page > 0:
                    break
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        dlog.log_dork("DDG", dork, len(all_urls))
        return all_urls

    def search_google(self, dork: str, max_pages: int = 2) -> Set[str]:
        """Busca no Google."""
        all_urls = set()
        dlog.debug(f"Google search: {dork[:80]}")

        for page in range(max_pages):
            start = page * 10
            query = urllib.parse.quote_plus(dork)
            url = f"https://www.google.com/search?q={query}&start={start}&num=10&hl=pt-BR"

            html = self.req.get(url)
            if html:
                found = self._extract_urls_from_html(html)
                new = found - all_urls
                all_urls.update(found)
                dlog.debug(f"Google page {page}: {len(new)} new URLs")

                if "captcha" in html.lower() or "unusual traffic" in html.lower():
                    dlog.warn("Google CAPTCHA detected, stopping Google engine")
                    break
            time.sleep(random.uniform(DELAY_MIN + 1, DELAY_MAX + 2))

        dlog.log_dork("Google", dork, len(all_urls))
        return all_urls

    def search_bing(self, dork: str, max_pages: int = 2) -> Set[str]:
        """Busca no Bing."""
        all_urls = set()
        dlog.debug(f"Bing search: {dork[:80]}")

        for page in range(max_pages):
            first = page * 10 + 1
            query = urllib.parse.quote_plus(dork)
            url = f"https://www.bing.com/search?q={query}&first={first}&count=10"

            html = self.req.get(url)
            if html:
                found = self._extract_urls_from_html(html)
                new = found - all_urls
                all_urls.update(found)
                dlog.debug(f"Bing page {page}: {len(new)} new URLs")
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        dlog.log_dork("Bing", dork, len(all_urls))
        return all_urls

    def search_all_engines(self, dorks: List[str]) -> List[str]:
        """Executa todas as dorks em todos os engines com filtro."""
        all_urls = set()
        filtered_count = 0
        total_raw = 0

        for i, dork in enumerate(dorks):
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"  {ts} {C}[-]{RST} Dork [{i+1}/{len(dorks)}]: {dork[:60]}...")
            dlog.log_phase(f"DORK {i+1}/{len(dorks)}", dork[:80])

            # DuckDuckGo (principal - mais confiável)
            raw_urls = self.search_duckduckgo(dork)
            total_raw += len(raw_urls)

            # Google (secundário)
            try:
                g_urls = self.search_google(dork, max_pages=1)
                raw_urls.update(g_urls)
                total_raw += len(g_urls)
            except Exception as e:
                dlog.error(f"Google error: {e}")

            # Bing (terciário)
            try:
                b_urls = self.search_bing(dork, max_pages=1)
                raw_urls.update(b_urls)
                total_raw += len(b_urls)
            except Exception as e:
                dlog.error(f"Bing error: {e}")

            # Filtrar URLs (CAMADA 1)
            for url in raw_urls:
                is_valid, reason = self.url_filter.is_valid(url)
                if is_valid:
                    all_urls.add(url)
                else:
                    filtered_count += 1
                    dlog.log_filter(url, reason)

            ts = datetime.now().strftime("%H:%M:%S")
            print(f"  {ts} {G}[+]{RST}   -> {len(raw_urls)} raw, {filtered_count} filtradas, {len(all_urls)} válidas acumuladas")

        # Dedup por domínio (manter apenas 1 URL por domínio)
        seen_domains = {}
        for url in all_urls:
            try:
                domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
            except Exception:
                domain = url
            if domain not in seen_domains:
                seen_domains[domain] = url
            else:
                # Preferir URL mais curta (geralmente homepage)
                if len(url) < len(seen_domains[domain]):
                    seen_domains[domain] = url

        unique_urls = list(seen_domains.values())
        dlog.info(f"DORK SUMMARY | raw={total_raw} | filtered={filtered_count} | valid={len(all_urls)} | unique_domains={len(unique_urls)}")
        print(f"\n  {G}[+]{RST} Total URLs únicas (por domínio): {W}{len(unique_urls)}{RST}")

        return unique_urls



# ══════════════════════════════════════════════════════════════════
#                    SITE ANALYZER (CAMADAS 2 e 3)
# ══════════════════════════════════════════════════════════════════

class SiteAnalyzer:
    """Analisa sites para confirmar gateway e validar se é loja real."""

    def __init__(self, requester: SmartRequester, gateway_config: Dict):
        self.req = requester
        self.gw = gateway_config
        self.js_sigs = gateway_config.get("js_signatures", [])
        self.text_sigs = gateway_config.get("text_signatures", [])

    def _extract_title(self, html: str) -> str:
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
        return m.group(1).strip()[:200] if m else "N/A"

    def _extract_description(self, html: str) -> str:
        m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I | re.S)
        if not m:
            m = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.I | re.S)
        return m.group(1).strip()[:300] if m else "N/A"

    def _extract_keywords(self, html: str) -> str:
        m = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\'](.*?)["\']', html, re.I | re.S)
        return m.group(1).strip()[:300] if m else "N/A"

    def _extract_emails(self, html: str) -> List[str]:
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))
        # Filtrar emails falsos/de exemplo
        fake_patterns = ["example", "test", "sample", "noreply", "no-reply",
                         "avengers", "sandbox", "placeholder", "email@"]
        return [e for e in emails if not any(f in e.lower() for f in fake_patterns)][:5]

    def _extract_phones(self, html: str) -> List[str]:
        # Buscar telefones brasileiros reais
        phones = set()
        patterns = [
            r'\(?\d{2}\)?\s*\d{4,5}[-.\s]?\d{4}',
            r'\+55\s*\(?\d{2}\)?\s*\d{4,5}[-.\s]?\d{4}',
        ]
        for pat in patterns:
            for m in re.finditer(pat, html):
                phone = re.sub(r'[^\d+]', '', m.group())
                if 10 <= len(phone.replace('+', '')) <= 13:
                    phones.add(m.group().strip())
        return list(phones)[:5]

    def _detect_platform(self, html: str) -> str:
        """Detecta plataforma e-commerce."""
        html_lower = html.lower()
        platforms = [
            ("WooCommerce", ["woocommerce", "wc-cart", "wc-ajax", "wp-content/plugins/woocommerce"]),
            ("Shopify", ["cdn.shopify.com", "shopify.com/s/", "myshopify.com"]),
            ("VTEX", ["vtex.com", "vteximg.com.br", "vtexcommerce"]),
            ("Nuvemshop", ["nuvemshop", "tiendanube", "lojaintegrada"]),
            ("Tray", ["tray.com.br", "traycorp"]),
            ("Magento", ["magento", "mage-", "varien"]),
            ("PrestaShop", ["prestashop", "presta"]),
            ("OpenCart", ["opencart", "route=product"]),
            ("Loja Integrada", ["lojaintegrada.com.br"]),
            ("Yampi", ["yampi.com.br", "yampi.io"]),
            ("CartPanda", ["cartpanda.com"]),
            ("Dooca", ["dooca.com.br"]),
            ("Bagy", ["bagy.com.br"]),
        ]
        for name, sigs in platforms:
            if any(s in html_lower for s in sigs):
                return name
        return "Desconhecida"

    def _detect_technologies(self, html: str) -> List[str]:
        """Detecta tecnologias usadas no site."""
        html_lower = html.lower()
        techs = []
        tech_sigs = {
            "WordPress": ["wp-content", "wp-includes", "wordpress"],
            "React": ["react.js", "react.min.js", "_next/static", "react-dom"],
            "Vue.js": ["vue.js", "vue.min.js", "vuejs"],
            "Bootstrap": ["bootstrap.min.css", "bootstrap.min.js"],
            "Tailwind CSS": ["tailwindcss", "tailwind.min.css"],
            "jQuery": ["jquery.min.js", "jquery-"],
            "Google Analytics": ["google-analytics.com", "gtag/js", "analytics.js"],
            "Google Tag Manager": ["googletagmanager.com", "gtm.js"],
            "Facebook Pixel": ["connect.facebook.net", "fbevents.js", "fbq("],
            "Hotjar": ["hotjar.com", "hj("],
            "Cloudflare": ["cloudflare.com", "cf-ray", "__cf_bm"],
            "reCAPTCHA": ["recaptcha", "grecaptcha"],
            "Laravel": ["laravel", "csrf-token"],
            "Next.js": ["_next/", "next/"],
        }
        for name, sigs in tech_sigs.items():
            if any(s in html_lower for s in sigs):
                techs.append(name)
        return techs

    def _confirm_gateway_in_html(self, html: str) -> Tuple[bool, List[str]]:
        """
        CAMADA 2: Confirma presença da gateway no HTML.
        Busca assinaturas JS em tags script, iframe, form - NÃO em texto livre.
        """
        html_lower = html.lower()
        matches = []

        # Buscar assinaturas JS em tags técnicas (script src, iframe src, form action)
        technical_zones = []
        # Extrair src de tags script
        for m in re.finditer(r'<script[^>]*src=["\']([^"\'>]+)["\']', html_lower):
            technical_zones.append(m.group(1))
        # Extrair conteúdo inline de tags script
        for m in re.finditer(r'<script[^>]*>(.*?)</script>', html_lower, re.S):
            if m.group(1).strip():
                technical_zones.append(m.group(1))
        # Extrair src de iframes
        for m in re.finditer(r'<iframe[^>]*src=["\']([^"\']+)["\']', html_lower):
            technical_zones.append(m.group(1))
        # Extrair action de forms
        for m in re.finditer(r'<form[^>]*action=["\']([^"\']+)["\']', html_lower):
            technical_zones.append(m.group(1))
        # Extrair links de CSS/JS
        for m in re.finditer(r'<link[^>]*href=["\']([^"\']+)["\']', html_lower):
            technical_zones.append(m.group(1))
        # Extrair data attributes
        for m in re.finditer(r'data-[a-z-]+=["\']([^"\']+)["\']', html_lower):
            technical_zones.append(m.group(1))

        tech_text = " ".join(technical_zones)

        # Verificar assinaturas JS nas zonas técnicas
        for sig in self.js_sigs:
            if sig.lower() in tech_text:
                matches.append(f"JS:{sig}")

        # Se não encontrou nas zonas técnicas, verificar no HTML inteiro
        # mas com peso menor (apenas text_signatures)
        if not matches:
            for sig in self.text_sigs:
                sig_lower = sig.lower()
                # Contar ocorrências - precisa de pelo menos 3 para ser relevante
                count = html_lower.count(sig_lower)
                if count >= 3:
                    matches.append(f"TEXT({count}x):{sig}")

        confirmed = len(matches) > 0
        dlog.debug(f"GATEWAY CHECK | confirmed={confirmed} | matches={matches}")
        return confirmed, matches

    def _validate_real_store(self, html: str, url: str) -> Tuple[bool, int, List[str]]:
        """
        CAMADA 3: Valida se o site é uma LOJA REAL usando score.
        Retorna (is_store, score, signals).
        """
        html_lower = html.lower()
        score = 0
        signals = []

        # ── SINAIS POSITIVOS (loja real) ──

        # Preços em Real
        price_patterns = [
            r'R\$\s*\d+[.,]\d{2}', r'BRL\s*\d+', r'data-price',
            r'class="[^"]*price[^"]*"', r'class="[^"]*preco[^"]*"',
        ]
        for pat in price_patterns:
            if re.search(pat, html, re.I):
                score += 5
                signals.append(f"+5:price_pattern:{pat[:30]}")
                break

        # Botões de compra
        buy_terms = [
            "comprar agora", "adicionar ao carrinho", "add to cart",
            "buy now", "comprar", "adicionar à sacola", "add to bag",
            "finalizar compra", "ir para o checkout",
        ]
        for term in buy_terms:
            if term in html_lower:
                score += 5
                signals.append(f"+5:buy_button:{term}")
                break

        # Carrinho de compras
        cart_terms = [
            "carrinho", "sacola", "cart", "basket", "bag",
            "meu-carrinho", "my-cart", "shopping-cart",
        ]
        cart_found = sum(1 for t in cart_terms if t in html_lower)
        if cart_found >= 2:
            score += 4
            signals.append(f"+4:cart_terms({cart_found})")

        # Produtos/catálogo
        product_terms = [
            "produto", "product", "catálogo", "catalog",
            "categoria", "category", "departamento",
        ]
        prod_found = sum(1 for t in product_terms if t in html_lower)
        if prod_found >= 2:
            score += 3
            signals.append(f"+3:product_terms({prod_found})")

        # Frete/envio
        shipping_terms = [
            "frete", "entrega", "shipping", "delivery", "envio",
            "calcular frete", "cep", "correios", "sedex",
        ]
        if any(t in html_lower for t in shipping_terms):
            score += 3
            signals.append("+3:shipping")

        # Plataforma e-commerce detectada
        platform = self._detect_platform(html)
        if platform != "Desconhecida":
            score += 4
            signals.append(f"+4:platform:{platform}")

        # Tamanhos/variações de produto
        size_terms = ["tamanho", "size", "cor", "color", "variação", "variation",
                      "quantidade", "quantity", "estoque", "stock"]
        if any(t in html_lower for t in size_terms):
            score += 2
            signals.append("+2:product_variations")

        # Avaliações de produto
        review_terms = ["avaliação", "review", "estrela", "star", "rating",
                        "comentário de cliente", "customer review"]
        if any(t in html_lower for t in review_terms):
            score += 2
            signals.append("+2:reviews")

        # Formas de pagamento mencionadas
        payment_terms = ["cartão de crédito", "boleto", "pix", "credit card",
                         "parcelamento", "parcelas", "installment"]
        pay_found = sum(1 for t in payment_terms if t in html_lower)
        if pay_found >= 2:
            score += 3
            signals.append(f"+3:payment_methods({pay_found})")

        # ── SINAIS NEGATIVOS (não é loja) ──

        # Documentação/API
        doc_terms = ["api reference", "api documentation", "endpoint",
                     "request body", "response body", "curl -x",
                     "sdk", "npm install", "pip install", "composer require",
                     "getting started", "quick start", "integration guide"]
        doc_found = sum(1 for t in doc_terms if t in html_lower)
        if doc_found >= 2:
            score -= 15
            signals.append(f"-15:documentation({doc_found})")

        # Blog/artigo
        blog_terms = ["publicado em", "published on", "author:", "autor:",
                      "leia mais", "read more", "artigo", "article",
                      "compartilhar", "share this", "tags:", "categorias:"]
        blog_found = sum(1 for t in blog_terms if t in html_lower)
        if blog_found >= 3:
            score -= 10
            signals.append(f"-10:blog_article({blog_found})")

        # Tutorial/how-to
        tutorial_terms = ["como configurar", "how to", "passo a passo",
                          "step by step", "tutorial", "guia de",
                          "configuração", "setup guide"]
        if any(t in html_lower for t in tutorial_terms):
            score -= 8
            signals.append("-8:tutorial")

        # Suporte/help center
        support_terms = ["base de conhecimento", "knowledge base",
                         "central de ajuda", "help center",
                         "ticket de suporte", "support ticket",
                         "faq", "perguntas frequentes"]
        if any(t in html_lower for t in support_terms):
            score -= 8
            signals.append("-8:support_center")

        # Comparativo/review de serviço
        compare_terms = ["comparativo", "comparison", "melhor gateway",
                         "best payment", "alternativas", "alternatives",
                         "prós e contras", "pros and cons", "vantagens e desvantagens"]
        if any(t in html_lower for t in compare_terms):
            score -= 8
            signals.append("-8:comparison_article")

        # Fórum/comunidade
        forum_terms = ["responder tópico", "reply to topic", "membro desde",
                       "member since", "postado em", "posted on",
                       "solução aceita", "accepted solution"]
        if any(t in html_lower for t in forum_terms):
            score -= 10
            signals.append("-10:forum")

        is_store = score >= STORE_SCORE_THRESHOLD
        dlog.log_store_validation(url, score, signals, is_store)
        return is_store, score, signals

    def _classify_category(self, html: str, title: str, desc: str) -> str:
        """Classifica o nicho/categoria da loja."""
        text = f"{title} {desc} {html[:5000]}".lower()
        best_cat = "Loja Online / E-commerce"
        best_score = 0

        for cat_id, cat_info in SITE_CATEGORIES.items():
            score = sum(1 for kw in cat_info["keywords"] if kw.lower() in text)
            if score > best_score:
                best_score = score
                best_cat = cat_info["label"]

        return best_cat

    def analyze(self, url: str) -> Dict[str, Any]:
        """Análise completa de um site."""
        result = {
            "url": url,
            "domain": "",
            "title": "N/A",
            "description": "N/A",
            "keywords": "N/A",
            "category": "N/A",
            "status": "ERRO",
            "gateway_confirmed": False,
            "gateway_matches": [],
            "is_real_store": False,
            "store_score": 0,
            "store_signals": [],
            "platform": "N/A",
            "technologies": [],
            "ssl": url.startswith("https"),
            "emails": [],
            "phones": [],
            "html_size": 0,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            domain = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
            result["domain"] = domain

            html = self.req.get(url)
            if not html:
                result["status"] = "FALHA_REQUEST"
                dlog.log_analysis(url, False, "N/A", "no_html", "request_failed")
                return result

            result["html_size"] = len(html)
            result["title"] = self._extract_title(html)
            result["description"] = self._extract_description(html)
            result["keywords"] = self._extract_keywords(html)
            result["emails"] = self._extract_emails(html)
            result["phones"] = self._extract_phones(html)
            result["platform"] = self._detect_platform(html)
            result["technologies"] = self._detect_technologies(html)

            # CAMADA 2: Confirmar gateway
            confirmed, matches = self._confirm_gateway_in_html(html)
            result["gateway_confirmed"] = confirmed
            result["gateway_matches"] = matches

            if confirmed:
                # CAMADA 3: Validar se é loja real
                is_store, score, signals = self._validate_real_store(html, url)
                result["is_real_store"] = is_store
                result["store_score"] = score
                result["store_signals"] = signals

                if is_store:
                    result["status"] = "LOJA_CONFIRMADA"
                    result["category"] = self._classify_category(html, result["title"], result["description"])
                else:
                    result["status"] = "GATEWAY_SIM_LOJA_NAO"
                    result["category"] = "Não é loja (score: {})".format(score)
            else:
                result["status"] = "GATEWAY_NAO_ENCONTRADA"

            dlog.log_analysis(url, confirmed, result["category"], matches)

        except Exception as e:
            result["status"] = f"ERRO: {str(e)[:80]}"
            dlog.log_analysis(url, False, "N/A", "error", str(e))

        return result



# ══════════════════════════════════════════════════════════════════
#                    REPORT GENERATOR
# ══════════════════════════════════════════════════════════════════

class ReportGenerator:
    """Gera relatórios ultra detalhados em múltiplos formatos."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_all(self, gateway_name: str, results: List[Dict], stats: Dict, elapsed: float) -> Dict[str, str]:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"gatehunter_{gateway_name.lower()}_{ts}"
        files = {}

        # Separar resultados
        stores = [r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")]
        gw_only = [r for r in results if r.get("gateway_confirmed") and not r.get("is_real_store")]
        failed = [r for r in results if not r.get("gateway_confirmed")]

        # TXT detalhado
        txt_path = os.path.join(self.output_dir, f"{prefix}.txt")
        self._write_txt(txt_path, gateway_name, stores, gw_only, failed, stats, elapsed)
        files["TXT"] = txt_path

        # JSON
        json_path = os.path.join(self.output_dir, f"{prefix}.json")
        self._write_json(json_path, gateway_name, results, stats, elapsed)
        files["JSON"] = json_path

        # URLs (apenas lojas confirmadas)
        urls_path = os.path.join(self.output_dir, f"{prefix}_LOJAS.txt")
        self._write_stores_list(urls_path, stores)
        files["LOJAS"] = urls_path

        # Todas URLs
        all_urls_path = os.path.join(self.output_dir, f"{prefix}_all_urls.txt")
        self._write_all_urls(all_urls_path, results)
        files["ALL_URLS"] = all_urls_path

        dlog.log_report(files)
        return files

    def _write_txt(self, path, gw, stores, gw_only, failed, stats, elapsed):
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("     GATEHUNTER v4.0 - NETHUNTER SUPREME EDITION - RELATORIO\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"  Gateway Alvo     : {gw}\n")
            f.write(f"  Data/Hora        : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"  Tempo de Scan    : {elapsed:.1f} segundos\n")
            f.write(f"  URLs Analisadas  : {len(stores) + len(gw_only) + len(failed)}\n")
            f.write(f"  LOJAS REAIS      : {len(stores)}\n")
            f.write(f"  Gateway s/ Loja  : {len(gw_only)}\n")
            f.write(f"  Sem Gateway      : {len(failed)}\n")
            f.write(f"  Requests Total   : {stats.get('requests', 0)}\n")
            f.write(f"  Requests OK      : {stats.get('success', 0)}\n")
            f.write(f"  Bloqueios (429)  : {stats.get('blocked', 0)}\n\n")

            if stores:
                f.write("=" * 80 + "\n")
                f.write(f"  LOJAS REAIS CONFIRMADAS COM {gw.upper()} ({len(stores)})\n")
                f.write("=" * 80 + "\n\n")
                for i, r in enumerate(stores, 1):
                    f.write(f"  [{i:03d}] {'='*68}\n")
                    f.write(f"  URL            : {r['url']}\n")
                    f.write(f"  Dominio        : {r['domain']}\n")
                    f.write(f"  Titulo         : {r['title']}\n")
                    f.write(f"  Descricao      : {r['description'][:200]}\n")
                    f.write(f"  Categoria      : {r['category']}\n")
                    f.write(f"  Store Score    : {r['store_score']}\n")
                    f.write(f"  Status         : {r['status']}\n")
                    f.write(f"  Gateway Match  : {', '.join(r['gateway_matches'])}\n")
                    f.write(f"  Plataforma     : {r['platform']}\n")
                    f.write(f"  Tecnologias    : {', '.join(r['technologies'][:8])}\n")
                    f.write(f"  SSL            : {'Sim' if r['ssl'] else 'Nao'}\n")
                    f.write(f"  Emails         : {', '.join(r['emails']) if r['emails'] else 'N/A'}\n")
                    f.write(f"  Telefones      : {', '.join(r['phones']) if r['phones'] else 'N/A'}\n")
                    f.write(f"  HTML Size      : {r['html_size']:,} bytes\n")
                    f.write(f"  Analisado em   : {r['analyzed_at']}\n")
                    f.write(f"  Keywords       : {r['keywords'][:150]}\n\n")

            if gw_only:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"  SITES COM GATEWAY MAS NAO SAO LOJAS ({len(gw_only)})\n")
                f.write("=" * 80 + "\n\n")
                for i, r in enumerate(gw_only, 1):
                    f.write(f"  [{i:03d}] {r['url']}\n")
                    f.write(f"         Titulo: {r['title'][:80]}\n")
                    f.write(f"         Score: {r['store_score']} | Motivo: {r['category']}\n\n")

    def _write_json(self, path, gw, results, stats, elapsed):
        data = {
            "version": VERSION,
            "gateway": gw,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "stats": stats,
            "total_results": len(results),
            "stores_found": len([r for r in results if r.get("is_real_store")]),
            "results": results,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _write_stores_list(self, path, stores):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# GateHunter v{VERSION} - LOJAS CONFIRMADAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(stores)}\n\n")
            for r in stores:
                f.write(f"{r['url']} | {r['title'][:60]} | {r['category']} | Score:{r['store_score']}\n")

    def _write_all_urls(self, path, results):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# GateHunter v{VERSION} - TODAS URLs - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(results)}\n\n")
            for r in results:
                f.write(f"{r['url']} | {r['status']}\n")


# ══════════════════════════════════════════════════════════════════
#                    BANNER & INTERFACE
# ══════════════════════════════════════════════════════════════════

def print_banner():
    banner = f"""
{R}╔══════════════════════════════════════════════════════════════════╗{RST}
{R}║{RST}  {C}  ██████╗  █████╗ ████████╗███████╗{RST}                             {R}║{RST}
{R}║{RST}  {C} ██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝{RST}                             {R}║{RST}
{R}║{RST}  {C} ██║  ███╗███████║   ██║   █████╗  {RST}                              {R}║{RST}
{R}║{RST}  {C} ██║   ██║██╔══██║   ██║   ██╔══╝  {RST}                              {R}║{RST}
{R}║{RST}  {C} ╚██████╔╝██║  ██║   ██║   ███████╗{RST}                              {R}║{RST}
{R}║{RST}  {C}  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝{RST}                              {R}║{RST}
{R}║{RST}  {Y} ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ {RST}           {R}║{RST}
{R}║{RST}  {Y} ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗{RST}           {R}║{RST}
{R}║{RST}  {Y} ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝{RST}           {R}║{RST}
{R}║{RST}  {Y} ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗{RST}           {R}║{RST}
{R}║{RST}  {Y} ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║{RST}           {R}║{RST}
{R}║{RST}  {Y} ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝{RST}           {R}║{RST}
{R}╚══════════════════════════════════════════════════════════════════╝{RST}

  {W}v{VERSION}{RST} // {M}NETHUNTER SUPREME EDITION{RST} // {G}Payment Gateway OSINT{RST}
"""
    print(banner)

    # Info box
    print(f"  {D}┌──────────────────────────────────────────────────────────┐{RST}")
    print(f"  {D}│{RST} Engine  : {G}curl_cffi Impersonate + Multi-Thread + Proxy{RST}    {D}│{RST}")
    print(f"  {D}│{RST} Evasion : {G}TLS Fingerprint + Header Spoof + UA Rotation{RST}   {D}│{RST}")
    print(f"  {D}│{RST} Search  : {G}DuckDuckGo + Google + Bing (Multi-Engine){RST}      {D}│{RST}")
    print(f"  {D}│{RST} Filter  : {G}3-Layer Validation (URL + Gateway + Store){RST}     {D}│{RST}")
    print(f"  {D}│{RST} Output  : {G}{OUTPUT_DIR}/ (TXT + JSON + LOJAS){RST}       {D}│{RST}")
    print(f"  {D}│{RST} Logs    : {G}{LOG_PATH}{RST}  {D}│{RST}")
    print(f"  {D}└──────────────────────────────────────────────────────────┘{RST}")


def print_menu(proxy_count: int):
    print(f"\n  {D}┌─────────────────────────────────────────┐{RST}")
    print(f"  {D}│{RST}  {W}CONFIGURACAO ATIVA{RST}                      {D}│{RST}")
    print(f"  {D}├─────────────────────────────────────────┤{RST}")
    print(f"  {D}│{RST}  Proxies Carregadas  :  {G}{proxy_count}{RST}               {D}│{RST}")
    print(f"  {D}│{RST}  Threads             :  {G}{MAX_THREADS}{RST}              {D}│{RST}")
    print(f"  {D}│{RST}  Timeout             :  {G}{REQUEST_TIMEOUT}s{RST}             {D}│{RST}")
    print(f"  {D}│{RST}  curl_cffi           :  {G if CFFI_OK else R}{'OK' if CFFI_OK else 'FALHA'}{RST}              {D}│{RST}")
    print(f"  {D}│{RST}  Engines             :  {G}DDG + Google + Bing{RST}  {D}│{RST}")
    print(f"  {D}│{RST}  Store Threshold     :  {G}>= {STORE_SCORE_THRESHOLD} pontos{RST}        {D}│{RST}")
    print(f"  {D}└─────────────────────────────────────────┘{RST}")

    print(f"\n  {D}┌─────────────────────────────────────────────────────────┐{RST}")
    print(f"  {D}│{RST}  {W}SELECIONE A GATEWAY DE PAGAMENTO{RST}                        {D}│{RST}")
    print(f"  {D}├─────────────────────────────────────────────────────────┤{RST}")
    for key, gw in sorted(GATEWAYS.items(), key=lambda x: int(x[0])):
        num = f"[{key:>2}]"
        name = gw["name"].ljust(16)
        desc = gw["description"][:45]
        print(f"  {D}│{RST}  {C}{num}{RST}  {W}{name}{RST} {desc}{D}│{RST}")
    print(f"  {D}├─────────────────────────────────────────────────────────┤{RST}")
    print(f"  {D}│{RST}  {Y}[ 0]{RST}  CUSTOM - Inserir gateway personalizada             {D}│{RST}")
    print(f"  {D}│{RST}  {R}[99]{RST}  SAIR                                               {D}│{RST}")
    print(f"  {D}└─────────────────────────────────────────────────────────┘{RST}")


# ══════════════════════════════════════════════════════════════════
#                     GATEHUNTER MAIN CLASS
# ══════════════════════════════════════════════════════════════════

class GateHunter:
    """Classe principal do GateHunter."""

    def __init__(self):
        self.proxy = ProxyRotator()
        self.fp = FingerprintGenerator()
        self.req = SmartRequester(self.proxy, self.fp)
        # Determinar output dir
        self.output_dir = OUTPUT_DIR
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            test_file = os.path.join(self.output_dir, ".test_write")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except (PermissionError, OSError):
            self.output_dir = FALLBACK_OUTPUT
            os.makedirs(self.output_dir, exist_ok=True)
        self.report = ReportGenerator(self.output_dir)
        dlog.info(f"GateHunter initialized | output={self.output_dir} | proxies={self.proxy.count}")

    def _execute_scan(self, gateway_config: Dict):
        """Executa o scan completo para uma gateway."""
        gw_name = gateway_config["name"]
        dorks = gateway_config["dorks"]
        dlog.log_scan_start(gw_name, dorks, gateway_config.get("js_signatures", []), self.proxy.count)

        print(f"\n{'='*70}")
        print(f"  {M}INICIANDO SCAN: {W}{gw_name}{RST}")
        print(f"{'='*70}\n")

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  {ts} {G}[*]{RST} Gateway: {W}{gw_name}{RST}")
        print(f"  {ts} {G}[*]{RST} Dorks: {W}{len(dorks)}{RST}")
        print(f"  {ts} {G}[*]{RST} JS Signatures: {W}{', '.join(gateway_config.get('js_signatures', [])[:3])}{RST}")
        print(f"  {ts} {G}[*]{RST} Proxies: {W}{self.proxy.count}{RST}")
        print(f"  {ts} {G}[*]{RST} Threads: {W}{MAX_THREADS}{RST}")
        print(f"  {ts} {G}[*]{RST} Store Threshold: {W}>= {STORE_SCORE_THRESHOLD}{RST}")

        t0 = time.time()

        # FASE 1: Coletar URLs via Dorks
        dlog.log_phase("1/3", "Coletando URLs via Dorks (Multi-Engine)")
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n  {ts} {C}[-]{RST} FASE 1/3: Coletando URLs via Dorks (Multi-Engine)...")

        url_filter = URLFilter(gateway_config)
        dork_engine = DorkEngine(self.req, url_filter)
        urls = dork_engine.search_all_engines(dorks)

        if not urls:
            print(f"\n  {R}[!]{RST} Nenhuma URL encontrada. Tente novamente ou use outra gateway.")
            dlog.warn("No URLs found after dork search")
            return

        # FASE 2: Analisar sites
        dlog.log_phase("2/3", f"Analisando {len(urls)} sites ({MAX_THREADS} threads)")
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n  {ts} {C}[-]{RST} FASE 2/3: Analisando {W}{len(urls)}{RST} sites ({MAX_THREADS} threads)...")

        analyzer = SiteAnalyzer(self.req, gateway_config)
        results = []
        stores_count = 0

        with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="Analyzer") as pool:
            futures = {pool.submit(analyzer.analyze, url): url for url in urls}
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result(timeout=60)
                    results.append(result)

                    ts = datetime.now().strftime("%H:%M:%S")
                    status_icon = ""
                    status_text = ""

                    if result.get("is_real_store") and result.get("gateway_confirmed"):
                        stores_count += 1
                        status_icon = f"{G}LOJA REAL"
                        status_text = f"{result['category']}"
                    elif result.get("gateway_confirmed"):
                        status_icon = f"{Y}GATEWAY OK"
                        status_text = f"Score:{result['store_score']} (não é loja)"
                    else:
                        status_icon = f"{R}SEM GATEWAY"
                        status_text = ""

                    domain = result.get("domain", "?")[:35]
                    print(f"  {ts} {C}[{i}/{len(urls)}]{RST} {status_icon}{RST} {W}{domain}{RST} | {status_text}")

                except Exception as e:
                    dlog.error(f"Future error for {futures[future]}: {e}")

        elapsed = time.time() - t0

        # FASE 3: Gerar relatórios
        dlog.log_phase("3/3", "Gerando relatórios")
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n  {ts} {C}[-]{RST} FASE 3/3: Gerando relatórios...")

        files = self.report.generate_all(gw_name, results, self.req.stats, elapsed)

        dlog.log_scan_end(gw_name, results, self.req.stats, elapsed)

        # Resumo final
        stores = [r for r in results if r.get("is_real_store") and r.get("gateway_confirmed")]
        gw_only = [r for r in results if r.get("gateway_confirmed") and not r.get("is_real_store")]

        print(f"\n{'='*70}")
        print(f"  {G}SCAN COMPLETO!{RST}")
        print(f"{'='*70}")
        print(f"  Gateway          : {C}{gw_name}{RST}")
        print(f"  Tempo total      : {W}{elapsed:.1f}s{RST}")
        print(f"  URLs analisadas  : {W}{len(results)}{RST}")
        print(f"  {G}LOJAS REAIS      : {W}{len(stores)}{RST}")
        print(f"  {Y}Gateway s/ Loja  : {W}{len(gw_only)}{RST}")
        print(f"  Requests total   : {W}{self.req.stats.get('requests', 0)}{RST}")
        print(f"  Bloqueios        : {W}{self.req.stats.get('blocked', 0)}{RST}")

        print(f"\n  Arquivos gerados:")
        for fmt, path in files.items():
            size = os.path.getsize(path) if os.path.exists(path) else 0
            print(f"  {C}[-]{RST}   {fmt:>8} = {path} ({size:,} bytes)")

        print(f"\n  {G}Debug Log: {dlog.log_path}{RST}")

        if stores:
            print(f"\n  {G}TOP LOJAS REAIS CONFIRMADAS:{RST}\n")
            for i, r in enumerate(stores[:20], 1):
                cat = r["category"][:35].ljust(35)
                domain = r["domain"][:30].ljust(30)
                print(f"  {W}{i:>3}.{RST} {C}{domain}{RST} | {G}{cat}{RST} | Score:{r['store_score']}")

        # Categorias
        if stores:
            cats = {}
            for r in stores:
                c = r["category"]
                cats[c] = cats.get(c, 0) + 1
            print(f"\n  {M}CATEGORIAS:{RST}")
            for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                bar = "█" * min(count * 2, 40)
                print(f"  {cat[:35].ljust(35)} {W}{count:>3}{RST} {G}{bar}{RST}")

        print(f"\n{'='*70}")

    def run(self):
        """Loop principal do menu."""
        print_banner()

        while True:
            print_menu(self.proxy.count)
            try:
                choice = input(f"\n  {C}GateHunter > {RST}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n  {Y}[!] Saindo...{RST}")
                break

            if choice == "99":
                print(f"\n  {Y}[!] Saindo... Até a próxima!{RST}")
                break

            if choice == "0":
                # Custom gateway
                try:
                    name = input(f"  {C}Nome da gateway: {RST}").strip()
                    sigs = input(f"  {C}Assinaturas JS (separadas por vírgula): {RST}").strip()
                    own = input(f"  {C}Domínios da gateway (separados por vírgula): {RST}").strip()

                    if not name or not sigs:
                        print(f"  {R}[!] Nome e assinaturas são obrigatórios!{RST}")
                        continue

                    sig_list = [s.strip() for s in sigs.split(",")]
                    own_list = [o.strip() for o in own.split(",") if o.strip()]

                    # Gerar dorks automaticamente
                    custom_dorks = []
                    for sig in sig_list[:3]:
                        custom_dorks.append(f'intext:"{sig}" -site:github.com -blog -docs -tutorial')
                        custom_dorks.append(f'intext:"{sig}" intext:"comprar" intext:"R$" -blog')
                    for o in own_list[:2]:
                        custom_dorks.append(f'intext:"{name.lower()}" intext:"carrinho" -site:{o} -blog -docs')

                    custom_gw = {
                        "name": name,
                        "description": f"{name} - Gateway personalizada",
                        "js_signatures": sig_list,
                        "text_signatures": [name.lower()],
                        "own_domains": own_list,
                        "dorks": custom_dorks,
                    }
                    self._execute_scan(custom_gw)
                except (KeyboardInterrupt, EOFError):
                    continue

            elif choice in GATEWAYS:
                self._execute_scan(GATEWAYS[choice])
            else:
                print(f"  {R}[!] Opção inválida!{RST}")

            input(f"\n  {D}Pressione Enter para voltar ao menu...{RST}")
            # Reset stats
            self.req.stats = {"requests": 0, "success": 0, "failed": 0, "blocked": 0}


# ══════════════════════════════════════════════════════════════════
#                          MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    # Handle SIGINT gracefully
    signal.signal(signal.SIGINT, lambda s, f: (print(f"\n  {Y}[!] Interrompido pelo usuário.{RST}"), sys.exit(0)))

    try:
        hunter = GateHunter()
        hunter.run()
    except Exception as e:
        dlog.critical(f"Fatal error: {e}")
        dlog.exception("Traceback:")
        print(f"\n  {R}[!] Erro fatal: {e}{RST}")
        print(f"  {Y}[!] Verifique o log: {dlog.log_path}{RST}")
        sys.exit(1)


if __name__ == "__main__":
    main()
