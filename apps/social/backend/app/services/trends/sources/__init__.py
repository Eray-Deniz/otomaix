"""Layer A ücretsiz trend kaynakları.

Her modül bir `fetch(sector: dict) -> list[dict]` coroutine'i dışa açar.
Dönen item şeması:
    {
        "title": str,           # trend/başlık
        "source": str,          # kaynak adı ("Google News" vb.)
        "url": str | None,      # opsiyonel deeplink
        "score": float | None,  # opsiyonel popülerlik skoru
        "summary": str | None,  # opsiyonel kısa özet
    }

Her kaynak exception fırlatmaz — hata durumunda boş liste döndürür.
`sector` dict'i `slug`, `display_name`, `keywords` alanlarını içerir.
"""
