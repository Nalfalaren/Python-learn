<script lang="ts">
    import { goto, replaceState } from "$app/navigation";
    import { onMount } from "svelte";
    import { jwtDecode } from "jwt-decode";
    import { cart, type Product, type CartItem } from "$lib/stores/CartStore";
    import { derived } from "svelte/store";
    import { clientApi } from "../hooks/apiFetch";
    import styles from "$lib/styles/landing/landing.module.css";
    import droneImage from "$lib/assets/uav.png";
    import shoppingCart from "$lib/assets/shopping_cart.svg";
    import shoppingAddToCart from "$lib/assets/shopping_cart_white.svg";
    import user from "$lib/assets/user.svg";
    import searchIcon from "$lib/assets/search_icon.svg";
    import CreditCard from "$lib/assets/credit_card.svg";
    import HeadPhone from "$lib/assets/headphones.svg";
    import Trophy from "$lib/assets/trophy.svg";
    import Package from "$lib/assets/package.svg";
    import Eye from "$lib/assets/eye.svg";
    import Rating from "$lib/assets/rating.svelte";
    import ProductContainer from "../components/product-container/ProductContainer.svelte";
    import { listBrands } from "../utils/utils";
    import Footer from "../components/footer/Footer.svelte";
    import RequireSignInModal from "../components/require-sign-in-modal/RequireSignInModal.svelte";
    import MessageModal from "../components/modal-success/MessageModal.svelte";
    import HeaderClient from "../components/header-client/HeaderClient.svelte";
    /** Products list */
    let products: Product[] = $state([]);
    let userName = $state<string>("")
    let query = $state("");
    let category = $state("All");
    let sortBy = $state("featured");
    let quickView: Product | null = null;

    let isLoading = $state(false);
    let error = $state("");
    let mounted = $state(false);

    let currentPage = 1;
    let limit = 5;

    /** Add to cart modal */
    let addToCartProduct = $state<Product | null>(null);
    let showAddToCartModal = $state(false);
    let showAddToCardListModal = $state(false);
    let addToCartQuantity = $state(1);
    let isLoggedIn = $state(false);
    let message = $state("");
    let isConfirmModalClose = $state(false);

    // Subscribe to cart store
    let cartItems = $state<CartItem[]>([]);
    cart.subscribe((value) => {
        cartItems = value;
    });

    function updateURL() {
        const params = new URLSearchParams();
        if (query) params.set("query", query);
        if (category && category !== "All") params.set("category", category);
        if (sortBy) params.set("sortBy", sortBy);
        if (currentPage > 1) params.set("page", String(currentPage));
        const newUrl = `?${params.toString()}`;
        goto(newUrl, { noScroll: true });
    }

    /** Fetch products from API */
    const fetchProducts = async (
        cursor: string | null = null,
        direction: "next" | "prev" | "initial" = "initial",
    ): Promise<void> => {
        isLoading = true;
        error = "";

        try {
            const params = new URLSearchParams();
            if (query) params.set("search_product", query);
            if (category && category !== "All")
                params.set("category", category);
            if (sortBy) params.set("sort_by", sortBy);
            if (limit) params.set("limit", String(limit));
            if (cursor) params.set("next_cursor", cursor);

            const url = `${import.meta.env.VITE_API_BASE_URL}/products?${params.toString()}`;
            const res = await clientApi(url);
            const data = await res.json();

            products = (data.search_result || []).map(
                (p: Product, index: number) => ({
                    ...p,
                    img: `https://picsum.photos/seed/drone${index + 1}/600/400`,
                    rating: p.rating || 0,
                    stock: p.stock || 0,
                }),
            );

            if (direction === "next") {
                currentPage++;
            } else if (direction === "prev") {
                currentPage--;
            } else {
                currentPage = 1;
            }
            updateURL();
            mounted = true;
        } catch (e) {
            console.error(e);
            error = "Error found!";
        } finally {
            isLoading = false;
        }
    };

    function isTokenValid(token: string | null): boolean {
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            const exp = payload.exp * 1000;
            return Date.now() < exp;
        } catch {
            return false;
        }
    }
    onMount(() => {
        const token = localStorage.getItem("accessToken");
        userName = localStorage.getItem("customer_name") || ''
        isLoggedIn = isTokenValid(token);
        fetchProducts();
    });

    let dealProducts = $derived(products.slice(0, 5));

    const cartCount = derived(cart, ($cart) =>
        $cart.reduce((total, item) => total + item.quantity, 0),
    );

    function openQuickView(product: Product) {
        quickView = product;
    }

    function openAddToCartModal(product: Product) {
        addToCartProduct = product;
        addToCartQuantity = 1;
        showAddToCartModal = true;
    }

    function closeAddToCartModal() {
        addToCartProduct = null;
        addToCartQuantity = 1;
        showAddToCartModal = false;
    }

    function openCartList() {
        showAddToCardListModal = true;
    }

    function redirectToLogin() {
        goto("/login");
    }

    function closeCartList() {
        showAddToCardListModal = false;
    }

    function confirmAddToCart() {
        if (!addToCartProduct) return;
        cart.addItem(addToCartProduct, addToCartQuantity);
        closeAddToCartModal();
        (message = `Added ${addToCartQuantity} × ${addToCartProduct.product_name} to cart!`),
            (isConfirmModalClose = true);
    }

    const handleSearch = () => {
    if (query.trim()) {
        goto(`/products/list?search_product=${query}`, {replaceState: true});
    }
};

    async function logout() {
        try {
            const token = localStorage.getItem("accessToken");
            const decoded = token ? jwtDecode<{ id: string }>(token) : null;
            const currentUserId = decoded?.id;
            const res = await fetch(
                `${import.meta.env.VITE_API_BASE_URL}/auth/logout`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({ id: currentUserId }),
                },
            );

            if (!res.ok) {
                console.error("Logout API failed:", res.status);
            }
        } catch (err) {
            console.error("Logout request error:", err);
        } finally {
            localStorage.removeItem("accessToken");
            localStorage.removeItem("customer_refresh_token");
            cart.clear();
            isLoggedIn = false;
            goto("/login");
        }
    }
