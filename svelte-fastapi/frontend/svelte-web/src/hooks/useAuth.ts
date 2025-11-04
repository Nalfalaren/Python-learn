import { goto } from '$app/navigation'
import { create } from 'zustand'

interface useAuthParams {
    token: string
    removeToken: () => void
    setToken: (value: string) => void
}

export const useAuth = create<useAuthParams>((set) => ({
    token: localStorage.getItem('accessToken') || '',

    setToken: (token: string) => 
        set((state) => {
            localStorage.setItem('accessToken', token);
            return {...state, token: token};
        }),
    removeToken: () =>
        set((state) => {
            localStorage.removeItem('accessToken');
            goto('/login')
            return {...state, token: ''}
        })
}));