# Otomaix Brain Doctor v1

`otomaix-brain` vault'unun yapısal sağlık denetçisi. Stdlib-only, vault'a karşı read-only.
Spec: `docs/specs/2026-05-21-otomaix-brain-doctor.md`.

## Kullanım

    python3 tooling/brain-doctor/brain_doctor.py            # rapor → tooling/brain-doctor/reports/
    python3 tooling/brain-doctor/brain_doctor.py --json --no-report   # stdout JSON, dosya yok
    python3 tooling/brain-doctor/brain_doctor.py --min-severity error # sadece error

Exit: 0 = error yok | 1 = ≥1 error | 2 = tool/config/IO hatası.
Vault'a yazma yalnız `--output-dir <vault>/_health --allow-vault-output` ile.

## Test

    cd tooling/brain-doctor && python3 -m unittest -v
