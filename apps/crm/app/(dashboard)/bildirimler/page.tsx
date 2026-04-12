export default function BildirimlerPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-bold text-gray-900 mb-6">Bildirimler</h1>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 text-center">
        <div className="text-4xl mb-3">🔔</div>
        <h2 className="text-sm font-semibold text-gray-700 mb-2">
          n8n CRM Otomasyonları
        </h2>
        <p className="text-xs text-gray-500 max-w-sm mx-auto">
          Telegram bildirimleri n8n üzerinden gönderilir.
          Yeni müşteri, plan yükseltme, ödeme hatası ve churn riski bildirimleri
          n8n workflow&apos;larında yapılandırılır.
        </p>
        <a
          href="https://n8n.otomaix.com"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-4 text-xs text-blue-600 hover:underline"
        >
          n8n Workflow&apos;larına Git →
        </a>
      </div>
    </div>
  )
}
