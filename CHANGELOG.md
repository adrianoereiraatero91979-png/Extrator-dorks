# Changelog - GateHunter

## v6.1.0 (2026-03-23) - Ambiguous Gateway + Anti False Positive

### Problemas Corrigidos
- **Falsos positivos com gateways ambiguas**: Sites como nuancielo.com.br (marca "Nuancielo"), giraofertas.com.br/el-cielo (perfume "El Cielo"), ldelinda.com.br/produtos-cielo (cosmeticos "Cielo") eram confirmados incorretamente como tendo a gateway Cielo
- **Sites de plugins/modulos**: loja5.com.br que vende plugin de Cielo era confirmado como loja que USA Cielo
- **Sites de cupons/desconto**: desconto.com.br passava pelo filtro
- **Documentacao**: developercielo.github.io passava com score 13
- **Dorks repetitivas**: Dorks 2-25 retornavam 0 URLs novas porque usavam a mesma engine

### Novidades
- **AMBIGUOUS_GATEWAYS**: Cielo, Stripe, Vindi, Iugu e Getnet agora exigem evidencia TECNICA forte (JS_SRC, IFRAME, FORM action para dominio da gateway). Texto mencionando o nome NAO confirma
- **Engine Rotation**: Cada dork e enviada para uma engine diferente (Brave -> DDG -> Bing -> Brave) para evitar rate limit e maximizar resultados
- **Backup Engine**: Se uma engine retorna menos de 3 resultados, automaticamente tenta outra
- **Blacklist expandida**: 158 dominios bloqueados (era 96 na v6.0)
- **Penalidade para plugins**: Titulos com "plugin", "modulo", "extensao" recebem -30 no score
- **Store Score Threshold**: Aumentado de 8 para 12 para maior precisao
- **Debug Log**: Salva corretamente em `/sdcard/nh_files/logs_gate_hunter.txt`

---

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
- **Filtro anti-falso-positivo**: blacklist expandida para 96+ dominios incluindo plataformas e-commerce
- **Store Score refinado**: 16 sinais positivos e 11 sinais negativos
- **Gateway detection em 5 zonas**: script src, iframe, form action, links, texto contextual
- **Dedup por dominio**: apenas 1 URL por dominio para evitar duplicatas

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
