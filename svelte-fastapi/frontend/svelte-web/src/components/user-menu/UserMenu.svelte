<script lang="ts">
    import { onMount } from "svelte";

    export let username: string = "User";
    export let signOut: () => void = () => {};

    let open = false;
    let menuRef: HTMLElement;
    const toggle = () => (open = !open);

    const handleClickOutside = (e: MouseEvent) => {
        if (menuRef && !menuRef.contains(e.target as Node)) {
            open = false;
        }
    };

    onMount(() => {
        document.addEventListener("click", handleClickOutside);
        return () => document.removeEventListener("click", handleClickOutside);
    });
</script>


<div class="menu-wrapper" bind:this={menuRef}>
    <button class="menu-btn" onclick={toggle}>
        Welcome {username}
        <span class="arrow"></span>
    </button>

    {#if open}
        <div class="dropdown">
            <div class="triangle"></div>
            <button onclick={signOut}>Sign out</button>
        </div>
    {/if}
</div>

<style>
    .menu-wrapper {
        position: relative;
        display: inline-block;
    }

    .menu-btn {
        background: #001529;
        color: white;
        border: none;
        padding: 8px 16px;
        cursor: pointer;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    :hover{
        background: #001529;
        color: #8ab4ff;
    }

    .arrow {
        border: solid #8ab4ff;
        border-width: 0 2px 2px 0;
        display: inline-block;
        padding: 3px;
        transform: rotate(45deg);
        margin-top: -2px;
    }

    .dropdown {
        position: absolute;
        top: 46px;
        right: 0;
        background: white;
        border-radius: 12px;
        padding: 14px 20px;
        box-shadow: 0px 8px 18px rgba(0,0,0,0.15);
        min-width: 180px;
        animation: fadeIn 0.18s ease-out;
        z-index: 10;
    }

    .triangle {
        position: absolute;
        top: -6px;
        right: 18px;
        width: 0;
        height: 0;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-bottom: 6px solid white;
    }

    .dropdown button {
        width: 100%;
        text-align: left;
        padding: 8px 0;
        font-size: 15px;
        cursor: pointer;
        background: none;
        border: none;
        color: #333;
    }

    .dropdown button:hover {
        color: #1d4ed8;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-4px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>