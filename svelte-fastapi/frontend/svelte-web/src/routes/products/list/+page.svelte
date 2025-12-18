<script lang="ts">
    import { onMount } from "svelte";
    import ProductDetailModal from "../../../components/modal/ProductDetailModal.svelte";
    import { goto } from "$app/navigation";
    import { clientApi } from "../../../hooks/apiFetch";

    type Product = {
        id?: string;
        product_name: string;
        category: string;
        price: number;
        is_active: boolean;
        created_at?: string;
        updated_at?: string;
        img?: string;
        rating?: number;
        stock?: number;
    };

    let drones = $state<Product[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    let limit = $state(6);
    let total = $state(0);
    let currentCursor = $state<string | null>(null);
    let nextCursor = $state<string | null>(null);
    let cursorStack = $state<(string | null)[]>([]);
    let currentPage = $state(1);

    let search = $state("");
    let selected = $state<Product | null>(null);
    let showModal = $state(false);

    let totalPages = $derived(Math.max(1, Math.ceil(total / limit)));
    let hasPrev = $derived(currentPage > 1);
    let hasNext = $derived(nextCursor !== null && currentPage < totalPages);

    const buildUrl = (cursor: string | null = null) => {
        const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/products`);
        url.searchParams.set("limit", String(limit));
        if (search) url.searchParams.set("search_product", search);
        if (cursor) url.searchParams.set("next_cursor", cursor);

        const newUrl = `?${url.searchParams.toString()}`;

        goto(newUrl, { replaceState: true, noScroll: true });
        return url.toString();
    };

    const fetchProducts = async (cursor: string | null = null) => {
        loading = true;
        try {
            const res = await clientApi(buildUrl(cursor));
            let data = await res.json();

            drones = (data.search_result || []).map(
                (p: Product, index: number) => ({
                    ...p,
                    img: `https://picsum.photos/seed/drone${index + 1}/600/400`,
                    rating: p.rating || "N/A",
                    stock: p.stock || 0,
                }),
            );
            total = data.total_product || data.total || 0;
            nextCursor = data.next_cursor || null;
            currentCursor = cursor;
        } catch (e) {
            error = "Không thể tải danh sách drone";
        } finally {
            loading = false;
        }
    };

    const handleNext = () => {
        if (!hasNext) return;
        cursorStack = [...cursorStack, currentCursor];
        currentPage++;
        fetchProducts(nextCursor);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const handlePrev = () => {
        if (!hasPrev) return;
        currentPage--;
        const prevCursor = cursorStack[cursorStack.length - 1];
        cursorStack = cursorStack.slice(0, -1);
        fetchProducts(prevCursor);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const handleSearch = () => {
        // Reset pagination when searching
        cursorStack = [];
        currentPage = 1;
        currentCursor = null;
        nextCursor = null;
        fetchProducts(null);
    };

    const buyNow = (item: Product) => {
        if (item.id) window.location.href = `/products/details/${item.id}`;
    };

    const openDetail = (item: Product) => {
        selected = item;
        showModal = true;
    };

    onMount(() => fetchProducts(null));
</script>

<div class="container">
    <div class="header">
        <div class="header-content">
            <h1>
                <span class="icon">🚁</span>
                Explore Drones
            </h1>
            <p class="subtitle">
                Search and choose the right drone for your needs
            </p>
        </div>
    </div>

    <div class="search-section">
        <div class="search-wrapper">
            <svg
                class="search-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
            >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
            </svg>
            <input
                bind:value={search}
                placeholder="Search drones by name or model..."
            />
            {#if search}
                <button
                    class="search-btn"
                    onclick={() => {
                        cursorStack = [];
                        currentPage = 1;
                        currentCursor = null;
                        nextCursor = null;
                        buildUrl();
                        fetchProducts(null);
                    }}>Search</button
                >
            {/if}
        </div>
        <div class="results-info">
            {#if !loading && !error}
                <p>Found <strong>{total}</strong> products</p>
            {/if}
        </div>
    </div>

    {#if loading}
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading products...</p>
        </div>
    {:else if error}
        <div class="error-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <p>{error}</p>
            <button class="retry-btn" onclick={() => handleSearch()}
                >Retry</button
            >
        </div>
    {:else if drones.length === 0}
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
            </svg>
            <p>No products found</p>
        </div>
    {:else}
        <div class="grid">
            {#each drones as item, i}
                <div class="card" style="animation-delay: {i * 0.05}s">
                    <div
                        class="card-image-wrapper"
                        onclick={() => openDetail(item)}
                    >
                        <img
                            src={item.img || "/placeholder.png"}
                            alt={item.product_name}
                        />
                        <div class="card-badge">
                            {#if item.stock === 0}
                                <span class="badge sold-out">OUT OF STOCK</span>
                            {:else if item.stock && item.stock < 5}
                                <span class="badge low-stock">Low Stock</span>
                            {:else if item.stock && item.stock > 10}
                                <span class="badge in-stock">In Stock</span>
                            {/if}
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="card-category">{item.category}</div>
                        <h2>{item.product_name}</h2>

                        <div class="card-meta">
                            <div class="rating">
                                <span class="stars">
                                    {#each Array(5) as _, i}
                                        <svg
                                            viewBox="0 0 24 24"
                                            class:filled={i <
                                                Math.floor(item.rating || 0)}
                                        >
                                            <path
                                                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                            />
                                        </svg>
                                    {/each}
                                </span>
                                <span class="rating-text"
                                    >{item.rating || 0}</span
                                >
                            </div>
                            <div class="stock-info">
                                <svg
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                >
                                    <rect x="1" y="3" width="15" height="13" />
                                    <path d="M16 8h5l3 3v5h-8V8z" />
                                    <circle cx="5.5" cy="18.5" r="2.5" />
                                    <circle cx="18.5" cy="18.5" r="2.5" />
                                </svg>
                                <span>{item.stock || 0} units</span>
                            </div>
                        </div>

                        <div class="card-footer">
                            <div class="price">
                                <span class="price-label">Price</span>
                                <span class="price-value"
                                    >{item.price.toLocaleString()}$</span
                                >
                            </div>
                            <button
                                class="btn-buy"
                                onclick={() => buyNow(item)}
                                disabled={item.stock === 0}
                            >
                                Buy Now
                                <svg
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                >
                                    <path d="M5 12h14M12 5l7 7-7 7" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        <div class="pagination">
            <button class="page-btn" onclick={handlePrev} disabled={!hasPrev}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M15 18l-6-6 6-6" />
                </svg>
                Previous
            </button>

            <div class="page-info">
                <span class="page-current">Page {currentPage}</span>
                <span class="page-separator">/</span>
                <span class="page-total">{totalPages}</span>
            </div>

            <button class="page-btn" onclick={handleNext} disabled={!hasNext}>
                Next
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M9 18l6-6-6-6" />
                </svg>
            </button>
        </div>
    {/if}
</div>

{#if showModal && selected}
    <ProductDetailModal item={selected} on:close={() => (showModal = false)} />
{/if}

<style>
    * {
        box-sizing: border-box;
    }

    .container {
        width: 80%;
        margin: 0 auto;
        padding: 20px;
    }

    .header {
        background: #0c59b6;
        border-radius: 24px;
        padding: 48px 32px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }

    .header::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(
            circle,
            rgba(255, 255, 255, 0.1) 0%,
            transparent 70%
        );
        border-radius: 50%;
    }

    .header-content {
        position: relative;
        z-index: 1;
        text-align: center;
    }

    .header h1 {
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin: 0 0 12px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
    }

    .icon {
        font-size: 48px;
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%,
        100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    .subtitle {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
    }

    .search-section {
        margin-bottom: 32px;
    }

    .search-wrapper {
        position: relative;
        max-width: 600px;
        margin: 0 auto 16px;
    }

    .search-icon {
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        width: 20px;
        height: 20px;
        color: #94a3b8;
        stroke-width: 2;
    }

    input {
        width: 100%;
        padding: 16px 56px 16px 52px;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        background: white;
        font-size: 16px;
        outline: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    input:focus {
        border-color: #667eea;
        box-shadow: 0 8px 16px -4px rgba(102, 126, 234, 0.25);
        transform: translateY(-2px);
    }

    .search-btn {
        position: absolute;
        right: 16px;
        top: 50%;
        transform: translateY(-50%);
        border: none;
        border-radius: 5px;
        padding: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #0c59b6;
        color: white;
        transition: all 0.2s;
    }

    .results-info {
        text-align: center;
        color: #64748b;
        font-size: 14px;
    }

    .results-info strong {
        color: #667eea;
        font-weight: 600;
    }

    .loading-state,
    .error-state,
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px;
        text-align: center;
    }

    .spinner {
        width: 48px;
        height: 48px;
        border: 4px solid #e2e8f0;
        border-top-color: #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .loading-state p,
    .error-state p,
    .empty-state p {
        color: #64748b;
        font-size: 16px;
        margin: 8px 0 0 0;
    }

    .error-state svg,
    .empty-state svg {
        width: 64px;
        height: 64px;
        color: #94a3b8;
        stroke-width: 1.5;
        margin-bottom: 16px;
    }

    .retry-btn {
        margin-top: 16px;
        padding: 10px 24px;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .retry-btn:hover {
        background: #5568d3;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 28px;
        margin-bottom: 48px;
    }

    .card {
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.5s ease-out backwards;
        border: 1px solid #f1f5f9;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }

    .card-image-wrapper {
        position: relative;
        width: 100%;
        height: 220px;
        overflow: hidden;
        cursor: pointer;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }

    .card-image-wrapper img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }

    .card:hover .card-image-wrapper img {
        transform: scale(1.1);
    }

    .card-badge {
        position: absolute;
        top: 12px;
        right: 12px;
    }

    .badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        backdrop-filter: blur(8px);
    }

    .badge.low-stock {
        background: rgba(239, 68, 68, 0.9);
        color: white;
    }

    .badge.in-stock {
        background: rgba(34, 197, 94, 0.9);
        color: white;
    }

    .card-body {
        padding: 20px;
    }

    .card-category {
        color: #0c59b6;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .card h2 {
        font-size: 20px;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 16px 0;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .card-meta {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid #f1f5f9;
    }

    .rating {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .stars {
        display: flex;
        gap: 2px;
    }

    .stars svg {
        width: 14px;
        height: 14px;
        fill: #cbd5e1;
        stroke: none;
    }

    .stars svg.filled {
        fill: #fbbf24;
    }

    .rating-text {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
    }

    .stock-info {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: #64748b;
    }

    .stock-info svg {
        width: 14px;
        height: 14px;
        stroke-width: 2;
    }

    .card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }

    .price {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .price-label {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
    }

    .price-value {
        font-size: 22px;
        font-weight: 800;
        background: #0c59b6;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .btn-buy {
        padding: 12px 20px;
        background: #0c59b6;
        color: white;
        font-weight: 600;
        font-size: 14px;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }

    .btn-buy svg {
        width: 16px;
        height: 16px;
        stroke-width: 2.5;
        transition: transform 0.3s ease;
    }

    .btn-buy:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    .btn-buy:hover svg {
        transform: translateX(4px);
    }

    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        padding: 20px 0;
    }

    .page-btn {
        padding: 10px 18px;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        background: white;
        color: #475569;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .page-btn svg {
        width: 16px;
        height: 16px;
        stroke-width: 2.5;
    }

    .page-btn:disabled {
        cursor: not-allowed;
        opacity: 0.4;
    }

    .page-btn:hover:not(:disabled) {
        background: #667eea;
        color: white;
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .page-info {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-weight: 600;
    }

    .page-current {
        color: #667eea;
        font-size: 16px;
    }

    .page-separator {
        color: #cbd5e1;
    }

    .page-total {
        color: #64748b;
        font-size: 14px;
    }

    .page-dots {
        color: #94a3b8;
        font-weight: 600;
        padding: 0 4px;
    }

    @media (max-width: 768px) {
        .header h1 {
            font-size: 32px;
        }

        .icon {
            font-size: 36px;
        }

        .subtitle {
            font-size: 16px;
        }

        .grid {
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }

        .card-image-wrapper {
            height: 180px;
        }

        .pagination {
            gap: 8px;
        }

        .page-btn {
            padding: 8px 14px;
            font-size: 13px;
        }

        .page-info {
            font-size: 14px;
            padding: 8px 16px;
        }

        .page-current {
            font-size: 14px;
        }
    }

    @media (max-width: 480px) {
        .container {
            padding: 16px;
        }

        .header {
            padding: 32px 24px;
            border-radius: 16px;
        }

        .header h1 {
            font-size: 24px;
            flex-direction: column;
            gap: 8px;
        }

        .grid {
            grid-template-columns: 1fr;
        }

        .page-info {
            order: -1;
            width: 100%;
            justify-content: center;
        }
    }

    .badge.sold-out {
        background: #999;
        color: white;
    }

    .btn-buy:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        pointer-events: none;
    }
</style>
