-- Sprint 7 — Faceless → Kısa Video adlandırma geçişi
-- Geçmiş video post'larının template_id'si yeni şablon ID'sine taşınır.
-- Eski şablon (facelessvideo-genel-sablon) backend'de status="deprecated" olarak
-- 1-2 hafta paralel kayıtlı kalır; PR 3 cleanup'ta hem DB'de hem kodda silinir.

UPDATE social.posts
SET template_id = 'shortvideo-genel-sablon'
WHERE template_id = 'facelessvideo-genel-sablon';
