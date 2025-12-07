const API_URL: string = import.meta.env.VITE_API_BASE_URL;

let isRefreshing: boolean = false;
let refreshPromise: Promise<string> | null = null;

interface ApiHeaders {
    [key: string]: string;
}

interface ApiOptions extends RequestInit {
    headers?: ApiHeaders;
}

async function refreshAccessToken(): Promise<string> {
    if (!isRefreshing) {
        isRefreshing = true;

        refreshPromise = fetch(`${API_URL}/refresh`, {
            method: "POST",
            credentials: "include"
        })
            .then(async res => {
                if (!res.ok) throw new Error("Refresh failed");
                const data = await res.json();
                localStorage.setItem("access_token", data.access_token);
                return data.access_token as string;
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
        const newToken = await refreshAccessToken();

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
        const newToken = await refreshAccessToken();

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


