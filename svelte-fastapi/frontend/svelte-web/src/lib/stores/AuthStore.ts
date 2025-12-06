import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { jwtDecode } from 'jwt-decode';
import { goto } from '$app/navigation';

function createAuthStore() {
  interface AuthProps {
    token: string | null;
    role: string | null;
    isAuthenticated: boolean;
    id: string | null;
  }

  const initialValue: AuthProps = {
    token: null,
    role: null,
    isAuthenticated: false,
    id: null
  };

  // =============================
  // 🔥 KHỞI TẠO STORE
  // =============================
  if (browser) {
    const adminToken = localStorage.getItem("admin_access_token");
    const customerToken = localStorage.getItem("accessToken");

    let tokenToUse = adminToken || customerToken;

    const decoded = tokenToUse
      ? jwtDecode<{ id: string; role: string }>(tokenToUse)
      : null;

    if (tokenToUse && decoded?.role && decoded?.id) {
      initialValue.token = tokenToUse;
      initialValue.role = decoded.role;
      initialValue.isAuthenticated = true;
      initialValue.id = decoded.id;
    }
  }

  const { subscribe, set } = writable(initialValue);

  return {
    subscribe,

    // =============================
    // 🔥 LOGIN
    // =============================
    login: (token: string) => {
      if (browser) {
        const decoded = jwtDecode<{ id: string; role: string }>(token);

        if (decoded.role === "ADMIN" || decoded.role === "EMPLOYEE") {
          localStorage.setItem("admin_access_token", token);
        } else {
          localStorage.setItem("accessToken", token);
        }

        set({
          token,
          role: decoded.role,
          isAuthenticated: true,
          id: decoded.id
        });
      }
    },

    // =============================
    // 🔥 LOGOUT
    // =============================
    logout: async () => {
      if (browser) {
        const adminToken = localStorage.getItem("admin_access_token");
        const customerToken = localStorage.getItem("accessToken");
        const token = adminToken || customerToken;

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

        localStorage.removeItem("admin_access_token");
        localStorage.removeItem("accessToken");
      }

      set({
        token: null,
        role: null,
        isAuthenticated: false,
        id: null
      });

      goto("/employees/login");
    },

    // =============================
    // 🔥 CHECK AUTH STATUS
    // =============================
    isAuthenticated: (): boolean => {
      if (browser) {
        return (
          !!localStorage.getItem("admin_access_token") ||
          !!localStorage.getItem("accessToken")
        );
      }
      return false;
    },

    // =============================
    // 🔥 TỰ CHECK TOKEN
    // =============================
    checkAuth: () => {
      if (browser) {
        const adminToken = localStorage.getItem("admin_access_token");
        const customerToken = localStorage.getItem("accessToken");

        const token = adminToken || customerToken;

        if (token) {
          const decoded = jwtDecode<{ id: string; role: string }>(token);
          set({
            token,
            role: decoded.role,
            isAuthenticated: true,
            id: decoded.id
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
