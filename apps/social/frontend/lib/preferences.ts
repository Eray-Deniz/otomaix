/**
 * Kullanıcı tercihi persist (localStorage). SSR-safe.
 *
 * Anahtar şeması: `otomaix_pref_<scope>` veya `otomaix_pref_<scope>_<id>`.
 * Marka seçimi gibi mevcut anahtarlarla çakışmaması için `otomaix_pref_` prefix'i.
 */

const PREFIX = 'otomaix_pref_'

export function getPref<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback
  try {
    const raw = window.localStorage.getItem(PREFIX + key)
    if (raw == null) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export function setPref<T>(key: string, value: T): void {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(PREFIX + key, JSON.stringify(value))
  } catch {
    // Quota / private browsing — sessizce yutulur
  }
}
