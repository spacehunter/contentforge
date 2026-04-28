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

interface Store {
  contents: ContentPiece[];
  setContents: (items: ContentPiece[]) => void;
  addContent: (item: any) => void;
}

const useStore = create<Store>((set) => ({
  contents: [],
  setContents: (items) => set({ contents: items }),
  addContent: (item) => set((state) => ({ contents: [item, ...state.contents] })),
}));

export default useStore;
