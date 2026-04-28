import { create } from 'zustand';

interface Brand {
  id: number;
  name: string;
  voice: string;
  industry: string;
  target_audience: string;
}

interface ContentPiece {
  id: number;
  title: string;
  content_type: string;
  prompt: string;
  generated_text: string | null;
  status: string;
}

interface Store {
  user: any;
  token: string | null;
  brands: Brand[];
  content: ContentPiece[];
  currentBrand: Brand | null;
  setUser: (user: any) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
  addBrand: (brand: Brand) => void;
  addContent: (piece: ContentPiece) => void;
}

const useStore = create<Store>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  brands: [],
  content: [],
  currentBrand: null,
  
  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) localStorage.setItem('token', token);
    else localStorage.removeItem('token');
    set({ token });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, brands: [], content: [] });
  },
  addBrand: (brand) => set((state) => ({ brands: [...state.brands, brand] })),
  addContent: (piece) => set((state) => ({ content: [piece, ...state.content] })),
}));

export default useStore;
