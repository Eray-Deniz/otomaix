import { create } from 'zustand'

interface User {
  id: string
  email: string
  name: string
}

interface Workspace {
  id: string
  name: string
}

interface Brand {
  id: string
  name: string
  logo_light_url?: string
  logo_dark_url?: string
}

interface AppStore {
  user: User | null
  currentWorkspace: Workspace | null
  currentBrand: Brand | null
  setUser: (user: User | null) => void
  setCurrentWorkspace: (workspace: Workspace | null) => void
  setCurrentBrand: (brand: Brand | null) => void
}

export const useAppStore = create<AppStore>((set) => ({
  user: null,
  currentWorkspace: null,
  currentBrand: null,
  setUser: (user) => set({ user }),
  setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
  setCurrentBrand: (brand) => set({ currentBrand: brand }),
}))
