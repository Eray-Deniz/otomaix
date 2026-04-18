import { create } from 'zustand'

export interface User {
  id: string
  email: string
  name: string
  plan_id?: string
  trial_ends_at?: string | null
}

export interface Workspace {
  id: string
  name: string
}

export interface Brand {
  id: string
  name: string
  sector?: string | null
  sector_slug?: string | null
  sector_display_name?: string | null
  logo_light_url?: string | null
  logo_dark_url?: string | null
  is_active?: boolean
}

interface AppStore {
  user: User | null
  currentWorkspace: Workspace | null
  currentBrand: Brand | null
  brands: Brand[]
  setUser: (user: User | null) => void
  setCurrentWorkspace: (workspace: Workspace | null) => void
  setCurrentBrand: (brand: Brand | null) => void
  setBrands: (brands: Brand[]) => void
  switchBrand: (brand: Brand) => void
}

export const useAppStore = create<AppStore>((set) => ({
  user: null,
  currentWorkspace: null,
  currentBrand: null,
  brands: [],
  setUser: (user) => set({ user }),
  setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
  setCurrentBrand: (brand) => set({ currentBrand: brand }),
  setBrands: (brands) => set({ brands }),
  switchBrand: (brand) => set({ currentBrand: brand }),
}))
