import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { formatDistanceToNow, format } from 'date-fns'
import { tr } from 'date-fns/locale'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function relativeTime(date: Date | string | null): string {
  if (!date) return 'Hiç giriş yapmadı'
  const d = typeof date === 'string' ? new Date(date) : date
  return formatDistanceToNow(d, { addSuffix: true, locale: tr })
}

export function formatDate(date: Date | string | null, fmt = 'dd.MM.yyyy'): string {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return format(d, fmt)
}

export function formatCurrency(amountTry: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0,
  }).format(amountTry)
}

export const PLAN_LABELS: Record<string, string> = {
  free: 'Ücretsiz',
  starter: 'Starter',
  pro: 'Pro',
  business: 'Business',
  agency: 'Agency',
}

export const PLAN_COLORS: Record<string, string> = {
  free: 'bg-gray-100 text-gray-700',
  starter: 'bg-slate-100 text-slate-700',
  pro: 'bg-blue-100 text-blue-700',
  business: 'bg-purple-100 text-purple-700',
  agency: 'bg-amber-100 text-amber-700',
}

export const PLAN_PRICES: Record<string, number> = {
  free: 0,
  starter: 499,
  pro: 999,
  business: 2499,
  agency: 4999,
}

export const STATUS_LABELS: Record<string, string> = {
  active: 'Aktif',
  trialing: 'Deneme',
  past_due: 'Ödeme Sorunu',
  cancelled: 'İptal',
  none: 'Abonelik Yok',
}

export const STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  trialing: 'bg-cyan-100 text-cyan-700',
  past_due: 'bg-red-100 text-red-700',
  cancelled: 'bg-gray-100 text-gray-500',
  none: 'bg-gray-100 text-gray-500',
}
