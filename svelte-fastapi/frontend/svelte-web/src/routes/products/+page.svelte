<script lang="ts">
  import { onMount } from "svelte";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import styles from "$lib/styles/product/Product.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
  import { jwtDecode } from "jwt-decode";
  import { authStore } from "../../lib/stores/AuthStore";
  interface Product {
    id: string;
    product_name: string;
    category: string;
    price: number;
    created_at: string;
    image_url?: string;
  }

  // === State ===
  let products: Product[] = $state([]);
  let loading = $state(false);
  let message = $state("");
  let searchId = $state("");
  let searchName = $state("");

  // Pagination cursor
  let nextCursor: string | null = $state(null);
  let currentCursor: string | null = $state(null);
  let cursorStack: (string | null)[] = $state([]);
  let loadedCount = $state(0);
  let totalRecords = $state(0);
  let pageSize = 10;

  // === Helper ===
  function buildUrl(cursor: string | null) {
    const url = new URL(`${env.PUBLIC_API_URL}/admin/products`);
    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_product", searchName);
    if (cursor) url.searchParams.set("next_cursor", cursor);
    return url;
  }

  async function fetchProducts(cursor: string | null = null) {
    loading = true;
    const token = localStorage.getItem("accessToken");
    const response = await fetch(buildUrl(cursor), {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      products = data.search_result || [];
      nextCursor = data.next_cursor || null;
      currentCursor = cursor;
      loadedCount = (cursorStack.length + 1) * pageSize;
      totalRecords = data.total_product || 0;
      loading = false;
    } else {
      loading = false;
      message = "❌ Failed to load products.";
    }
  }

  function handleSearch() {
    cursorStack = [];
    currentCursor = null;
    nextCursor = null;
    fetchProducts(null);
  }

  function handleNext() {
    if (!nextCursor) return;
    cursorStack.push(currentCursor);
    fetchProducts(nextCursor);
  }

  function handlePrev() {
    if (cursorStack.length === 0) return;
    const prevCursor = cursorStack.pop() ?? null;
    fetchProducts(prevCursor);
  }

  async function handleDelete(id: string) {
    if (!confirm("Are you sure you want to delete this product?")) return;
    const token = localStorage.getItem("accessToken");
    const res = await fetch(`${env.PUBLIC_API_URL}/admin/products/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      message = "✅ Product deleted!";
      fetchProducts(currentCursor);
    } else {
      message = "❌ Failed to delete product.";
    }
  }

  async function handleLogout() {
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
      goto("/employee/login");
    }
  }

  onMount(() => {
    fetchProducts(null);
  });
</script>

<!-- HEADER -->

<div class={styles.headerContainer}>
  <div class={styles.headerContent}>
    <h1 style="font-family: system-ui, sans-serif;">Products</h1>
    <div>
      {#if $authStore.role === "admin"}
        <button onclick={() => goto("/products/add")}>+ Add Product</button>
      {/if}
      <button onclick={handleLogout}>Logout</button>
    </div>
  </div>
  <TabNavigation is_admin={$authStore.role === "admin"} />
</div>

<!-- SEARCH -->

<div class={styles.tableSearch}>
  <TextField
    name="id"
    title="ID"
    placeholder="Search ID"
    value={searchId}
    onValueChange={(v: string) => (searchId = v)}
  />

  <TextField
    name="productName"
    title="Product Name"
    placeholder="Search Product Name"
    value={searchName}
    onValueChange={(v: string) => (searchName = v)}
  />

  <button onclick={handleSearch}>Search</button>
</div>

<!-- TABLE -->

<div class={styles.tableContainer}>
  {#if loading}
    <p>Loading products...</p>
  {:else if $authStore.role !== "admin"}
    <div class={styles.forbiddenBox}>
      <h2>403 – Forbidden</h2>
      <p>You do not have permission to access this page.</p>
    </div>
  {:else if products.length === 0}
    <p>No products found.</p>
  {:else}
    <table class={styles.table}>
      <thead>
        <tr>
          <th>ID</th>
          <th>Product Name</th>
          <th>Category</th>
          <th>Price ($)</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {#each products as p}
          <tr onclick={() => goto(`/products/${p.id}`)}>
            <td>{p.id}</td>
            <td>{p.product_name}</td>
            <td>{p.category}</td>
            <td>{p.price.toFixed(2)}</td>
            <td>
              <button
                onclick={(event) => {
                  event.stopPropagation();
                  goto(`/products/${p.id}/edit`);
                }}
              >
                Edit
              </button>

              <button
                onclick={(event) => {
                  event.stopPropagation();
                  handleDelete(p.id);
                }}
              >
                Delete
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>

    <!-- Pagination -->
    <div class={styles.paginationControls}>
      <button onclick={handlePrev} disabled={cursorStack.length === 0}>
        Previous
      </button>
      <button
        onclick={handleNext}
        disabled={!nextCursor || loadedCount >= totalRecords}
      >
        Next
      </button>
    </div>
  {/if}
</div>
