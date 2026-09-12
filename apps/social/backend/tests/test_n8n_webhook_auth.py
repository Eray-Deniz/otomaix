"""Backend → n8n webhook çağrılarının kabul kontrolü — 2026-09-12 güvenlik review'ı (S-1).

Dual güvenlik review'ı bir **critical** buldu: `crm-automations.json` içindeki üç
webhook (`crm/new-customer` · `crm/plan-upgrade` · `crm/payment-failed`) kimlik
doğrulaması istemiyordu ve ödeme akışı istek gövdesinden gelen `account_id`'yi
SQL metnine gömüyordu. Artefakt tarafı `headerAuth` + `queryReplacement` ile
kapatıldı; kapatma çağıran tarafı da bağlar: webhook artık başlık istiyorsa
çağıranın o başlığı GÖNDERMESİ, sırrı yoksa çağrıyı HİÇ yapmaması gerekir.

Desen uydurulmadı — yönetici-olay kanalı (`notifications._send_to_n8n`) zaten
aynı sözleşmeyi taşıyor: sır boşsa çağrı yola çıkmaz (fail-closed), sır varsa
kabul başlığı eklenir.
"""

import httpx
import pytest

from app.routers import billing, posts


def _posts_settings():
    """`posts` modülü ayarları fonksiyon içinde import eder — yama hedefi tek nesnedir."""
    from app.core.config import settings

    return settings


class _FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None


class _FakeClient:
    """httpx.AsyncClient yerine geçen, isteği yakalayan sahte istemci."""

    captured: dict = {}

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    durum_gonderim_aninda = None

    async def post(self, url, json=None, headers=None):
        _FakeClient.captured = {"url": url, "json": json, "headers": headers or {}}
        _FakeClient.durum_gonderim_aninda = (
            _SahteBaglanti.aktif.durum_yazildi if _SahteBaglanti.aktif else None
        )
        return _FakeResponse()


