---
description: otomaix-brain vault sağlık denetçisini çalıştır (read-only)
---

`tooling/brain-doctor/brain_doctor.py`'yi çalıştır: `python3 tooling/brain-doctor/brain_doctor.py --json --no-report`.
Çıktıyı oku, error/warning/info'yu özetle, en kritik bulguları (broken link, ambiguous, frontmatter_absent) öne çıkar.
Otomatik düzeltme YAPMA (v1 read-only). Vault'a yazma.
