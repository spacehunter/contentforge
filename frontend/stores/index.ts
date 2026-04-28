import { create } from 'zustand';

export interface ContentPiece {
  id: number;
  title: string;
  content_type: string;
  prompt: string;
  generated_text?: string;
  status: string;
  brand_id?: number;
  user_id: number;
  created_at: string;
}

export interface Brand {
  id: number;
  name: string;
  voice: string;
  industry: string;
  target_audience: string;
  user_id: number;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
}

interface Store {
  user: User | null;
  token: string | null;
  contents: ContentPiece[];
  brands: Brand[];
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setContents: (items: ContentPiece[]) => void;
  addContent: (item: ContentPiece) => void;
  setBrands: (items: Brand[]) => void;
  addBrand: (item: Brand) => void;
}

const useStore = create<Store>((set) => ({
  user: null,
  token: null,
  contents: [],
  brands: [],
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setContents: (items) => set({ contents: items }),
  addContent: (item) => set((state) => ({ contents: [item, ...state.contents] })),
  setBrands: (items) => set({ brands: items }),
  addBrand: (item) => set((state) => ({ brands: [item, ...state.brands] })),
}));

export default useStore;
