<script lang="ts">
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { jwtDecode } from "jwt-decode";
    import { cart, type Product, type CartItem } from "$lib/stores/CartStore";
    import { derived } from "svelte/store";
    import { clientApi } from "../hooks/apiFetch";
    import styles from "$lib/styles/landing/landing.module.css"
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
    /** Products list */
    let products: Product[] = [];
    let query = "";
    let category = "All";
    let sortBy = "featured";
    let quickView: Product | null = null;

    // categories
    let categories = ["All", "Multirotor", "Fixed-wing"];

    let isLoading = false;
    let error = "";
    let mounted = false;

    let currentPage = 1;
    let limit = 5;

    /** Add to cart modal */
    let addToCartProduct: Product | null = null;
    let showAddToCartModal = false;
    let showAddToCardListModal = false;
    let addToCartQuantity = 1;
    let isLoggedIn = false;

    // Subscribe to cart store
    let cartItems: CartItem[] = [];
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
        goto(newUrl, { replaceState: true, noScroll: true });
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
        isLoggedIn = isTokenValid(token);
        fetchProducts();
    });

    $: topFive = products.slice(0, 5);

    const cartCount = derived(cart, ($cart) =>
        $cart.reduce((total, item) => total + item.quantity, 0),
    );

    function openQuickView(product: Product) {
        quickView = product;
    }

    function closeQuickView() {
        quickView = null;
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

    function deleteCart(id: string) {
        cart.removeItem(id);
    }

    function confirmAddToCart() {
        if (!addToCartProduct) return;
        cart.addItem(addToCartProduct, addToCartQuantity);
        closeAddToCartModal();
        alert(
            `Added ${addToCartQuantity} × ${addToCartProduct.product_name} to cart!`,
        );
    }

    const handleSearch = () => {
        currentPage = 1;
        fetchProducts(null, "initial");
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

<header class={styles.header} class:anim-in={mounted}>
    <div class={styles.container}>
        <div class={styles.headerMain}>
            <div class={styles.brand}>
                <div class={styles.logo}>
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <rect width="32" height="32" rx="6" fill="#000000" />
                        <path d="M16 8L20 14H12L16 8Z" fill="white" />
                        <circle cx="16" cy="18" r="3" fill="white" />
                        <path
                            d="M12 22L16 20L20 22"
                            stroke="white"
                            stroke-width="2"
                        />
                    </svg>
                </div>
                <div>
                    <div style="font-weight:700; font-size: 20px, color: #000000">
                        DRONERACK
                    </div>
                </div>
            </div>

            <div class={styles.searchBar}>
                <img src={searchIcon} alt="search_icon" class={styles.searchIcon} />
                <input
                    placeholder="Search for drones, parts, accessories..."
                    bind:value={query}
                    onkeypress={(e) => e.key === "Enter" && handleSearch()}
                />
            </div>

            <div class={styles.headerActions}>
                <div class={styles.headerBtn}>
                    <img src={user} alt="user" />
                    {#if isLoggedIn}
                        <button class={styles.logoutBtn} onclick={logout}>
                            Logout
                        </button>
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
                    {#if $cartCount > 0}
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
                    <div class={styles.featureDesc}>100% money-back guarantee</div>
                </div>
            </div>
            <div class={styles.featureItem}>
                <img class={styles.featureIcon} src={CreditCard} alt="credit_card" />
                <div>
                    <div class={styles.featureTitle}>Secure Payment</div>
                    <div class={styles.featureDesc}>Your money is safe</div>
                </div>
            </div>
            <div class={styles.featureItem}>
                <img class={styles.featureIcon} src={HeadPhone} alt="headphone" />
                <div>
                    <div class={styles.featureTitle}>Support 24/7</div>
                    <div class={styles.featureDesc}>Live contact/message</div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- TODAY'S DEALS -->
{#if topFive.length}
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
                {#each topFive as product, i}
                    <div
                        class={styles.dealCard}
                        style={`animation-delay: ${i * 60}ms`}
                    >
                        <div class={styles.dealBadge}>🔥 HOT</div>
                        <img src={product.img} alt={product.product_name} />
                        <div class={styles.dealContent}>
                            <div class={styles.dealCategory}>{product.category}</div>
                            <h2 class={styles.dealTitle}>{product.product_name}</h2>
                            <div class={styles.rating}>
                                <span class={styles.stars}>
                                    {#each Array(5) as _, i}
                                        <svg
                                            viewBox="0 0 24 24"
                                            class:filled={i <
                                                Math.floor(product.rating || 0)}
                                        >
                                            <path
                                                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                            />
                                        </svg>
                                    {/each}
                                </span>
                                <span class={styles.ratingText}
                                    >{product.rating || 0}</span
                                >
                            </div>
                        </div>
                        <a
                            class={styles.dealPrice}
                            href={`/products/details/${product.id}`}
                        >
                            <span class={styles.dealPriceText}>
                                BUY NOW
                                <span class={styles.dealPriceDetail}>
                                    -{product.price}$
                                </span>
                            </span>
                        </a>
                    </div>
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
            <div class={styles.controls}>
                <select
                    bind:value={category}
                    onchange={handleSearch}
                    class={styles.filterSelect}
                >
                    {#each categories as c}<option value={c}>{c}</option>{/each}
                </select>
                <select
                    bind:value={sortBy}
                    onchange={handleSearch}
                    class={styles.filterSelect}
                >
                    <option value="featured">Featured</option>
                    <option value="price-asc">Price: Low → High</option>
                    <option value="price-desc">Price: High → Low</option>
                    <option value="rating">Top Rated</option>
                </select>
            </div>
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
                            <div class={styles.outOfStockBadge}>OUT OF STOCK</div>
                        {:else}
                            <div class={styles.discountBadge}>HOT</div>
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
                                    onclick={() => openAddToCartModal(products?.[0])}
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
                                        <svg
                                            viewBox="0 0 24 24"
                                            class:filled={i <
                                                Math.floor(
                                                    products?.[0]?.rating || 0,
                                                )}
                                        >
                                            <path
                                                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                            />
                                        </svg>
                                    {/each}
                                </span>
                                <span class={styles.ratingText}
                                    >{products?.[0]?.rating || 0}</span
                                >
                            </div>
                            <div class={styles.productPrice}>
                                <span class={styles.priceCurrent}
                                    >${products?.[0]?.price}</span
                                >
                                <span class={styles.priceOld}
                                    >${(products?.[0]?.price * 1.4).toFixed(0)}</span
                                >
                            </div>
                            <div class={styles.productInformation}>
                                <span style="color: #5F6C72"
                                    ><span style="font-weight: bold"
                                        >Description:</span
                                    >
                                    {products?.[0]?.description || "N/A"}</span
                                >
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
                    {#each products.slice(1).filter(product => 
                        product && 
                        product.id && 
                        product.product_name && 
                        product.img &&
                        !isNaN(product.price)
                    ) as product, i}
                        <article
                            class={styles.productCard}
                            style={`animation-delay: ${i * 40}ms`}
                        >
                            {#if product.stock === 0}
                                <div class={styles.outOfStockBadge}>
                                    OUT OF STOCK
                                </div>
                            {:else if i % 3 === 0}
                                <div class={styles.discountBadge}>-32% OFF</div>
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
                                            <svg
                                                viewBox="0 0 24 24"
                                                class:filled={i <
                                                    Math.floor(
                                                        product.rating || 0,
                                                    )}
                                            >
                                                <path
                                                    d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                                />
                                            </svg>
                                        {/each}
                                    </span>
                                    <span class={styles.ratingText}>{product.rating || 0}</span>
                                </div>
                                <div class={styles.productPrice}>
                                    <span class={styles.priceCurrent}>${product.price}</span>
                                    <span class={styles.priceOld}>${(product.price * 1.4).toFixed(0)}</span>
                                </div>
                            </div>
                        </article>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</section>

<!-- QUICK VIEW MODAL -->
{#if quickView}
    <div
        class={styles.modalBackdrop}
        role="button"
        tabindex="0"
        aria-label="Close quick view"
        onclick={closeQuickView}
        onkeydown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
                closeQuickView();
            }
        }}
    >
        <div
            class={styles.modal}
            role="dialog"
            aria-modal="true"
            aria-labelledby="quick-view-title"
        >
            <button
                type="button"
                class={styles.modalClose}
                aria-label="Close"
                onclick={closeQuickView}
            >
                ×
            </button>

            <div class={styles.modalContent}>
                <div class={styles.modalImage}>
                    <img src={quickView.img} alt={quickView.product_name} />
                </div>

                <div class={styles.modalDetails}>
                    <div class={styles.modalCategory}>
                        {quickView.category}
                    </div>

                    <h2 id="quick-view-title" class={styles.modalTitle}>
                        {quickView.product_name}
                    </h2>

                    <div class={styles.modalRating}>
                        {"⭐".repeat(Math.floor(quickView.rating || 0))}
                        <span>
                            ({quickView.rating?.toFixed(1) || "—"})
                        </span>
                    </div>

                    <p class={styles.modalDescription}>
                        {quickView.description ||
                            "High-quality drone perfect for photography and aerial exploration."}
                    </p>

                    <div class={styles.modalPrice}>
                        <span class={styles.priceLarge}>
                            ${quickView.price}
                        </span>
                        <span class={styles.priceOldLarge}>
                            ${(quickView.price * 1.4).toFixed(0)}
                        </span>
                    </div>
                    <div class={styles.modalActions}>
                        <button
                            type="button"
                            class={styles.btnAddCart}
                            onclick={() => {
                                openAddToCartModal(quickView);
                                closeQuickView();
                            }}
                            disabled={quickView.stock === 0}
                        >
                            Add to Cart
                        </button>

                        <a
                            class={styles.btnBuyNow}
                            href={`/products/details/${quickView.id}`}
                        >
                            Buy Now
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

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
{#if showAddToCardListModal}
    <div
        class={styles.modalBackdrop}
        role="button"
        tabindex="0"
        aria-label="Close cart dialog"
        onkeydown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
                closeCartList();
            }
        }}
    >
        {#if isLoggedIn}
            <div
                class="{styles.modal} {styles.modalCart}"
                role="dialog"
                aria-modal="true"
                aria-labelledby="cart-dialog-title"
            >
                <button
                    type="button"
                    class={styles.modalClose}
                    aria-label="Close"
                    onclick={closeCartList}
                >
                    ×
                </button>

                <h2 id="cart-dialog-title" class={styles.modalTitle}>
                    Your Shopping Cart
                </h2>

                {#if cartItems.length === 0}
                    <div class={styles.emptyCart}>
                        <div class={styles.emptyIcon}>
                            <img src={shoppingCart} alt="cart_img" />
                        </div>
                        <p>Your cart is empty</p>
                        <button
                            type="button"
                            class={styles.btnPrimaryFull}
                            onclick={closeCartList}
                        >
                            Continue Shopping
                        </button>
                    </div>
                {:else}
                    <div class={styles.cartItems}>
                        {#each cartItems as item}
                            <div class={styles.cartItem}>
                                <img src={item.img} alt={item.product_name} />

                                <div class={styles.cartItemDetails}>
                                    <h4>{item.product_name}</h4>
                                    <div class={styles.cartItemMeta}>
                                        {item.category} • ${item.price}
                                    </div>
                                    <div class={styles.cartItemQuantity}>
                                        Qty: {item.quantity}
                                    </div>
                                </div>

                                <div class={styles.cartItemActions}>
                                    <div class={styles.cartItemPrice}>
                                        ${Number((item.price * item.quantity).toFixed(2))}
                                    </div>
                                    <button
                                        type="button"
                                        class={styles.removeBtn}
                                        aria-label="Remove item"
                                        onclick={() => deleteCart(item.id!)}
                                    >
                                        Remove
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>
                    <div class={styles.cartTotal}>
                        <div class="{styles.totalRow} {styles.totalFinal}">
                            <span>Total:</span>
                            <span>
                                ${Number(cart.getTotalPrice().toFixed(2))}
                            </span>
                        </div>
                    </div>

                    <div class={styles.cartActions}>
                        <button
                            type="button"
                            class={styles.btnSecondaryFull}
                            onclick={closeCartList}
                        >
                            Continue Shopping
                        </button>

                        <a class={styles.btnPrimaryFull} href="/checkout">
                            Proceed to Checkout
                        </a>
                    </div>
                {/if}
            </div>
        {:else}
            <div
                class="{styles.modal} {styles.modalSm}"
                role="dialog"
                aria-modal="true"
                aria-labelledby="login-required-title"
            >
                <button
                    type="button"
                    class={styles.modalClose}
                    aria-label="Close"
                    onclick={closeCartList}
                >
                    ×
                </button>

                <div class={styles.loginRequired}>
                    <div class={styles.loginIcon}>🔒</div>

                    <h3 id="login-required-title">Login Required</h3>

                    <p>
                        Please log in to view your cart and complete your
                        purchase.
                    </p>

                    <div class={styles.modalActions}>
                        <button
                            type="button"
                            class={styles.btnPrimaryFull}
                            onclick={redirectToLogin}
                        >
                            Login
                        </button>

                        <button
                            type="button"
                            class={styles.btnSecondaryFull}
                            onclick={closeCartList}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    </div>
{/if}

<!-- FOOTER -->
<footer class={styles.footer}>
    <div class={styles.container}>
        <div class={styles.footerContent}>
            <div class={styles.footerCol}>
                <div class={styles.footerLogo}>
                    <span class={styles.logoIcon}>🚁</span>
                    <span class={styles.logoText}>DRONERACK</span>
                </div>
                <p>
                    Your trusted marketplace for drones, parts, and accessories.
                </p>
            </div>
            <div class={styles.footerCol}>
                <h4>Quick Links</h4>
                <a href="#">About Us</a>
                <a href="#">Contact</a>
                <a href="#">FAQs</a>
            </div>
            <div class={styles.footerCol}>
                <h4>Support</h4>
                <a href="#">Shipping Info</a>
                <a href="#">Returns</a>
                <a href="#">Warranty</a>
            </div>
            <div class={styles.footerCol}>
                <h4>Follow Us</h4>
                <div class={styles.socialLinks}>
                    <a href="#">Facebook</a>
                    <a href="#">Twitter</a>
                    <a href="#">Instagram</a>
                </div>
            </div>
        </div>
        <div class={styles.footerBottom}>
            <p>© 2024 DroneRack. All rights reserved.</p>
        </div>
    </div>
</footer>

