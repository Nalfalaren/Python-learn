import { jwtDecode } from "jwt-decode";

const API_URL: string = import.meta.env.VITE_API_BASE_URL;

let isRefreshing: boolean = false;
let refreshPromise: Promise<string> | null = null;

interface ApiHeaders {
    [key: string]: string;
}

interface ApiOptions extends RequestInit {
    headers?: ApiHeaders;
}

type UserType = "CUSTOMER" | "ADMIN" | 'EMPLOYEE';

async function refreshAccessToken(userType: UserType): Promise<string> {
    const accessKey = userType === "ADMIN" || userType === "EMPLOYEE" ? "admin_access_token" : "accessToken";
    const refreshKey = userType === "ADMIN" || userType === "EMPLOYEE" ? "admin_refresh_token" : "customer_refresh_token";

    if (!isRefreshing) {
        isRefreshing = true;

        const refreshToken = localStorage.getItem(refreshKey);
        if (!refreshToken) throw new Error("No refresh token found");

        refreshPromise = fetch(`${API_URL}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
            credentials: "include"
        })
        .then(async res => {
            if (!res.ok) throw new Error("Refresh failed");
            const data = await res.json();

            localStorage.setItem(accessKey, data.access_token);
            if (data.refresh_token) {
                localStorage.setItem(refreshKey, data.refresh_token);
            }

            return data.access_token;
        })
        .finally(() => {
            isRefreshing = false;
        });
    }

    return refreshPromise!;
}

export async function clientApi(url: string, options: RequestInit = {}) {
    const token = localStorage.getItem("accessToken");
    // Merge headers đúng chuẩn
    const mergedHeaders = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(options.headers || {})
    };

    const mergedOptions: RequestInit = {
        ...options,
        headers: mergedHeaders,
        credentials: "include",
    };

    let res = await fetch(url, mergedOptions);
    if (res.status === 401) {
        const newToken = await refreshAccessToken('CUSTOMER');
        const retryHeaders = {
            "Content-Type": "application/json",
            Authorization: `Bearer ${newToken}`,
            ...(options.headers || {})
        };

        const retryOptions: RequestInit = {
            ...options,
            headers: retryHeaders,
            credentials: "include",
        };

        res = await fetch(url, retryOptions);
    }

    return res;
}


export async function adminApi(url: string | URL, options: RequestInit = {}) {
    const token = localStorage.getItem("admin_access_token");
    const decoded = token ? jwtDecode<{ role: 'ADMIN' | 'EMPLOYEE' }>(token) : null;

    const mergedHeaders = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(options.headers || {})
    };

    const mergedOptions: RequestInit = {
        ...options,
        headers: mergedHeaders,
        credentials: "include",
    };

    let res = await fetch(url, mergedOptions);

    if (res.status === 401) {
        const newToken = await refreshAccessToken(decoded.role);

        const retryHeaders = {
            "Content-Type": "application/json",
            Authorization: `Bearer ${newToken}`,
            ...(options.headers || {})
        };

        const retryOptions: RequestInit = {
            ...options,
            headers: retryHeaders,
            credentials: "include",
        };

        res = await fetch(url, retryOptions);
    }

    return res;
}
