// src/lib/stores/cart.ts
import { writable } from "svelte/store";

export type Product = {
  id?: string;
  product_name: string;
  category: string;
  price: number;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  img?: string;
  rating?: number;
  stock?: number;
};

export type CartItem = Product & {
  quantity: number;
};

const STORAGE_KEY = "cart";

function readFromStorage(): CartItem[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeToStorage(cart: CartItem[]) {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
  } catch {}
}

function createCartStore() {
  const initial = readFromStorage();
  const { subscribe, set, update } = writable<CartItem[]>(initial);

  // keep localStorage in sync
  subscribe((val) => writeToStorage(val));

  return {
    subscribe,
    set,
    clear: () => {
      set([]);
      if (typeof localStorage !== "undefined") {
        localStorage.removeItem(STORAGE_KEY);
      }
    },
    addItem: (product: Product, qty = 1) =>
      update((cart) => {
        if (!product.id) return cart;
        
        const idx = cart.findIndex((c) => c.id === product.id);
        if (idx !== -1) {
          // Update existing item
          const maxQty = product.stock ?? Number.MAX_SAFE_INTEGER;
          cart[idx].quantity = Math.min(cart[idx].quantity + qty, maxQty);
        } else {
          // Add new item
          const newItem: CartItem = {
            ...product,
            quantity: Math.min(qty, product.stock ?? Number.MAX_SAFE_INTEGER),
          };
          cart.push(newItem);
        }
        return [...cart];
      }),
    removeItem: (id: string) =>
      update((cart) => cart.filter((c) => c.id !== id)),
    updateQuantity: (id: string, quantity: number) =>
      update((cart) =>
        cart.map((c) => {
          if (c.id === id) {
            const maxQty = c.stock ?? Number.MAX_SAFE_INTEGER;
            return { ...c, quantity: Math.max(1, Math.min(quantity, maxQty)) };
          }
          return c;
        })
      ),
    getTotalCount: (): number => {
      const cart = readFromStorage();
      return cart.reduce((sum, item) => sum + item.quantity, 0);
    },
    getTotalPrice: (): number => {
      const cart = readFromStorage();
      return cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    },
  };
}

export const cart = createCartStore();
export const CartStore = cart;