</script>

<!-- Header client -->
<HeaderClient
    {userName}
    bind:query={query}
    {mounted}
    {handleSearch}
    {isLoggedIn}
    {logout}
    {openCartList}
    {cartCount}
/>

<!-- HERO BANNER -->
<section class={styles.heroBanner} class:anim-in={mounted}>
    <a href="/products/list" class={styles.container}>
        <div class={styles.bannerContent}>
            <div class={styles.bannerText}>
                <span class={styles.bannerBadge}>Best Deal Online on drone</span>
                <h1 class={styles.bannerTitle}>LATEST DRONE MODELS</h1>
                <h2 class={styles.bannerSubtitle}>Up to 50% OFF</h2>
            </div>
            <div class={styles.bannerImage}>
                <img src={droneImage} alt="Latest Drones" />
            </div>
        </div>
    </a>
</section>

<!-- FEATURES BAR -->
<section class={styles.featuresBar}>
    <div class={styles.container}>
        <div class={styles.featuresGrid}>
            <div class={styles.featureItem}>
                <img class={styles.featureIcon} src={Package} alt="package" />
                <div>
                    <div class={styles.featureTitle}>Fasted Delivery</div>
                    <div class={styles.featureDesc}>Delivery in 24/H</div>
                </div>
            </div>
            <div class={styles.featureItem}>
                <img class={styles.featureIcon} src={Trophy} alt="trophy" />
                <div>
                    <div class={styles.featureTitle}>24 Hours Return</div>
                    <div class={styles.featureDesc}>
                        100% money-back guarantee
                    </div>
                </div>
            </div>
            <div class={styles.featureItem}>
                <img
                    class={styles.featureIcon}
                    src={CreditCard}
                    alt="credit_card"
                />
                <div>
                    <div class={styles.featureTitle}>Secure Payment</div>
                    <div class={styles.featureDesc}>Your money is safe</div>
                </div>
            </div>
            <div class={styles.featureItem}>
                <img
                    class={styles.featureIcon}
                    src={HeadPhone}
                    alt="headphone"
                />
                <div>
                    <div class={styles.featureTitle}>Support 24/7</div>
                    <div class={styles.featureDesc}>Live contact/message</div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- SHOP BY BRANDS -->
{#if dealProducts.length}
    <section class={styles.dealsSection}>
        <div class={styles.container}>
            <div class={styles.sectionHeader}>
                <h2 class={styles.sectionTitle}>SHOP BY BRANDS</h2>
            </div>
            <div class={styles.listBrands}>
                {#each listBrands as brand, i}
                <div style="width: 168px; height: 168px; background-color: #F4F4F4; border-radius: 10px">
                    <img src={brand} alt={brand} style="width: 100%; height: 100%">
                </div>
                {/each}
            </div>
        </div>
    </section>
{/if}

<!-- TODAY'S DEALS -->
{#if dealProducts.length}
    <section class={styles.dealsSection}>
        <div class={styles.container}>
            <div class={styles.sectionHeader}>
                <h2 class={styles.sectionTitle}>TODAY'S DEALS OF THE DAY</h2>
                <button
                    class={styles.viewAllBtn}
                    onclick={() => goto("/products/list")}>View All →</button
                >
            </div>
            <div class={styles.dealsGrid}>
                {#each dealProducts as product, i}
                    <ProductContainer keyNumber={i}>
                        <div class={styles.dealBadge}>NEW</div>
                        <div class={styles.productImage}>
                            <img src={product.img} alt={product.product_name} />
                        </div>
                        <div class={styles.dealContent}>
                            <div class={styles.dealCategory}>
                                {product.category}
                            </div>
                            <h2 class={styles.dealTitle}>
                                {product.product_name}
                            </h2>
                            <div class={styles.rating}>
                                <span class={styles.stars}>
                                    {#each Array(5) as _, i}
                                        <Rating
                                            keyNumber={i}
                                            rating={product?.rating}
                                        />
                                    {/each}
                                </span>
                                <span class={styles.ratingText}>{product.rating || 0}</span>
                            </div>
                        </div>
                        <a
                            class={styles.dealPrice}
                            href={`/products/details/${product.id}`}
                        >
                            <span class={styles.dealPriceText}>
                                BUY NOW
                                <span class={styles.dealPriceDetail}>-{product.price}$</span>
                            </span>
                        </a>
                    </ProductContainer>
                {/each}
            </div>
        </div>
    </section>
{/if}

<!-- PRODUCT LIST -->
<section id="product-list" class={styles.productsSection}>
    <div class={styles.container}>
        <div class={styles.sectionHeader}>
            <h2 class={styles.sectionTitle}>FREQUENTLY BOUGHT TOGETHER</h2>
        </div>

        {#if isLoading}
            <div class={styles.loading}>Loading products...</div>
        {:else if error}
            <div class={styles.error}>{error}</div>
        {:else}
            <div class={styles.productsContainer}>
                <div class={styles.featuredProduct}>
                    <article class="{styles.productCard} {styles.productFirst}">
                        {#if products?.[0]?.stock === 0}
                            <div class={styles.outOfStockBadge}>
                                OUT OF STOCK
                            </div>
                        {:else}
                            <div class={styles.discountBadge}>
                                {Math.floor(
                                    ((products?.[0]?.price * 0.4) /
                                        (products?.[0]?.price * 1.4)) *
                                        100,
                                )}% OFF
                            </div>
                            <div class={styles.hotBadge}>HOT</div>
                        {/if}
                        <a
                            class={styles.productImage}
                            href={`/products/details/${products?.[0]?.id}`}
                        >
                            <img
                                class="{styles.productImage} {styles.coverImg}"
                                src={products?.[0]?.img}
                                alt={products?.[0]?.product_name}
                            />

                            <div class={styles.productActions}>
                                <button
                                    type="button"
                                    class={styles.actionBtn}
                                    onclick={() => openQuickView(products?.[0])}
                                >
                                    <div class={styles.eyeImgContainer}>
                                        <img
                                            src={Eye}
                                            alt="eye"
                                            class={styles.eyeImg}
                                        />
                                    </div>
                                </button>

                                <button
                                    type="button"
                                    class={styles.actionBtn}
                                    onclick={() =>
                                        openAddToCartModal(products?.[0])}
                                    disabled={products?.[0]?.stock === 0}
                                >
                                    <div class={styles.cartImgContainer}>
                                        <img
                                            src={shoppingCart}
                                            alt={products?.[0]?.product_name}
                                            class={styles.cartImg}
                                        />
                                    </div>
                                </button>
                            </div>
                        </a>

                        <div class={styles.productInfo}>
                            <div class={styles.productCategory}>
                                {products?.[0]?.category}
                            </div>
                            <h3 class={styles.productName}>
                                {products?.[0]?.product_name}
                            </h3>
                            <div class={styles.rating}>
                                <span class={styles.stars}>
                                    {#each Array(5) as _, i}
                                        <Rating
                                            keyNumber={i}
                                            rating={Math.floor(
                                                products?.[0]?.rating || 0,
                                            )}
                                        />
                                    {/each}
                                </span>
                                <span class={styles.ratingText}>
                                    {products?.[0]?.rating || 0}
                                </span>
                            </div>
                            <div class={styles.productPrice}>
                                <span class={styles.priceCurrent}>
                                    ${products?.[0]?.price}
                                </span>
                                <span class={styles.priceOld}>
                                    ${(products?.[0]?.price * 1.4).toFixed(0)}
                                </span>
                            </div>
                            <div class={styles.productInformation}>
                                <span style="color: #5F6C72; line-height: 1.5">
                                    <span style="font-weight: bold">
                                       Description:
                                    </span>
                                    {products?.[0]?.description || "N/A"}
                                </span>
                            </div>
                            <div style="position: relative">
                                <button
                                    onclick={(e) => {
                                        e.stopPropagation();
                                        openAddToCartModal(products?.[0]);
                                    }}
                                    class="{styles.btnPrimary} {styles.addBtn}"
                                    disabled={products?.[0]?.stock === 0}
                                    title={products?.[0]?.stock === 0
                                        ? "Out of stock"
                                        : "Add to cart"}
                                >
                                    <img
                                        src={shoppingAddToCart}
                                        alt="shopping-cart"
                                        class="{styles.cartImg} {styles.addCartImg}"
                                    />
                                    ADD TO CART
                                </button>
                            </div>
                        </div>
                    </article>
                </div>

                <div class={styles.productsGrid}>
                    {#each products.slice(1) as product, i}
                        <ProductContainer keyNumber={i}>
                            {#if product.stock === 0}
                                <div class={styles.outOfStockBadge}>
                                    OUT OF STOCK
                                </div>
                            {:else}
                                <div class={styles.discountBadge}>
                                    {Math.floor(
                                        ((product?.price * 0.4) /
                                            (product?.price * 1.4)) *
                                            100,
                                    )}% OFF
                                </div>
                            {/if}
                            <a
                                class={styles.productImage}
                                href={`/products/details/${product.id}`}
                            >
                                <img
                                    class={styles.productImage}
                                    src={product.img}
                                    alt={product.product_name}
                                />
                                <div class={styles.productActions}>
                                    <button
                                        type="button"
                                        class={styles.actionBtn}
                                        onclick={() => openQuickView(product)}
                                    >
                                        <div class={styles.eyeImgContainer}>
                                            <img
                                                src={Eye}
                                                alt="eye"
                                                class={styles.eyeImg}
                                            />
                                        </div>
                                    </button>

                                    <button
                                        type="button"
                                        class={styles.actionBtn}
                                        onclick={() =>
                                            openAddToCartModal(product)}
                                        disabled={product.stock === 0}
                                    >
                                        <img
                                            src={shoppingCart}
                                            alt="cart_img"
                                            class={styles.cartImg}
                                        />
                                    </button>
                                </div>
                            </a>

                            <div class={styles.productInfo}>
                                <div class={styles.productCategory}>
                                    {product.category}
                                </div>
                                <h3 class={styles.productName}>
                                    {product.product_name}
                                </h3>
                                <div class={styles.rating}>
                                    <span class={styles.stars}>
                                        {#each Array(5) as _, i}
                                            <Rating
                                                keyNumber={i}
                                                rating={Math.floor(
                                                    product.rating || 0,
                                                )}
                                            />
                                        {/each}
                                    </span>
                                    <span class={styles.ratingText}>
                                        {product.rating || 0}
                                    </span>
                                </div>
                                <div class={styles.productPrice}>
                                    <span class={styles.priceCurrent}>
                                        ${product.price}
                                    </span>
                                    <span class={styles.priceOld}>
                                        ${(product.price * 1.4).toFixed(0,)}
                                    </span>
                                </div>
                            </div>
                        </ProductContainer>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</section>

<!-- ADD TO CART MODAL -->
{#if isLoggedIn && showAddToCartModal && addToCartProduct}
    <div
        class={styles.modalBackdrop}
        role="button"
        tabindex="0"
        aria-label="Close add to cart dialog"
        onkeydown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
                closeAddToCartModal();
            }
        }}
    >
        <div
            class="{styles.modal} {styles.modalSm}"
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-to-cart-title"
        >
            <button
                type="button"
                class={styles.modalClose}
                aria-label="Close"
                onclick={closeAddToCartModal}
            >
                ×
            </button>

            <div class={styles.modalContent}>
                <div class={styles.modalImageSm}>
                    <img
                        src={addToCartProduct.img}
                        alt={addToCartProduct.product_name}
                    />
                </div>

                <div class={styles.modalDetails}>
                    <h3 id="add-to-cart-title">
                        {addToCartProduct.product_name}
                    </h3>

                    <div class={styles.modalPrice}>
                        <span class={styles.priceLarge}>
                            ${addToCartProduct.price}
                        </span>
                    </div>

                    <div class={styles.quantitySelector}>
                        <label for="quantity-input"> Quantity: </label>
                        <input
                            id="quantity-input"
                            type="number"
                            min="1"
                            max={addToCartProduct.stock ?? 99}
                            bind:value={addToCartQuantity}
                        />
                    </div>

                    <div class={styles.modalActions}>
                        <button
                            type="button"
                            class={styles.btnPrimaryFull}
                            onclick={confirmAddToCart}
                            disabled={addToCartQuantity <= 0}
                        >
                            Add to Cart
                        </button>

                        <button
                            type="button"
                            class={styles.btnSecondaryFull}
                            onclick={closeAddToCartModal}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- CART LIST MODAL -->
<RequireSignInModal
    {showAddToCardListModal}
    {closeCartList}
    {isLoggedIn}
    {cartItems}
    shoppingCartImage={shoppingCart}
    {redirectToLogin}
/>
<MessageModal show={isConfirmModalClose} {message} onClose />

<!-- Footer -->
<Footer />
