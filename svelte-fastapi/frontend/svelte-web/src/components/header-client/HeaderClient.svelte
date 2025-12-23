<script lang="ts">
    import HeaderLogo from "$lib/assets/header_logo.svelte";
    import styles from "$lib/styles/landing/landing.module.css";
    import searchIcon from "$lib/assets/search_icon.svg";
    import { goto } from "$app/navigation";
    import user from "$lib/assets/user.svg";
    import shoppingCart from "$lib/assets/shopping_cart.svg";

    let {
        mounted,
        query = $bindable(),
        handleSearch,
        isLoggedIn,
        logout,
        openCartList,
        cartCount,
        userName,
    } = $props();
</script>

<header class={styles.header} class:anim-in={mounted}>
    <div class={styles.container}>
        <div class={styles.headerMain}>
            <a href="/" class={styles.brand}>
                <div class={styles.logo}>
                    <HeaderLogo />
                </div>
                <div>
                    <div
                        style="font-weight:700; font-size: 20px, color: #000000"
                    >
                        DRONESELL
                    </div>
                </div>
            </a>

            <div class={styles.searchBar}>
                <img
                    src={searchIcon}
                    alt="search_icon"
                    class={styles.searchIcon}
                />
                <input
                    placeholder="Search for drones, parts, accessories..."
                    bind:value={query}
                    onkeydown={(e) => e.key === "Enter" && handleSearch()}
                />
            </div>

            <div class={styles.headerActions}>
                <div class={styles.headerBtn}>
                    {#if isLoggedIn}
                        <div class={styles.headerLogin}>
                            <div>Welcome <b>{userName}</b></div>
                            <div class={styles.headerUser}>
                                <img src={user} alt="user" />
                                <button
                                    class={styles.logoutBtn}
                                    onclick={logout}
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    {:else}
                        <button
                            class={styles.loginBtn}
                            onclick={() => goto("/login")}
                        >
                            Sign In
                        </button>
                    {/if}
                </div>
                <button class={styles.iconBtn} onclick={openCartList}>
                    <img src={shoppingCart} alt="cart_img" />
                    <span class={styles.label}>Cart</span>
                    {#if $cartCount > 0 && isLoggedIn}
                        <span class={styles.cartBadge}>{$cartCount}</span>
                    {/if}
                </button>
            </div>
        </div>

        <nav class={styles.mainNav}>
            <a href="#" class={styles.navItem}>
                <span class={styles.navIcon}>☰</span>
                All Categories
            </a>
        </nav>
    </div>
</header>
