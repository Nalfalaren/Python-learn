<script lang="ts">
  import { onMount } from "svelte";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import styles from "$lib/styles/product/Product.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";

  interface Product {
    id: string;
    product_name: string;
    category: string;
    price: number;
    created_at: string;
    is_active: boolean;
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

  // === Helper ===
  function buildUrl(cursor: string | null) {
    const url = new URL(`${env.PUBLIC_API_URL}/products`);
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
    const res = await fetch(`${env.PUBLIC_API_URL}/product/${id}`, {
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

  function handleLogout() {
    localStorage.removeItem("accessToken");
    goto("/login");
  }

  onMount(() => {
    fetchProducts(null);
  });
</script>

<div class={styles.wrapper}>
  <div class={styles.headerContainer}>
    <div class={styles.headerContent}>
      <h1>🛍️ Products</h1>
      <div>
        <button on:click={() => goto("/products/add")}>+ Add Product</button>
        <button on:click={handleLogout}>Logout</button>
      </div>
    </div>
    <TabNavigation />
  </div>

  <!-- Search -->
  <div class={styles.tableSearch}>
    <div class={styles.tableSearchInput}>
      <TextField
        title="ID"
        type="text"
        placeholder="Search ID"
        value={searchId}
        onValueChange={(v: string) => (searchId = v)}
      />
    </div>
    <div class={styles.tableSearchInput}>
      <TextField
        title="Product Name"
        type="text"
        placeholder="Search Product Name"
        value={searchName}
        onValueChange={(v: string) => (searchName = v)}
      />
    </div>
    <button on:click={handleSearch}>Search</button>
  </div>

  <!-- Table -->
  <div class={styles.tableContainer}>
    {#if loading}
      <p>Loading products...</p>
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
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {#each products as p}
            <tr on:click={() => goto(`/products/${p.id}`)}>
              <td>{p.id}</td>
              <td>{p.product_name}</td>
              <td>{p.category}</td>
              <td>{p.price.toFixed(2)}</td>
              <td>{p.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button on:click={() => goto(`/products/${p.id}/edit`)}>Edit</button>
                <button on:click={() => handleDelete(p.id)}>Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

      <!-- Pagination -->
      <div class={styles.paginationControls}>
        <button on:click={handlePrev} disabled={cursorStack.length === 0}>Previous</button>
        <span>Page {cursorStack.length + 1}</span>
        <button on:click={handleNext} disabled={!nextCursor}>Next</button>
      </div>
    {/if}
  </div>
</div>
