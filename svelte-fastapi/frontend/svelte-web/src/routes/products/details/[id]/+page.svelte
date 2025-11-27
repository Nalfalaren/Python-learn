<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { env } from '$env/dynamic/public';

  type Product = {
    id: string;
    product_name: string;
    category: string;
    price: number;
    is_active: boolean;
    img?: string;
    rating?: number;
    stock?: number;
    description?: string;
  };

  let product: Product | null = null;
  let isLoading = true;
  let error = "";
  let productId = $page.params.id;

  onMount(async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`${env.PUBLIC_API_URL}/products/${productId}`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) throw new Error(`Failed to fetch product: ${res.status}`);
      const data = await res.json();
      product = {
        ...data,
        img: data.img || `https://picsum.photos/seed/drone${data.id}/600/400`,
      };
    } catch (e) {
      console.error(e);
      error = "Không thể tải thông tin sản phẩm.";
    } finally {
      isLoading = false;
    }
  });

  function addToCart() {
    if (product) alert(`Added ${product.product_name} to cart (demo) 👋`);
  }

  function renderStars(rating = 0) {
    return Array(5).fill(0).map((_, i) => i < Math.floor(rating) ? "★" : "☆").join("");
  }
</script>

{#if isLoading}
  <div class="loading">Đang tải sản phẩm...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if product}
  <section class="product-detail">
    <a href="/" class="breadcrumb">← Marketplace</a>

    <div class="detail-container">
      <div class="image-section">
        <img src={product.img} alt={product.product_name} class="main-img" />
        <!-- demo carousel (thêm ảnh khác nếu muốn) -->
        <div class="carousel">
          {#each [1,2,3] as i}
            <img src={`https://picsum.photos/seed/drone${product.id}${i}/120/80`} alt="" />
          {/each}
        </div>
      </div>

      <div class="info-section">
        <h1 class="title">{product.product_name}</h1>
        <div class="meta">
          <span class="category">{product.category}</span>
          <span class="rating">{renderStars(product.rating)} ({product.rating?.toFixed(1) ?? "—"})</span>
          <span class="stock">{product.stock ?? "—"} in stock</span>
        </div>

        <p class="description">{product.description ?? "Drone cao cấp, pin lâu, camera chất lượng, phù hợp nhiều mục đích."}</p>

        <div class="buy-section">
          <div class="price">${product.price}</div>
          <button on:click={addToCart} class="btn-primary">Add to cart</button>
        </div>
      </div>
    </div>
  </section>
{/if}

<style>
  :global(body) {
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    background: #f8fafc;
    color: #0f172a;
    margin: 0;
  }

  .loading, .error {
    padding: 40px;
    font-size: 18px;
    text-align: center;
  }
  .error { color: red; }

  .breadcrumb {
    display: inline-block;
    margin: 16px 0;
    font-size: 14px;
    color: #0ea5e9;
    text-decoration: none;
  }
  .breadcrumb:hover { text-decoration: underline; }

  .product-detail {
    max-width: 1080px;
    margin: 0 auto;
    padding: 24px;
  }

  .detail-container {
    display: flex;
    gap: 32px;
    flex-wrap: wrap;
    background: #fff;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 16px 40px rgba(15,23,42,0.1);
  }

  .image-section {
    flex: 1;
    min-width: 280px;
  }

  .main-img {
    width: 100%;
    border-radius: 16px;
    box-shadow: 0 12px 32px rgba(15,23,42,0.1);
    object-fit: cover;
  }

  .carousel {
    display: flex;
    gap: 8px;
    margin-top: 12px;
  }

  .carousel img {
    width: 80px;
    height: 60px;
    object-fit: cover;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 140ms ease;
  }

  .carousel img:hover {
    transform: scale(1.05);
  }

  .info-section {
    flex: 1;
    min-width: 280px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .title {
    font-size: 32px;
    margin: 0;
  }

  .meta {
    display: flex;
    gap: 12px;
    font-size: 14px;
    color: #64748b;
    flex-wrap: wrap;
  }

  .meta .rating {
    color: #facc15;
    font-weight: 600;
  }

  .description {
    font-size: 16px;
    color: #334155;
    line-height: 1.6;
  }

  .buy-section {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-top: 16px;
    flex-wrap: wrap;
  }

  .price {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
  }

  .btn-primary {
    padding: 14px 24px;
    border-radius: 12px;
    border: 0;
    background: linear-gradient(135deg, #0ea5e9, #22c55e);
    color: white;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 12px 28px rgba(14,165,164,0.35);
    transition: transform 140ms ease, box-shadow 140ms ease, filter 140ms ease;
  }

  .btn-primary:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 18px 40px rgba(14,165,164,0.45);
    filter: brightness(1.05);
  }

  @media (max-width: 768px) {
    .detail-container {
      flex-direction: column;
    }
    .main-img { max-width: 100%; }
    .buy-section { flex-direction: column; gap: 12px; }
  }
</style>
