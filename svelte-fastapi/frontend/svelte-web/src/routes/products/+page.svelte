<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import styles from "$lib/styles/product/product.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
  import { jwtDecode } from "jwt-decode";
  import { adminAuthStore } from "$lib/stores/AuthStore";
  import { adminApi } from "../../hooks/apiFetch";
  import MessageModal from "../../components/modal-success/MessageModal.svelte";

  interface Product {
    id: string;
    product_name: string;
    category: string;
    price: number;
    created_at: string;
    rating?: string;
    description?: string;
    stock: number;
    image_url?: string;
  }

  // === State ===
  let products: Product[] = $state([]);
  let loading = $state(false);
  let message = $state(""); 

  let searchId = $state("");
  let searchName = $state("");

  let nextCursor: string | null = $state(null);
  let currentCursor: string | null = $state(null);
  let cursorStack: (string | null)[] = $state([]);
  let loadedCount = $state(0);
  let totalRecords = $state(0);
  let pageSize = 10;

  let showModal = $state(false);

  // === Helper ===
  function showMessage(msg: string) {
    message = msg;
    showModal = true;
    setTimeout(() => (showModal = false), 2000);
  }

  function buildUrl(cursor: string | null) {
    const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/admin/products`);
    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_product", searchName);
    if (cursor) url.searchParams.set("next_cursor", cursor);
    return url;
  }

  async function fetchProducts(cursor: string | null = null) {
    loading = true;
    const response = await adminApi(buildUrl(cursor));

    if (response.ok) {
      const data = await response.json();
      products = data.search_result || [];
      nextCursor = data.next_cursor || null;
      currentCursor = cursor;
      loadedCount = (cursorStack.length + 1) * pageSize;
      totalRecords = data.total_product || 0;
    } else {
      const error = await response.json();  
      showMessage(error?.detail);
    }

    loading = false;
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

  const res = await adminApi(
    `${import.meta.env.VITE_API_BASE_URL}/admin/products/${id}`,
    { method: "DELETE" }
  );

  if (res.ok) {
    showMessage("✅ Product deleted successfully!");
    fetchProducts(currentCursor);
  } else {
    const error = await res.json();  
    showMessage(error.detail || "❌ Failed to delete product.");
  }
}


  async function handleLogout() {
    try {
      const token = localStorage.getItem("admin_access_token");
      const decoded = token ? jwtDecode<{ id: string }>(token) : null;
      const currentUserId = decoded?.id;

      await adminApi(`${import.meta.env.VITE_API_BASE_URL}/auth/logout`, {
        method: "POST",
        body: JSON.stringify({ id: currentUserId }),
      });
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      localStorage.removeItem("admin_access_token");
      localStorage.removeItem("refreshToken");
      goto("/employees/login");
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
      {#if $adminAuthStore.role === "ADMIN"}
        <button onclick={() => goto("/products/add")}>+ Add Product</button>
      {/if}
      <button onclick={handleLogout}>Logout</button>
    </div>
  </div>
  <TabNavigation is_admin={$adminAuthStore.role === "ADMIN"} />
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
  {:else if $adminAuthStore.role !== "ADMIN"}
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
          <th>Rating</th>
          <th>Stock</th>
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
            <td>{p.rating}</td>
            <td>{p.stock || 0}</td>
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

<MessageModal show={showModal} message={message} onClose={() => (showModal = false)} />
