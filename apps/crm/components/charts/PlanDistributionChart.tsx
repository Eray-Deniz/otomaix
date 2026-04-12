'use client'

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS: Record<string, string> = {
  Ücretsiz: '#94a3b8',
  Starter: '#64748b',
  Pro: '#3b82f6',
  Business: '#8b5cf6',
  Agency: '#f59e0b',
}

interface Props {
  data: { name: string; value: number; plan: string }[]
}

export function PlanDistributionChart({ data }: Props) {
  if (data.length === 0) {
    return (
      <div className="h-40 flex items-center justify-center text-gray-400 text-sm">
        Henüz veri yok
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={180}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={45}
          outerRadius={70}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((entry) => (
            <Cell
              key={entry.name}
              fill={COLORS[entry.name] ?? '#94a3b8'}
            />
          ))}
        </Pie>
        <Tooltip
          formatter={(value, name) => [`${value ?? 0} müşteri`, name as string]}
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value) => <span style={{ fontSize: 11 }}>{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
