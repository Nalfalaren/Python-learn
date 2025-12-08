import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { jwtDecode } from "jwt-decode";

interface AdminAuth {
  token: string | null;
  role: string | null;
  id: string | null;
  isAuthenticated: boolean;
}

const initial: AdminAuth = {
  token: null,
  role: null,
  id: null,
  isAuthenticated: false
};

if (browser) {
  const token = localStorage.getItem("admin_access_token");
  if (token) {
    const decoded = jwtDecode<{ id: string; role: string }>(token);
    initial.token = token;
    initial.role = decoded.role;
    initial.id = decoded.id;
    initial.isAuthenticated = true;
  }
}

const { subscribe, set } = writable(initial);

export const adminAuthStore = {
  subscribe,
  login(token: string) {
    if (browser) {
      localStorage.setItem("admin_access_token", token);
      const decoded = jwtDecode<{ id: string; role: string }>(token);
      set({
        token,
        role: decoded.role,
        id: decoded.id,
        isAuthenticated: true
      });
    }
  },
  logout() {
    if (browser) {
      localStorage.removeItem("admin_access_token");
      window.location.href = "/employees/login"
    }
    set({ token: null, role: null, id: null, isAuthenticated: false });
  }
};
