<script lang="ts">
    import { goto } from "$app/navigation";
    import { env } from "$env/dynamic/public";
    import { onMount } from "svelte";
    import { jwtDecode } from "jwt-decode";
    import { cart, type Product, type CartItem } from "$lib/stores/CartStore";

    /** Products list */
    let products: Product[] = [];
    let query = "";
    let category = "All";
    let sortBy = "featured";
    let quickView: Product | null = null;

    let isLoading = false;
    let error = "";
    let mounted = false;

    // cursor-based pagination
    let nextCursor: string | null = null;
    let prevCursor: string | null = null;
    let currentCursor: string | null = null;
    let cursorHistory: (string | null)[] = []; // Stack to track cursor history
    let currentPage = 1;
    let totalRecords = 0;
    let limit = 5

    /** Add to cart modal */
    let addToCartProduct: Product | null = null;
    let showAddToCartModal = false;
    let showAddToCardListModal = false;
    let addToCartQuantity = 1;
    let isLoggedIn = false;
    
    // Subscribe to cart store
    let cartItems: CartItem[] = [];
    cart.subscribe(value => {
        cartItems = value;
    });

    /** Fetch products from API */
    const fetchProducts = async (
        cursor: string | null = null,
        direction: 'next' | 'prev' | 'initial' = 'initial'
    ): Promise<void> => {
        isLoading = true;
        error = "";

        try {
            const token = localStorage.getItem("accessToken");
            const params = new URLSearchParams();

            if (query) params.append("search_product", query);
            if (category && category !== "All")
                params.append("category", category);
            if (sortBy) params.append("sort", sortBy);
            if (limit) params.append("limit", String(limit));
            if (cursor) params.append("next_cursor", cursor);

            const url = `${env.PUBLIC_API_URL}/products?${params.toString()}`;

            const res = await fetch(url, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);

            const data = await res.json();

            products = (data.search_result || []).map(
                (p: Product, index: number) => ({
                    ...p,
                    img: `https://picsum.photos/seed/drone${index + 1}/600/400`,
                    rating: 4 + Math.random() * 1,
                    stock: Math.floor(3 + Math.random() * 15),
                }),
            );

            totalRecords = data.total_product || products.length;
            nextCursor = data.next_cursor || null;
            currentCursor = cursor;

            // Update page number based on direction
            if (direction === 'next') {
                currentPage++;
            } else if (direction === 'prev') {
                currentPage--;
            } else {
                currentPage = 1;
            }

            mounted = true;
        } catch (e) {
            console.error(e);
            error = "Không thể tải danh sách drone. Vui lòng thử lại.";
        } finally {
            isLoading = false;
        }
    };

    export function debounce(fn, delay = 300) {
        let timeout: number | undefined;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                fn(...args);
            }, delay);
        };
    }

    onMount(() => {
        isLoggedIn = !!localStorage.getItem("accessToken");
        fetchProducts();
    });

    // top 5 section
    $: topFive = products.slice(0, 5);

    // categories
    $: categories = ["All", ...new Set(products.map((p) => p.category))];

    // Cart total count
    $: cartCount = cart.getTotalCount();

    // Has more pages
    $: hasPrevPage = currentPage > 1;
    $: hasNextPage = nextCursor !== null;

    // actions
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

    function handleNext() {
        if (!hasNextPage) return;
        
        // Save current cursor to history before moving forward
        cursorHistory.push(currentCursor);
        
        // Fetch next page
        fetchProducts(nextCursor, 'next');

        // Scroll to product list
        const listEl = document.getElementById("product-list");
        if (listEl) {
            listEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    function handlePrev() {
        if (!hasPrevPage) return;
        
        // Get previous cursor from history
        const previousCursor = cursorHistory.pop() ?? null;
        
        // Fetch previous page
        fetchProducts(previousCursor, 'prev');

        // Scroll to product list
        const listEl = document.getElementById("product-list");
        if (listEl) {
            listEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    const debouncedFetch = debounce(() => {
        // Reset pagination state when filters change
        cursorHistory = [];
        currentCursor = null;
        nextCursor = null;
        currentPage = 1;
        fetchProducts(null, 'initial');
    }, 400);

    async function logout() {
        try {
            const token = localStorage.getItem("accessToken");
            const decoded = token ? jwtDecode<{ id: string }>(token) : null;
            const currentUserId = decoded?.id;
            
            const res = await fetch(`${env.PUBLIC_API_URL}/auth/logout`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ id: currentUserId }),
            });

            if (!res.ok) {
                console.error("Logout API failed:", res.status);
            }
        } catch (err) {
            console.error("Logout request error:", err);
        } finally {
            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
            cart.clear();
            isLoggedIn = false;
            goto("/login");
        }
    }
</script>

<!-- HEADER -->
<header class:anim-in={mounted}>
    <div class="brand">
        <div class="logo">DR</div>
        <div>
            <div style="font-weight:700">DroneRack</div>
            <div style="font-size:12px; color:#64748b">Buy • Sell • Fly</div>
        </div>
    </div>
    <nav>
        <a href="#">Explore</a>
        <a href="#">Sell</a>
        <button
            style="background-color: transparent; border-color: transparent; position:relative"
            on:click={() => openCartList()}
        >
            My Orders
            {#if cartCount > 0}
                <span class="cart-badge">{cartCount}</span>
            {/if}
        </button>
        {#if isLoggedIn}
            <button
                style="background-color: transparent; border: transparent; margin-left: 10px; color:#ef4444; font-weight:600; cursor:pointer"
                on:click={logout}
            >
                Log out
            </button>
        {:else}
            <button
                style="background-color: transparent; border: transparent; margin-left: 10px; color:#ef4444; font-weight:600; cursor:pointer"
                on:click={() => goto("/login")}
            >
                Sign in
            </button>
        {/if}
    </nav>
</header>

<!-- HERO -->
<section class="hero" class:anim-in={mounted}>
    <div class="hero-left">
        <h1 style="font-size:32px; margin:0">
            Marketplace cho Drone — mua bán, so sánh, và review
        </h1>
        <p style="color:#334155; margin-top:10px">
            Tìm drone phù hợp cho nhiếp ảnh, quay phim, hoặc phiêu lưu. So sánh
            cấu hình, giá, và đánh giá từ cộng đồng.
        </p>

        <div class="controls">
            <input
                placeholder="Tìm kiếm drone..."
                bind:value={query}
                on:input={debouncedFetch}
                style="padding:10px 12px; border-radius:10px; border:1px solid #e2e8f0; min-width:260px"
            />

            <select
                bind:value={category}
                on:change={debouncedFetch}
                style="padding:10px 12px; border-radius:10px; border:1px solid #e2e8f0"
            >
                {#each categories as c}
                    <option value={c}>{c}</option>
                {/each}
            </select>

            <select
                bind:value={sortBy}
                on:change={debouncedFetch}
                style="padding:10px 12px; border-radius:10px; border:1px solid #e2e8f0"
            >
                <option value="featured">Featured</option>
                <option value="price-asc">Price: Low → High</option>
                <option value="price-desc">Price: High → Low</option>
                <option value="rating">Top Rated</option>
            </select>
        </div>

        <div style="display:flex; gap:10px; margin-top:6px">
            <button class="btn-primary" on:click={() => goto("/products/list")}>Mua ngay</button>
            <button class="btn-ghost">Bán drone</button>
        </div>
    </div>

    <div class="hero-right">
        <img
            alt="hero drone"
            src="https://picsum.photos/seed/hero/720/440"
            style="max-width:100%; border-radius:12px; box-shadow:0 18px 40px rgba(2,6,23,0.08)"
        />
    </div>
</section>

<!-- TOP 5 -->
{#if topFive.length}
    <section class="top-list-section">
        <div class="top-list-card">
            <div class="top-list-header">
                <span class="top-list-title">Top 5 Drone nổi bật</span>
                <span class="top-list-sub">
                    Dựa trên kết quả trang hiện tại
                </span>
            </div>
            <div class="top-list-scroll">
                {#each topFive as p}
                    <div class="top-list-item">
                        <div class="top-list-thumb">
                            <img src={p.img} alt={p.product_name} />
                        </div>
                        <div class="top-list-meta">
                            <div class="top-list-name">{p.product_name}</div>
                            <div class="top-list-info">
                                {p.category} • ${p.price} • Rating: {p.rating?.toFixed(
                                    1,
                                ) ?? "—"}
                            </div>
                        </div>
                        <button
                            class="top-list-btn"
                            on:click={() => openQuickView(p)}>Xem</button
                        >
                    </div>
                {/each}
            </div>
        </div>
    </section>
{/if}

<!-- PRODUCT LIST -->
<section id="product-list">
    <div style="padding:6px 24px; color:#475569; font-size:13px">
        {#if isLoading}
            Đang tải sản phẩm...
        {:else if error}
            {error}
        {:else}
            {products.length} sản phẩm trên trang này • Trang {currentPage} • Tổng: {totalRecords} sản phẩm
        {/if}
    </div>

    <div class="grid">
        {#if !isLoading && !error}
            {#each products as p, i}
                <article
                    class="card anim-in"
                    style={`animation-delay: ${80 + i * 40}ms`}
                    on:click={() => goto(`/products/details/${p.id}`)}
                >
                    <img alt={p.product_name} src={p.img} />
                    <div class="card-body">
                        <div
                            style="display:flex; justify-content:space-between; align-items:center"
                        >
                            <div style="font-weight:700">{p.product_name}</div>
                            <div class="badge">{p.category}</div>
                        </div>

                        <div
                            style="display:flex; justify-content:space-between; align-items:center; gap:10px"
                        >
                            <div>
                                <div class="price">${p.price}</div>
                                <div style="font-size:12px; color:#64748b">
                                    Rating: {p.rating?.toFixed(1) ?? "—"} • Stock:
                                    {p.stock ?? "—"}
                                </div>
                            </div>
                            <div
                                style="display:flex; flex-direction:column; gap:8px"
                            >
                                <button
                                    on:click={(e) => {
                                        e.stopPropagation();
                                        openAddToCartModal(p);
                                    }}
                                    class="btn-small-primary">Add</button
                                >
                                <button
                                    on:click={(e) => {
                                        e.stopPropagation();
                                        openQuickView(p);
                                    }}
                                    class="btn-small-ghost">Quick View</button
                                >
                            </div>
                        </div>
                    </div>
                </article>
            {/each}
        {/if}
    </div>

    {#if !isLoading && !error && (hasPrevPage || hasNextPage)}
        <div class="pagination">
            <button
                class="pagination-btn"
                on:click={handlePrev}
                disabled={!hasPrevPage || isLoading}
            >
                ‹ Prev
            </button>
            
            <div class="pagination-pages">
                <span style="color:#64748b; font-size:14px">
                    Trang {currentPage}
                </span>
            </div>
            
            <button
                class="pagination-btn"
                on:click={handleNext}
                disabled={!hasNextPage || isLoading}
            >
                Next ›
            </button>
        </div>
    {/if}
</section>

<!-- QUICK VIEW MODAL -->
{#if quickView}
    <div class="modal-backdrop" on:click={closeQuickView}>
        <div class="modal" on:click|stopPropagation>
            <div style="display:flex; gap:16px; align-items:flex-start">
                <img
                    src={quickView.img}
                    alt={quickView.product_name}
                    style="width:400px; max-width:40%; border-radius:8px; object-fit:cover"
                />
                <div style="flex:1">
                    <h2>{quickView.product_name}</h2>
                    <div style="color:#64748b; margin-top:6px">
                        {quickView.category} • Rating: {quickView.rating?.toFixed(
                            1,
                        ) ?? "—"}
                    </div>
                    <p style="margin-top:12px; color:#334155">
                        Mô tả ngắn: demo content
                    </p>
                    <div
                        style="display:flex; gap:12px; margin-top:18px; align-items:center"
                    >
                        <div style="font-size:20px; font-weight:800">
                            ${quickView.price}
                        </div>
                        <button
                            on:click={() => openAddToCartModal(quickView)}
                            class="btn-primary">Add to cart</button
                        >
                        <button on:click={closeQuickView} class="btn-secondary"
                            >Close</button
                        >
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- ADD TO CART MODAL OR LOGIN REQUIRED -->
{#if isLoggedIn}
    {#if showAddToCartModal && addToCartProduct}
        <!-- Add to Cart Modal -->
        <div class="modal-backdrop" on:click={closeAddToCartModal}>
            <div class="modal" on:click|stopPropagation>
                <div
                    style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap"
                >
                    <img
                        src={addToCartProduct.img}
                        alt={addToCartProduct.product_name}
                        style="width:200px; max-width:40%; border-radius:8px; object-fit:cover"
                    />
                    <div style="flex:1; min-width:220px">
                        <h2>{addToCartProduct.product_name}</h2>
                        <div style="color:#64748b; margin-top:6px">
                            {addToCartProduct.category} • Rating: {addToCartProduct.rating?.toFixed(
                                1,
                            ) ?? "—"}
                        </div>
                        <p style="margin-top:12px; color:#334155">
                            Mô tả ngắn: demo content
                        </p>
                        <div
                            style="margin-top:16px; display:flex; align-items:center; gap:12px"
                        >
                            <div style="font-size:20px; font-weight:800">
                                ${addToCartProduct.price}
                            </div>
                            <div>
                                <label>Quantity:</label>
                                <input
                                    type="number"
                                    min="1"
                                    max={addToCartProduct.stock ?? 99}
                                    bind:value={addToCartQuantity}
                                    style="width:60px; padding:4px; border-radius:6px; border:1px solid #ccc"
                                />
                            </div>
                        </div>
                        <div style="display:flex; gap:12px; margin-top:18px">
                            <button
                                on:click={confirmAddToCart}
                                class="btn-primary">Add to Cart</button
                            >
                            <button
                                on:click={closeAddToCartModal}
                                class="btn-secondary">Cancel</button
                            >
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {:else if showAddToCardListModal}
        <div class="modal-backdrop" on:click={closeCartList}>
            <div
                class="modal"
                on:click|stopPropagation
                style="max-width:600px;"
            >
                <h2 style="margin-bottom:12px">Giỏ hàng của bạn</h2>

                {#if cartItems.length === 0}
                    <p>Chưa có sản phẩm nào trong giỏ hàng.</p>
                {:else}
                    <div
                        style="display:flex; flex-direction:column; gap:12px; max-height:340px; overflow-y:auto"
                    >
                        {#each cartItems as item}
                            <div
                                style="display:flex; gap:12px; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:10px"
                            >
                                <img
                                    src={item.img}
                                    alt={item.product_name}
                                    style="width:80px; height:80px; border-radius:8px; object-fit:cover"
                                />

                                <div style="flex:1">
                                    <div style="font-weight:700">
                                        {item.product_name}
                                    </div>
                                    <div style="font-size:13px; color:#64748b">
                                        {item.category} • ${item.price}
                                    </div>
                                    <div style="margin-top:4px; font-size:13px">
                                        Quantity: {item.quantity}
                                    </div>
                                </div>

                                <button
                                    class="btn-small-ghost"
                                    on:click={() => deleteCart(item.id!)}
                                >
                                    Remove
                                </button>
                            </div>
                        {/each}
                    </div>
                    
                    <div style="margin-top:16px; padding-top:12px; border-top:2px solid #e2e8f0">
                        <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:700">
                            <span>Total:</span>
                            <span>${cart.getTotalPrice().toFixed(2)}</span>
                        </div>
                    </div>
                {/if}

                <div
                    style="margin-top:18px; display:flex; justify-content:flex-end; gap:10px"
                >
                    <button on:click={closeCartList} class="btn-secondary"
                        >Close</button
                    >
                    <button
                        class={cartItems.length === 0
                            ? "btn-disabled"
                            : "btn-primary"}
                        on:click={() => goto("/checkout")}
                        disabled={cartItems.length === 0}
                    >
                        Checkout
                    </button>
                </div>
            </div>
        </div>
    {/if}
{:else if !isLoggedIn && showAddToCardListModal}
    <!-- Login Required Modal -->
    <div class="modal-backdrop" on:click={closeCartList}>
        <div
            class="modal"
            on:click|stopPropagation
            style="padding:24px; text-align:center"
        >
            <h2>Please Login</h2>
            <p>You need to log in to view your cart.</p>
            <div
                style="margin-top:16px; display:flex; justify-content:center; gap:12px"
            >
                <button on:click={redirectToLogin} class="btn-primary"
                    >Login</button
                >
                <button on:click={closeCartList} class="btn-secondary"
                    >Cancel</button
                >
            </div>
        </div>
    </div>
{/if}

<style>
    /* Basic responsive layout, modern clean look */
    :global(body) {
        font-family:
            system-ui,
            -apple-system,
            "Segoe UI",
            Roboto,
            "Helvetica Neue",
            Arial;
        margin: 0;
        background: linear-gradient(180deg, #f8fbff 0%, #ffffff 40%);
        color: #0f172a;
    }

    /* ====== ANIMATION KEYFRAMES ====== */
    @keyframes fadeDown {
        from {
            opacity: 0;
            transform: translateY(-12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(16px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes modalIn {
        from {
            opacity: 0;
            transform: translateY(12px) scale(0.96);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* ====== LAYOUT ====== */

    header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 24px;
        position: sticky;
        top: 0;
        z-index: 10;
        backdrop-filter: blur(18px);
        background: linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.9) 0%,
            rgba(255, 255, 255, 0.75) 60%,
            transparent 100%
        );
        border-bottom: 1px solid rgba(226, 232, 240, 0.7);
        opacity: 0;
        transform: translateY(-12px);
    }

    header.anim-in {
        animation: fadeDown 420ms ease forwards;
    }

    .brand {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .logo {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: radial-gradient(circle at 20% 0, #22c55e, #0f766e);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        box-shadow:
            0 0 0 1px rgba(34, 197, 94, 0.5),
            0 16px 30px rgba(15, 118, 110, 0.4);
    }

    nav {
        display: flex;
        align-items: center;
    }

    nav a {
        margin-right: 16px;
        color: #0f172a;
        text-decoration: none;
        font-size: 14px;
        position: relative;
        padding-bottom: 2px;
    }

    nav a:last-child {
        margin-right: 0;
    }

    nav a::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: -2px;
        width: 0;
        height: 2px;
        border-radius: 999px;
        background: linear-gradient(90deg, #0ea5e9, #22c55e);
        transition: width 180ms ease;
    }

    nav a:hover::after {
        width: 100%;
    }

    .cart-badge {
        position: absolute;
        top: -6px;
        right: -8px;
        background: #ef4444;
        color: white;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 6px;
        min-width: 18px;
        text-align: center;
    }

    .hero {
        padding: 36px 24px;
        display: flex;
        gap: 24px;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        opacity: 0;
        transform: translateY(16px);
    }

    .hero.anim-in {
        animation: fadeUp 460ms ease 80ms forwards;
    }

    .hero-left {
        max-width: 640px;
    }

    .hero-right {
        flex: 1;
        min-width: 280px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .controls {
        display: flex;
        gap: 12px;
        align-items: center;
        margin: 18px 0;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 18px;
        padding: 12px 24px 40px;
    }

    .card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(12, 20, 40, 0.06);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        position: relative;
        transform: translateY(6px);
        opacity: 0;
        transition:
            transform 160ms ease,
            box-shadow 160ms ease,
            border 160ms ease,
            background 160ms ease;
        border: 1px solid transparent;
        cursor: pointer;
    }

    .card.anim-in {
        animation: fadeUp 380ms ease forwards;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(12, 20, 40, 0.12);
    }

    .card img {
        width: 100%;
        height: 160px;
        object-fit: cover;
        transition: transform 220ms ease;
    }

    .card:hover img {
        transform: scale(1.05);
    }

    .card-body {
        padding: 12px 14px 14px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        flex: 1;
    }

    .price {
        font-weight: 700;
    }

    .badge {
        font-size: 12px;
        padding: 6px 8px;
        background: #eef2ff;
        border-radius: 999px;
    }

    .footer {
        padding: 22px 24px;
        text-align: center;
        font-size: 14px;
        color: #475569;
    }

    /* ====== TOP VERTICAL LIST ====== */

    .top-list-section {
        padding: 0 24px 16px;
        margin-top: -8px;
    }

    .top-list-card {
        border-radius: 16px;
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        padding: 14px 16px;
    }

    .top-list-header {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin-bottom: 8px;
    }

    .top-list-title {
        font-weight: 600;
        font-size: 14px;
        color: #0f172a;
    }

    .top-list-sub {
        font-size: 12px;
        color: #64748b;
    }

    .top-list-scroll {
        max-height: 240px;
        overflow-y: auto;
        padding-right: 4px;
    }

    .top-list-scroll::-webkit-scrollbar {
        width: 6px;
    }

    .top-list-scroll::-webkit-scrollbar-thumb {
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.7);
    }

    .top-list-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 4px;
        border-radius: 10px;
        transition:
            background 140ms ease,
            transform 140ms ease;
    }

    .top-list-item:hover {
        background: #f1f5f9;
        transform: translateY(-1px);
    }

    .top-list-thumb {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        overflow: hidden;
        flex-shrink: 0;
    }

    .top-list-thumb img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .top-list-meta {
        flex: 1;
        min-width: 0;
    }

    .top-list-name {
        font-size: 13px;
        font-weight: 600;
        color: #0f172a;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .top-list-info {
        font-size: 11px;
        color: #64748b;
    }

    .top-list-btn {
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid #e2e8f0;
        background: white;
        font-size: 11px;
        cursor: pointer;
        transition:
            background 120ms ease,
            transform 120ms ease,
            box-shadow 120ms ease;
        white-space: nowrap;
    }

    .top-list-btn:hover {
        background: #0ea5a4;
        color: white;
        border-color: transparent;
        transform: translateY(-1px);
        box-shadow: 0 8px 16px rgba(14, 165, 164, 0.35);
    }

    /* ====== BUTTONS ====== */

    button {
        cursor: pointer;
    }

    .btn-primary {
        padding: 12px 16px;
        border-radius: 10px;
        border: 0;
        background: linear-gradient(135deg, #0ea5a4, #22c55e);
        color: white;
        font-weight: 600;
        box-shadow: 0 14px 30px rgba(14, 165, 164, 0.4);
        transition:
            transform 140ms ease,
            box-shadow 140ms ease,
            filter 140ms ease;
    }

    .btn-primary:hover {
        transform: translateY(-1px) scale(1.02);
        box-shadow: 0 18px 40px rgba(22, 163, 74, 0.45);
        filter: brightness(1.02);
    }

    .btn-disabled {
        padding: 12px 16px;
        border-radius: 10px;
        border: none;
        background: #94a3b8;
        color: #f1f5f9;
        cursor: not-allowed;
        filter: grayscale(20%);
    }

    .btn-ghost,
    .btn-secondary {
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background: transparent;
        transition:
            background 140ms ease,
            transform 140ms ease,
            box-shadow 140ms ease,
            border-color 140ms ease;
    }

    .btn-ghost:hover,
    .btn-secondary:hover {
        background: #f8fafc;
        transform: translateY(-1px);
        box-shadow: 0 10px 20px rgba(148, 163, 184, 0.25);
        border-color: #cbd5f5;
    }

    .btn-small-primary {
        padding: 8px 12px;
        border-radius: 8px;
        border: 0;
        background: #111827;
        color: white;
        transition:
            transform 120ms ease,
            box-shadow 120ms ease;
    }

    .btn-small-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 18px rgba(15, 23, 42, 0.35);
    }

    .btn-small-ghost {
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        background: transparent;
        transition:
            background 120ms ease,
            transform 120ms ease,
            border-color 120ms ease;
    }

    .btn-small-ghost:hover {
        background: #f8fafc;
        transform: translateY(-1px);
        border-color: #cbd5f5;
    }

    /* modal */
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(15, 23, 42, 0.45);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 60;
        animation: fadeDown 160ms ease forwards;
    }

    .modal {
        background: white;
        width: min(920px, 96%);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 22px 60px rgba(15, 23, 42, 0.4);
        animation: modalIn 220ms ease forwards;
    }

    /* ====== PAGINATION ====== */

    .pagination {
        padding: 4px 24px 28px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 14px;
    }

    .pagination-btn {
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid #e2e8f0;
        background: white;
        font-size: 13px;
    }

    .pagination-btn:disabled {
        opacity: 0.4;
        cursor: default;
    }

    .pagination-pages {
        display: flex;
        align-items: center;
        gap: 4px;
        flex-wrap: wrap;
        justify-content: center;
    }

    .page-dot {
        min-width: 32px;
        height: 32px;
        border-radius: 999px;
        border: 1px solid #e2e8f0;
        background: white;
        font-size: 13px;
    }

    .page-dot.active {
        background: #0ea5a4;
        border-color: transparent;
        color: white;
        font-weight: 600;
    }

    .page-ellipsis {
        padding: 0 4px;
        font-size: 14px;
        color: #94a3b8;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 18px;
        }
        .hero-left {
            max-width: 100%;
        }
        .card img {
            height: 140px;
        }
        .controls {
            flex-wrap: wrap;
        }
    }
</style>