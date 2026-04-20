-- Phase 8 — Template-spesifik görsel üzeri metin overlay (per-post override).
--
-- NULL  = post'un template'ında imageTextOverlay tanımlıysa template.imageTextOverlay.fields
--         kullanılır; tanımlı değilse overlay uygulanmaz.
-- []    = kullanıcı tüm alanları kapattı (overlay basılmaz).
-- [...] = bu alan id'leri (template.formFields'te tanımlı) görselin üstünde
--         template.imageTextOverlay.position'a göre render edilir.
ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS image_text_fields TEXT[] DEFAULT NULL;