@pytest.mark.asyncio
async def test_crm_notify_fails_closed_without_secret(monkeypatch):
    """Sır yoksa CRM webhook'una çağrı YAPILMAZ.

    Sessizce kimliksiz göndermek, artefakta eklenen kabul kontrolünü boşa
    çıkarırdı: uç 401 döndürürken çağıran "gönderdim" sanırdı. Bildirim kritik
    olmadığı için akış durmaz; yapılmayan şey ÇAĞRININ KENDİSİDİR.
    """
    monkeypatch.setattr(billing.settings, "N8N_CRM_EVENT_SECRET", "")
    monkeypatch.setattr(billing.httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    await billing._notify_crm_n8n("crm/payment-failed", {"account_id": "a-1"})

    assert _FakeClient.captured == {}, "sırsızken kimliksiz çağrı YAPILDI"


@pytest.mark.asyncio
async def test_crm_notify_sends_auth_header(monkeypatch):
    """Sır varsa kabul başlığı isteğe EKLENİR ve uç doğru adrese gider."""
    monkeypatch.setattr(billing.settings, "N8N_CRM_EVENT_SECRET", "gizli-crm-anahtari")
    monkeypatch.setattr(billing.httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    await billing._notify_crm_n8n("crm/payment-failed", {"account_id": "a-1"})

    captured = _FakeClient.captured
    assert captured, "sır varken çağrı yapılmadı"
    assert captured["headers"][billing.CRM_EVENT_AUTH_HEADER] == "gizli-crm-anahtari"
    assert captured["url"].endswith("/webhook/crm/payment-failed")
    assert captured["json"] == {"account_id": "a-1"}


@pytest.mark.asyncio
async def test_crm_notify_uses_a_dedicated_secret(monkeypatch):
    """CRM kanalı yönetici-olay sırrını ÖDÜNÇ ALMAZ — ayrı kimlik, ayrı kanal.

    Tek sırrı iki kanalda paylaşmak, birinin sızması hâlinde ikisini birden
    açar; artefakt da ayrı bir credential (`Otomaix CRM Event Key`) atfediyor.
    """
    monkeypatch.setattr(billing.settings, "N8N_CRM_EVENT_SECRET", "")
    monkeypatch.setattr(billing.settings, "N8N_ADMIN_EVENT_SECRET", "yonetici-anahtari")
    monkeypatch.setattr(billing.httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    await billing._notify_crm_n8n("crm/new-customer", {"account_id": "a-2"})

    assert _FakeClient.captured == {}, "CRM kanalı yönetici sırrına düştü"


# ─── telegram-content-approval — aynı sınıf, aynı kapı ─────────────────────
#
# Sınıf kapısı (`test_no_webhook_node_is_unauthenticated`) CRM düzeltmesinden
# SONRA üç webhook daha kimliksiz buldu; biri bizim kendi backend'imizin
# çağırdığı `telegram-content-approval`. Varyantı yamayıp sınıfı kapatmanın
# karşılığı budur: aynı desen buraya da kurulur.


@pytest.mark.asyncio
async def test_telegram_approval_fails_closed_without_secret(monkeypatch):
    """Sır yoksa çağrı YAPILMAZ **ve** bu sessizce geçilmez — istisna ile bildirilir.

    İlk yazımda yardımcı sessizce dönüyordu; kapanış turu ölçtü ki çağıran o
    sessizliği "gitti" sayıp gönderiyi `reviewing`e çekiyordu. Atlama artık
    çağıranın GÖREBİLECEĞİ bir sonuçtur.
    """
    monkeypatch.setattr(_posts_settings(), "N8N_TELEGRAM_APPROVAL_SECRET", "")
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    with pytest.raises(RuntimeError):
        await posts._notify_telegram_approval({"post_id": "p-1"})

    assert _FakeClient.captured == {}, "sırsızken kimliksiz çağrı YAPILDI"


@pytest.mark.asyncio
async def test_telegram_approval_sends_auth_header(monkeypatch):
    """Sır varsa kabul başlığı eklenir ve yük olduğu gibi gider."""
    monkeypatch.setattr(_posts_settings(), "N8N_TELEGRAM_APPROVAL_SECRET", "gizli-onay")
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    await posts._notify_telegram_approval({"post_id": "p-1"})

    captured = _FakeClient.captured
    assert captured, "sır varken çağrı yapılmadı"
    assert captured["headers"][posts.TELEGRAM_APPROVAL_AUTH_HEADER] == "gizli-onay"
    assert captured["url"].endswith("/webhook/telegram-content-approval")
    assert captured["json"] == {"post_id": "p-1"}


# ─── Kapanış turu bulgusu (Codex, high): fail-closed SESSİZ KAYIP üretiyordu ──
#
# Düzeltmenin kendi yan etkisi ölçüldü: `_notify_telegram_approval` sır boşken
# sessizce dönüyordu, ama çağıran `request_approval` gönderiyi ZATEN `reviewing`
# yapmış ve kullanıcıya başarı dönmüştü. `reviewing`, onaya yeniden gönderilebilir
# durumlar kümesinde DEĞİL — yani gönderi ne bildirim almış ne de kurtarılabilir
# oluyordu. Kapanış: yapılandırma mutasyondan ÖNCE doğrulanır, durum ancak
# bildirim KABUL EDİLDİKTEN sonra değişir.


class _SahteBaglanti:
    """asyncpg bağlantısı yerine geçen, çağrıları sayan sahte."""

    aktif = None

    def __init__(self, post_status="ready"):
        self.calls: list[tuple] = []
        self._post_status = post_status
        _SahteBaglanti.aktif = self

    async def fetchrow(self, sql, *args):
        self.calls.append(("fetchrow", sql.split()[0], args))
        if "FROM social.posts" in sql:
            return {"id": args[0], "brand_id": "b-1", "status": self._post_status}
        if "FROM social.workspaces" in sql:
            return {"telegram_bot_token": "bot-sifre", "telegram_chat_id": "12345"}
        return None

    async def execute(self, sql, *args):
        self.calls.append(("execute", sql, args))
        return "UPDATE 1"

    @property
    def durum_yazildi(self) -> bool:
        return any(c[0] == "execute" for c in self.calls)


@pytest.mark.asyncio
async def test_request_approval_refuses_before_mutating_when_channel_unconfigured(monkeypatch):
    """Kanal yapılandırılmamışsa gönderi DURUMU DEĞİŞMEZ ve çağıran hata alır.

    Eski davranış: durum `reviewing` olur, kullanıcıya başarı dönerdi, bildirim
    hiç gitmezdi ve gönderi kurtarılamaz hâlde kalırdı (sessiz kayıp).
    """
    from fastapi import HTTPException

    monkeypatch.setattr(_posts_settings(), "N8N_TELEGRAM_APPROVAL_SECRET", "")
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}
    db = _SahteBaglanti()

    with pytest.raises(HTTPException) as hata:
        await posts.request_approval("p-1", user={"sub": "u-1"}, db=db)

    assert hata.value.status_code == 503
    assert not db.durum_yazildi, "bildirim gitmeyecekken gönderi durumu DEĞİŞTİ"
    assert _FakeClient.captured == {}


@pytest.mark.asyncio
async def test_request_approval_marks_reviewing_only_after_delivery(monkeypatch):
    """Durum ancak bildirim KABUL EDİLDİKTEN sonra `reviewing` olur."""
    monkeypatch.setattr(_posts_settings(), "N8N_TELEGRAM_APPROVAL_SECRET", "gizli-onay")
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}
    db = _SahteBaglanti()

    sonuc = await posts.request_approval("p-1", user={"sub": "u-1"}, db=db)

    assert _FakeClient.captured, "bildirim gönderilmedi"
    assert db.durum_yazildi, "bildirim gitti ama durum yazılmadı"
    yazim = [c for c in db.calls if c[0] == "execute"][0]
    assert "reviewing" in yazim[1]
    assert sonuc.data["status"] == "reviewing"
    # SIRA ÖLÇÜMÜ: sahte istemci, çağrıldığı ANDA durumun yazılıp yazılmadığını
    # kaydeder. Bu olmadan test yalnız "execute son db çağrısı" derdi — mutasyon
    # bildirimden ÖNCE de olsa yeşil kalırdı (ilk yazımda öyleydi, ölçüldü).
    assert _FakeClient.durum_gonderim_aninda is False, (
        "durum bildirimden ÖNCE yazılmış — bildirim düşerse gönderi mahsur kalır"
    )


@pytest.mark.asyncio
async def test_request_approval_does_not_strand_post_when_delivery_fails(monkeypatch):
    """Bildirim HATA verirse gönderi `reviewing`e ÇEKİLMEZ — yeniden denenebilir kalır."""
    from fastapi import HTTPException

    class _PatlayanIstemci(_FakeClient):
        async def post(self, url, json=None, headers=None):
            raise httpx.ConnectError("n8n ulaşılamıyor")

    monkeypatch.setattr(_posts_settings(), "N8N_TELEGRAM_APPROVAL_SECRET", "gizli-onay")
    monkeypatch.setattr(httpx, "AsyncClient", _PatlayanIstemci)
    db = _SahteBaglanti()

    with pytest.raises(HTTPException) as hata:
        await posts.request_approval("p-1", user={"sub": "u-1"}, db=db)

    assert hata.value.status_code == 502
    assert not db.durum_yazildi, "bildirim düştü ama gönderi `reviewing`e çekildi"
