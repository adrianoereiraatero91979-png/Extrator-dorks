# Changelog - GateHunter

## v6.0.0 (2026-03-23) - Multi-Engine + Niche Filter + Brave Search

### Novidades
- **Brave Search** como engine principal (retorna 20+ URLs por dork, muito mais confiavel que DDG)
- **Filtro por Nicho**: sub-menu para selecionar tipo de loja (Roupas, Eletronicos, Gift Card, Pet Shop, Joias, Cosmeticos, Suplementos, etc)
- **15 nichos** disponiveis com termos de busca automaticos que expandem as dorks
- **Dorks expandidas**: termos de nicho sao combinados com dorks base automaticamente (ex: "pagar.me loja comprar roupas")
- **Debug log completo** salvo em `/sdcard/nh_files/logs_gate_hunter.txt` com timestamp, level, thread e detalhes

### Correcoes
- **Engine Brave**: substitui DDG (que retornava 202) pelo Brave Search que funciona consistentemente
- **Parser Brave**: extrai URLs corretamente do HTML do Brave Search com filtro de dominios internos
- **Filtro anti-falso-positivo**: blacklist expandida para 96+ dominios incluindo plataformas e-commerce (nuvemshop, tray, lojaintegrada, etc)
- **Store Score refinado**: 16 sinais positivos (preco R$, carrinho, checkout, frete, CEP, estoque, variacao, parcelamento, etc) e 11 sinais negativos (docs, tutorial, blog, SDK, API, changelog, etc)
- **Gateway detection em 5 zonas**: script src, iframe, form action, links, texto contextual
- **Dedup por dominio**: apenas 1 URL por dominio para evitar duplicatas
- **Delay inteligente**: 4-8s entre buscas + 15s de espera em rate limit para evitar bloqueio

### Engines de Busca
- Brave Search (principal - melhor taxa de sucesso)
- DuckDuckGo HTML (backup - funciona bem no NetHunter com IP direto)
- Bing (complementar)
- Google CSE API (opcional - 100 buscas/dia gratis)

---

## v5.0.0 (2026-03-23) - Multi-Engine Revolution

### Correcoes
- Falsos positivos eliminados (v4 retornava 34/38 como SaaS/Software)
- Dorks reformuladas sem operadores avancados
- DDG Lite 202 corrigido (usa DDG HTML sem proxy)
- Debug logs salvando em `/sdcard/nh_files/logs_gate_hunter.txt`

### Novidades
- Multi-Engine v5: DDG HTML + Google + Bing + Google CSE API
- Busca SEM proxy (IP direto do celular)
- Blacklist massiva: 152+ dominios
- Google CSE API suporte opcional

---

## v4.0.0 (2026-03-23) - 3-Layer Validation

### Novidades
- Dorks por assinatura JS
- Blacklist massiva de dominios
- Validacao em 3 camadas
- Debug logs

---

## v2.0.0 (2026-03-23) - Initial Release

### Funcionalidades
- Menu interativo com 15 gateways
- Multi-engine: DDG + Google + Bing
- curl_cffi com TLS impersonate
- Proxy rotator
- Relatorios TXT, JSON e URLs
