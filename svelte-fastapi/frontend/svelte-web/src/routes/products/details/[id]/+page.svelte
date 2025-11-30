<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { env } from '$env/dynamic/public';
  import { cart, type Product } from '$lib/stores/CartStore';

  let product: Product | null = null;
  let isLoading = true;
  let error = "";
  let productId = $page.params.id;
  let quantity = 1;
  let isLoggedIn = false;

  // Subscribe to cart for count badge
  let cartCount = 0;
  cart.subscribe(() => {
    cartCount = cart.getTotalCount();
  });

  onMount(() => {
    isLoggedIn = !!localStorage.getItem("accessToken");
    fetchProduct();
  });

  async function fetchProduct() {
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
        rating: data.rating || 4 + Math.random() * 1,
        stock: data.stock || Math.floor(3 + Math.random() * 15),
      };
    } catch (e) {
      console.error(e);
      error = "Không thể tải thông tin sản phẩm.";
    } finally {
      isLoading = false;
    }
  }

  function addToCart() {
    if (!isLoggedIn) {
      alert("Please login to add items to cart");
      goto("/login");
      return;
    }

    if (!product) return;

    cart.addItem(product, quantity);
    alert(`Added ${quantity} × ${product.product_name} to cart! 🛒`);
    quantity = 1; // reset
  }

  function renderStars(rating = 0) {
    return Array(5)
      .fill(0)
      .map((_, i) => (i < Math.floor(rating) ? "★" : "☆"))
      .join("");
  }

  function increaseQuantity() {
    if (product && quantity < (product.stock ?? 99)) {
      quantity++;
    }
  }

  function decreaseQuantity() {
    if (quantity > 1) {
      quantity--;
    }
  }

  function viewCart() {
    goto("/");
    // Or if you have a dedicated cart page: goto("/cart");
  }
</script>

