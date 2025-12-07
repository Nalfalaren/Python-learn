// authCustomer.ts
import { writable } from "svelte/store";
import { browser } from "$app/environment";
import { jwtDecode } from "jwt-decode";

interface CustomerAuth {
  token: string | null;
  id: string | null;
  isAuthenticated: boolean;
}

const initial: CustomerAuth = {
  token: null,
  id: null,
  isAuthenticated: false
};

if (browser) {
  const token = localStorage.getItem("accessToken");
  if (token) {
    const decoded = jwtDecode<{ id: string }>(token);
    initial.token = token;
    initial.id = decoded.id;
    initial.isAuthenticated = true;
  }
}

const { subscribe, set } = writable(initial);

export const authCustomer = {
  subscribe,

  login(token: string) {
    const decoded = jwtDecode<{ id: string }>(token);
    localStorage.setItem("accessToken", token);
    set({ token, id: decoded.id, isAuthenticated: true });
  },

  logout() {
    localStorage.removeItem("accessToken");
    set({ token: null, id: null, isAuthenticated: false });
  }
};
