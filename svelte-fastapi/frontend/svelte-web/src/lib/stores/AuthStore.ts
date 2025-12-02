import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { jwtDecode } from 'jwt-decode';
import { goto } from '$app/navigation';

function createAuthStore() {
  interface AuthProps{
    token: string | null
    role: string | null
    isAuthenticated: boolean
    id: string | null
  }
  const initialValue: AuthProps = {
    token: null,
    role: null,
    isAuthenticated: false,
    id: null
  };

  if (browser) {
    const savedToken = localStorage.getItem("accessToken");
    const decoded = savedToken ? jwtDecode<{ id: string; role: string }>(savedToken) : null;
    if (savedToken && decoded?.role && decoded?.id) {
      initialValue.token = savedToken;
      initialValue.role = decoded.role;
      initialValue.isAuthenticated = true;
      initialValue.id = decoded.id;
    }
  }

  const { subscribe, set, update } = writable(initialValue);

  return {
    subscribe,

    login: (token: string) => {
      if (browser) {
        localStorage.setItem('accessToken', token);
      }
      const decoded = token ? jwtDecode<{ id: string; role: string }>(token) : null;
      set({
        token,
        role: decoded?.role || null,
        isAuthenticated: true,
        id: decoded?.id || null
      });
    },

    logout: async () => {
      if (browser) {
        const token = localStorage.getItem("accessToken");
        const decoded = token ? jwtDecode<{ id: string }>(token) : null;

        try {
          if (token && decoded?.id) {
            await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/logout`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
              },
              body: JSON.stringify({ id: decoded.id })
            });
          }
        } catch (err) {
          console.error("Logout API failed:", err);
        }

        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
      }

      set({
        token: null,
        role: null,
        isAuthenticated: false,
        id: null
      });

      goto("/employees/login");
    },

    isAuthenticated: (): boolean => {
      if (browser) {
        return !!localStorage.getItem('accessToken');
      }
      return false;
    },

    checkAuth: () => {
      if (browser) {
        const token = localStorage.getItem('accessToken');
        if (token) {
          const decoded = jwtDecode<{ id: string; role: string }>(token);
          set({
            token,
            role: decoded?.role || null,
            isAuthenticated: true,
            id: decoded?.id || null
          });
        } else {
          set({
            token: null,
            role: null,
            isAuthenticated: false,
            id: null
          });
        }
      }
    }
  };
}

export const authStore = createAuthStore();
