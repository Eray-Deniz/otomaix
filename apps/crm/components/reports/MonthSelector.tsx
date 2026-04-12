'use client'

import { useRouter, usePathname } from 'next/navigation'

interface MonthOption {
  value: string
  label: string
}

interface Props {
  options: MonthOption[]
  selected: string
}

export function MonthSelector({ options, selected }: Props) {
  const router = useRouter()
  const pathname = usePathname()

  return (
    <select
      value={selected}
      onChange={(e) => router.push(`${pathname}?month=${e.target.value}`)}
      className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none bg-white"
    >
      {options.map((m) => (
        <option key={m.value} value={m.value}>
          {m.label}
        </option>
      ))}
    </select>
  )
}
