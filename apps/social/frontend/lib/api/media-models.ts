// Phase 7 Sprint 7 Faz 2g — /media-models/active API client
// Backend: GET /media-models/active (public, 1hr cache)
// 4 modalite için aktif fal.ai model bilgisi — supported_ratios frontend
// aspect selector'ını dinamik populate eder.

import { api } from '@/lib/api'

export interface ModalityConfig {
  key: string
  model_id: string
  supported_ratios: string[] | null  // image_to_video için null — aspect yok
}

export interface ActiveMediaModels {
  image: ModalityConfig
  video: ModalityConfig
  image_to_video: ModalityConfig
  short_video_background: ModalityConfig
}

export async function fetchActiveMediaModels(): Promise<ActiveMediaModels | null> {
  const res = await api.get<ActiveMediaModels>('/media-models/active')
  return res.success ? res.data : null
}
