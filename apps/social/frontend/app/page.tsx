import Link from 'next/link'
import { Check } from 'lucide-react'

const FEATURES = [
  {
    icon: '🎨',
    title: 'AI Görsel Üretimi',
    desc: 'Markanıza özel görseller saniyeler içinde. Marka renkleriniz ve logonuzla otomatik uyumlu.',
  },
  {
    icon: '🎬',
    title: 'Faceless Video',
    desc: 'Yüz göstermeden profesyonel video içerikleri. Türkçe seslendirme desteğiyle hazır.',
  },
  {
    icon: '🤖',
    title: 'AI Avatar',
    desc: 'Kendi dijital avatarınızla kişisel içerikler üretin. HeyGen entegrasyonu ile gerçekçi sonuçlar.',
  },
  {
    icon: '📅',
    title: 'Otomatik Yayın',
    desc: 'İçeriklerinizi planlayın, Telegram onay akışıyla kontrol edin. Siz uyurken yayınlansın.',
  },
  {
    icon: '📊',
    title: 'Rakip Analizi',
    desc: "Rakiplerinizin içerik stratejisini analiz edin. AI ile fırsatları ve açıkları görün.",
  },
  {
    icon: '📈',
    title: 'Trend Takibi',
    desc: 'Sektörünüzdeki güncel trendleri yakalayın. Tek tıkla trend içeriklere dönüştürün.',
  },
]

const STATS = [
  { value: '10K+', label: 'Üretilen İçerik' },
  { value: '500+', label: 'Aktif Marka' },
  { value: '4.9★', label: 'Kullanıcı Puanı' },
  { value: '6 saat', label: 'Haftalık Tasarruf' },
]

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: '499',
    features: ['1 marka', '50 içerik/ay', '1 GB depolama', 'AI görsel üretimi', 'İçerik takvimi'],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '999',
    popular: true,
    features: ['3 marka', '200 içerik/ay', '5 GB depolama', 'AI görsel + video', 'Rakip analizi', 'Otomatik yayın'],
  },
  {
    id: 'business',
    name: 'Business',
    price: '2.499',
    features: ['10 marka', 'Sınırsız içerik', '20 GB depolama', 'AI Avatar', 'Trend analizi', 'Öncelikli destek'],
  },
  {
    id: 'agency',
    name: 'Agency',
    price: '4.999',
    features: ['Sınırsız marka', 'Sınırsız içerik', '50 GB depolama', 'Tüm özellikler', 'Özel entegrasyon', 'Dedike destek'],
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">O</span>
            </div>
            <span className="font-bold text-gray-900">Otomaix Social</span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
            <a href="#ozellikler" className="hover:text-gray-900 transition-colors">Özellikler</a>
            <a href="#fiyatlar" className="hover:text-gray-900 transition-colors">Fiyatlar</a>
            <a href="mailto:destek@otomaix.com" className="hover:text-gray-900 transition-colors">Destek</a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
            >
              Giriş Yap
            </Link>
            <Link
              href="/kayit"
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              Ücretsiz Dene
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          <span>🎁</span>
          <span>14 gün ücretsiz deneme — kredi kartı gerekmez</span>
        </div>
        <h1 className="text-5xl font-extrabold text-gray-900 leading-tight mb-5">
          Türk KOBİ&apos;ler için
          <br />
          <span className="text-blue-600">AI Sosyal Medya Otomasyonu</span>
        </h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          Markanıza özel içerikler üretin, otomatik yayınlayın, rakiplerinizi analiz edin.
          Türkçe destekli, kullanımı kolay, hepsi tek platformda.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/kayit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3.5 rounded-xl text-lg transition-colors shadow-lg shadow-blue-200"
          >
            14 Gün Ücretsiz Başla →
          </Link>
          <Link
            href="/login"
            className="text-gray-600 hover:text-gray-900 font-medium px-6 py-3.5 rounded-xl border border-gray-200 hover:border-gray-300 transition-colors"
          >
            Giriş Yap
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-gray-50 border-y border-gray-100 py-10">
        <div className="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl font-extrabold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="ozellikler" className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Tek Platformda Her Şey</h2>
          <p className="text-gray-500 text-lg">İçerik üretiminden yayına kadar tüm süreç otomatik</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-md transition-shadow"
            >
              <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-2xl mb-4">
                {f.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="fiyatlar" className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Şeffaf Fiyatlandırma</h2>
            <p className="text-gray-500 text-lg">İstediğiniz zaman iptal edin. Taahhüt yok.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {PLANS.map((plan) => (
              <div
                key={plan.id}
                className={`relative bg-white rounded-2xl p-6 flex flex-col ${
                  plan.popular
                    ? 'border-2 border-blue-500 shadow-lg shadow-blue-50'
                    : 'border border-gray-200'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                      En Popüler
                    </span>
                  </div>
                )}
                <div className="mb-4">
                  <h3 className="text-lg font-bold text-gray-900">{plan.name}</h3>
                  <div className="mt-2">
                    <span className="text-3xl font-extrabold text-gray-900">₺{plan.price}</span>
                    <span className="text-sm text-gray-400 ml-1">/ay</span>
                  </div>
                </div>
                <ul className="space-y-2.5 flex-1 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-gray-600">
                      <Check className="w-4 h-4 text-green-500 shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/kayit"
                  className={`w-full text-center py-2.5 rounded-xl text-sm font-semibold transition-colors ${
                    plan.popular
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'border border-gray-200 hover:border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Ücretsiz Dene
                </Link>
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-gray-400 mt-6">
            Tüm planlar 14 gün ücretsiz deneme ile başlar. KDV hariçtir.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Bugün Ücretsiz Başlayın
        </h2>
        <p className="text-gray-500 mb-8 text-lg">
          500&apos;den fazla Türk markasının tercih ettiği platforma katılın.
          Kredi kartı gerekmez.
        </p>
        <Link
          href="/kayit"
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-10 py-4 rounded-xl text-lg transition-colors shadow-lg shadow-blue-200"
        >
          14 Gün Ücretsiz Başla →
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-xs">O</span>
            </div>
            <span className="text-sm font-medium text-gray-600">Otomaix Social</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-400">
            <a href="mailto:destek@otomaix.com" className="hover:text-gray-600 transition-colors">
              destek@otomaix.com
            </a>
            <Link href="/login" className="hover:text-gray-600 transition-colors">Giriş Yap</Link>
            <Link href="/kayit" className="hover:text-gray-600 transition-colors">Kayıt Ol</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
