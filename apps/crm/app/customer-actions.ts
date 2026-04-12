'use server'

import { query } from '@/lib/db'
import { revalidatePath } from 'next/cache'

export async function addNote(accountId: string, note: string, createdBy: string) {
  if (!note.trim()) return { error: 'Not boş olamaz' }
  await query(
    `INSERT INTO crm.account_notes (account_id, note, created_by) VALUES ($1, $2, $3)`,
    [accountId, note.trim(), createdBy]
  )
  revalidatePath(`/musteriler/${accountId}`)
  return { success: true }
}

export async function addCommunication(
  accountId: string,
  data: {
    channel: string
    direction: string
    subject?: string
    note?: string
    createdBy: string
  }
) {
  await query(
    `INSERT INTO crm.account_communications (account_id, channel, direction, subject, note, created_by)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [accountId, data.channel, data.direction, data.subject ?? null, data.note ?? null, data.createdBy]
  )
  revalidatePath(`/musteriler/${accountId}`)
  return { success: true }
}

export async function addTag(accountId: string, tag: string, addedBy: string) {
  await query(
    `INSERT INTO crm.account_tags (account_id, tag, added_by) VALUES ($1, $2, $3)
     ON CONFLICT (account_id, tag) DO NOTHING`,
    [accountId, tag, addedBy]
  )
  revalidatePath(`/musteriler/${accountId}`)
  revalidatePath('/musteriler')
  return { success: true }
}

export async function removeTag(accountId: string, tag: string) {
  await query(
    `DELETE FROM crm.account_tags WHERE account_id = $1 AND tag = $2`,
    [accountId, tag]
  )
  revalidatePath(`/musteriler/${accountId}`)
  revalidatePath('/musteriler')
  return { success: true }
}

export async function changePlan(accountId: string, newPlanId: string) {
  await query(
    `UPDATE social.accounts SET plan_id = $2 WHERE id = $1`,
    [accountId, newPlanId]
  )
  await query(
    `UPDATE social.subscriptions SET plan_id = $2 WHERE account_id = $1`,
    [accountId, newPlanId]
  )
  revalidatePath(`/musteriler/${accountId}`)
  revalidatePath('/musteriler')
  return { success: true }
}
