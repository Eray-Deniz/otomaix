export const dynamic = 'force-dynamic'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-[#F6F7F9] flex items-center justify-center">
      {children}
    </div>
  )
}
