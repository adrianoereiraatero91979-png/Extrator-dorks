# Changelog - GateHunter

## v5.0.0 (2026-03-23) - Multi-Engine Revolution

### Problemas Corrigidos
- **Falsos positivos eliminados**: v4.0 retornava 34/38 sites como "SaaS/Software" (docs, blogs, suporte da gateway). Agora o filtro bloqueia 100% desses sites.
- **Dorks reformuladas**: Dorks anteriores usavam múltiplos `intext:` que retornavam 0 resultados. Novas dorks são simples e abrangentes.
- **DDG Lite 202**: DDG Lite retornava status 202 com proxy. Agora usa DDG HTML sem proxy (IP direto do celular).
- **Google 0 URLs**: Google retornava 200 mas 0 URLs. Implementado parser com 4 padrões de extração + cookie de consent.
- **Debug logs**: Agora salva corretamente em `/sdcard/nh_files/logs_gate_hunter.txt`.

### Novidades
- **Multi-Engine v5**: DDG HTML + Google.com.br + Bing + Google CSE API (opcional)
- **Busca SEM proxy**: IP residencial do celular é mais confiável para buscas. Proxies usadas apenas para análise de sites.
- **Blacklist massiva**: 152+ domínios bloqueados (gateways, redes sociais, dev, docs, notícias, comparadores, etc.)
- **Store Score threshold reduzido**: De 8 para 6 para capturar mais lojas reais.
- **Dorks simples**: 1 termo entre aspas + contexto de loja, sem múltiplos `intext:`.
- **Dedup por domínio**: Apenas 1 URL por domínio para evitar repetição.
- **Google CSE API**: Suporte opcional para Google Custom Search Engine API (100 queries/dia grátis).

### Melhorias Técnicas
- Paginação em todos os engines (DDG página 2, Google start=10, Bing first=11,21)
- Parser Google com 4 padrões: `/url?q=`, `data-href`, links com `data-`/`ping=`, `<cite>` tags
- Gateway confirmation em 7 zonas: JS_SRC, IFRAME, FORM, LINK, INLINE_JS, META, TEXT
- Store Validator com 16 sinais positivos e 11 sinais negativos

---

## v4.0.0 (2026-03-23) - 3-Layer Validation

### Novidades
- Dorks por assinatura JS em vez de nome da gateway
- Blacklist massiva de domínios
- Validação em 3 camadas (URL Filter + Gateway Confirmation + Store Validator)
- Debug logs em `/sdcard/nh_files/logs_gate_hunter.txt`
- Deduplicação por domínio

---

## v2.0.0 (2026-03-23) - Initial Release

### Funcionalidades
- Menu interativo com 15 gateways de pagamento
- Multi-engine: DuckDuckGo + Google + Bing
- curl_cffi com TLS fingerprint impersonate
- Proxy rotator com multi-gateway
- Relatórios em TXT, JSON e URLs
- Classificação de sites por categoria