{#if isLoading}
  <div class="loading">Đang tải sản phẩm...</div>
{:else if error}
  <div class="error">{error}</div>
{:else if product}
  <section class="product-detail">
    <div class="top-nav">
      <a href="/" class="breadcrumb">← Marketplace</a>
      
      <button class="cart-btn" on:click={viewCart}>
        🛒 Cart
        {#if cartCount > 0}
          <span class="cart-badge">{cartCount}</span>
        {/if}
      </button>
    </div>

    <div class="detail-container">
      <div class="image-section">
        <img src={product.img} alt={product.product_name} class="main-img" />
        <!-- demo carousel -->
        <div class="carousel">
          {#each [1, 2, 3] as i}
            <img
              src={`https://picsum.photos/seed/drone${product.id}${i}/120/80`}
              alt=""
            />
          {/each}
        </div>
      </div>

      <div class="info-section">
        <h1 class="title">{product.product_name}</h1>
        <div class="meta">
          <span class="category">{product.category}</span>
          <span class="rating"
            >{renderStars(product.rating)} ({product.rating?.toFixed(1) ??
              "—"})</span
          >
          <span class="stock"
            >{product.stock ?? "—"} in stock
            {#if product.stock && product.stock < 10}
              <span class="low-stock">⚠️ Low stock</span>
            {/if}
          </span>
        </div>

        <p class="description">
          {product.description ??
            "Drone cao cấp, pin lâu, camera chất lượng, phù hợp nhiều mục đích. Thiết kế nhỏ gọn, dễ mang theo, phù hợp cho cả người mới và chuyên nghiệp."}
        </p>

        <div class="specs">
          <h3>Specifications</h3>
          <ul>
            <li><strong>Category:</strong> {product.category}</li>
            <li><strong>Status:</strong> {product.is_active ? "Available" : "Unavailable"}</li>
            <li><strong>Rating:</strong> {product.rating?.toFixed(1) ?? "N/A"} / 5.0</li>
            <li><strong>Stock:</strong> {product.stock ?? "N/A"} units</li>
          </ul>
        </div>

        <div class="buy-section">
          <div class="price-container">
            <div class="price">${product.price}</div>
            <div class="price-note">Free shipping on orders over $100</div>
          </div>

          <div class="quantity-selector">
            <label>Quantity:</label>
            <div class="quantity-controls">
              <button on:click={decreaseQuantity} class="qty-btn">−</button>
              <input
                type="number"
                bind:value={quantity}
                min="1"
                max={product.stock ?? 99}
                class="qty-input"
              />
              <button on:click={increaseQuantity} class="qty-btn">+</button>
            </div>
          </div>

          <div class="action-buttons">
            <button on:click={addToCart} class="btn-primary">
              Add to cart
            </button>
            <button class="btn-secondary" on:click={() => goto("/")}>
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Info Section -->
    <div class="additional-info">
      <div class="info-card">
        <h3>🚚 Free Shipping</h3>
        <p>On orders over $100</p>
      </div>
      <div class="info-card">
        <h3>🔒 Secure Payment</h3>
        <p>100% secure payment</p>
      </div>
      <div class="info-card">
        <h3>↩️ Easy Returns</h3>
        <p>30-day return policy</p>
      </div>
      <div class="info-card">
        <h3>💬 24/7 Support</h3>
        <p>Dedicated support team</p>
      </div>
    </div>
  </section>
{/if}

<style>
  :global(body) {
    font-family:
      Inter,
      system-ui,
      -apple-system,
      "Segoe UI",
      Roboto,
      "Helvetica Neue",
      Arial;
    background: #f8fafc;
    color: #0f172a;
    margin: 0;
  }

  .loading,
  .error {
    padding: 40px;
    font-size: 18px;
    text-align: center;
  }
  .error {
    color: #ef4444;
  }

  .top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 16px 0;
  }

  .breadcrumb {
    display: inline-block;
    font-size: 14px;
    color: #0ea5e9;
    text-decoration: none;
    transition: color 140ms ease;
  }
  .breadcrumb:hover {
    color: #0284c7;
    text-decoration: underline;
  }

  .cart-btn {
    position: relative;
    padding: 10px 16px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    background: white;
    cursor: pointer;
    transition:
      background 140ms ease,
      transform 140ms ease,
      box-shadow 140ms ease;
  }

  .cart-btn:hover {
    background: #f8fafc;
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(148, 163, 184, 0.2);
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
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.1);
  }

  .image-section {
    flex: 1;
    min-width: 280px;
  }

  .main-img {
    width: 100%;
    max-height: 500px;
    border-radius: 16px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.1);
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
    border: 2px solid transparent;
    transition:
      transform 140ms ease,
      border-color 140ms ease;
  }

  .carousel img:hover {
    transform: scale(1.05);
    border-color: #0ea5e9;
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
    color: #0f172a;
  }

  .meta {
    display: flex;
    gap: 12px;
    font-size: 14px;
    color: #64748b;
    flex-wrap: wrap;
    align-items: center;
  }

  .category {
    background: #eef2ff;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 600;
    color: #4f46e5;
  }

  .meta .rating {
    color: #facc15;
    font-weight: 600;
  }

  .low-stock {
    color: #ef4444;
    font-weight: 600;
    font-size: 12px;
  }

  .description {
    font-size: 16px;
    color: #334155;
    line-height: 1.6;
    padding: 12px 0;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
  }

  .specs {
    margin-top: 8px;
  }

  .specs h3 {
    font-size: 18px;
    margin: 0 0 12px 0;
    color: #0f172a;
  }

  .specs ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .specs li {
    padding: 6px 0;
    font-size: 14px;
    color: #475569;
  }

  .specs li strong {
    color: #0f172a;
  }

  .buy-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 2px solid #e2e8f0;
  }

  .price-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .price {
    font-size: 32px;
    font-weight: 800;
    color: #0f172a;
  }

  .price-note {
    font-size: 13px;
    color: #22c55e;
    font-weight: 600;
  }

  .quantity-selector {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .quantity-selector label {
    font-weight: 600;
    color: #0f172a;
  }

  .quantity-controls {
    display: flex;
    align-items: center;
    gap: 4px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 4px;
    background: #f8fafc;
  }

  .qty-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    background: white;
    cursor: pointer;
    font-size: 18px;
    font-weight: 600;
    transition:
      background 120ms ease,
      transform 120ms ease;
  }

  .qty-btn:hover {
    background: #0ea5e9;
    color: white;
    transform: scale(1.05);
  }

  .qty-input {
    width: 60px;
    height: 32px;
    text-align: center;
    border: none;
    background: transparent;
    font-size: 16px;
    font-weight: 600;
  }

  .qty-input::-webkit-inner-spin-button,
  .qty-input::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .btn-primary {
    flex: 1;
    min-width: 180px;
    padding: 14px 24px;
    border-radius: 12px;
    border: 0;
    background: linear-gradient(135deg, #0ea5e9, #22c55e);
    color: white;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 12px 28px rgba(14, 165, 164, 0.35);
    transition:
      transform 140ms ease,
      box-shadow 140ms ease,
      filter 140ms ease;
  }

  .btn-primary:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 18px 40px rgba(14, 165, 164, 0.45);
    filter: brightness(1.05);
  }

  .btn-secondary {
    flex: 1;
    min-width: 180px;
    padding: 14px 24px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: white;
    font-weight: 600;
    cursor: pointer;
    transition:
      background 140ms ease,
      transform 140ms ease,
      box-shadow 140ms ease;
  }

  .btn-secondary:hover {
    background: #f8fafc;
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(148, 163, 184, 0.25);
  }

  .additional-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-top: 32px;
  }

  .info-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    text-align: center;
    transition:
      transform 140ms ease,
      box-shadow 140ms ease;
  }

  .info-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
  }

  .info-card h3 {
    font-size: 16px;
    margin: 0 0 8px 0;
    color: #0f172a;
  }

  .info-card p {
    font-size: 14px;
    color: #64748b;
    margin: 0;
  }

  @media (max-width: 768px) {
    .detail-container {
      flex-direction: column;
    }
    .main-img {
      max-width: 100%;
    }
    .action-buttons {
      flex-direction: column;
    }
    .btn-primary,
    .btn-secondary {
      min-width: 100%;
    }
    .title {
      font-size: 24px;
    }
    .price {
      font-size: 24px;
    }
  }
</style>