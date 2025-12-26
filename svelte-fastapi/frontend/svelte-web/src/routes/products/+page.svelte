<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import styles from "$lib/styles/product/product.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
  import { jwtDecode } from "jwt-decode";
  import { adminAuthStore } from "$lib/stores/AuthAdmin";
  import { adminApi } from "../../hooks/apiFetch";
  import MessageModal from "../../components/modal-success/MessageModal.svelte";
  import Header from "../../components/header/header.svelte";
  import ModalConfirm from "../../components/modal-confirm/ModalConfirm.svelte";

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
  let employee_name = $state("");

  let searchId = $state("");
  let searchName = $state("");

  let nextCursor: string | null = $state(null);
  let currentCursor: string | null = $state(null);
  let cursorStack: (string | null)[] = $state([]);
  let loadedCount = $state(0);
  let totalRecords = $state(0);
  let pageSize = 10;

  let showModal = $state(false);
  let isDeleteModalOpen = $state(false);
  let deletingItemId: string | null = $state(null);
  let isDeleteItem = $state(false);

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

  async function handleDelete() {
    if (!deletingItemId) return;
    try {
      const res = await adminApi(
        `${import.meta.env.VITE_API_BASE_URL}/admin/products/${deletingItemId}`,
        { method: "DELETE" },
      );

      if (res.ok) {
        showMessage("✅ Product deleted successfully!");
        isDeleteItem = true;
        fetchProducts(currentCursor);
      } else {
        const error = await res.json();
        showMessage(error.detail || "❌ Failed to delete product.");
      }
    } catch (error) {
      console.log(error);
      message = "Unable to delete Product.";
      isDeleteItem = true;
    } finally {
      isDeleteModalOpen = false;
      deletingItemId = null;
    }
  }

  function openDeleteModal(id: string) {
    deletingItemId = id;
    isDeleteModalOpen = true;
  }

  function onCloseModal() {
    isDeleteModalOpen = false;
    isDeleteItem = false;
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
      localStorage.removeItem("admin_refresh_token");
      localStorage.removeItem("employee_name");
      goto("/employees/login");
    }
  }

  onMount(() => {
    fetchProducts(null);
    employee_name = localStorage.getItem("employee_name") || '';
  });
</script>

<!-- === UI === -->
<Header {handleLogout} username={employee_name || ""} />
<div style="display: flex; min-height: 100vh">
  <TabNavigation is_admin={$adminAuthStore.role === "ADMIN"} />
  <div style="width: 100%; background: #f5f5f5; padding: 20px">
    <div>
      <span style="font-size: 20px; color: rgb(26 59 105); font-weight: 700"
        >Products</span
      >
    </div>
    <!-- Search -->
    <div class={styles.tableSearch}>
      <div class={styles.tableSearchInput}>
        <TextField
          name="id"
          title="ID"
          placeholder="Search ID"
          value={searchId}
          onValueChange={(v: string) => (searchId = v)}
        />
      </div>
      <div class={styles.tableSearchInput}>
        <TextField
          name="productName"
          title="Product Name"
          placeholder="Search Product Name"
          value={searchName}
          onValueChange={(v: string) => (searchName = v)}
        />
      </div>
      <button
        onclick={handleSearch}
        style="background-color: white; border: 1px solid #d9d9d9; color: rgba(0, 0, 0, 0.88)"
        >Search</button
      >
      {#if $adminAuthStore.role === "ADMIN"}
        <button
          style="background-color: white; border: 1px solid #d9d9d9; color: rgba(0, 0, 0, 0.88)"
          onclick={() => goto("/products/add")}>+ Add Products</button
        >
      {/if}
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
              <th class={styles.text_left}>ID</th>
              <th class={styles.text_left}>Product Name</th>
              <th class={styles.text_left}>Category</th>
              <th>Price ($)</th>
              <th>Rating</th>
              <th>Stock</th>
              <th class={styles.text_left}>Action</th>
            </tr>
          </thead>
          <tbody>
            {#each products as product}
              <tr onclick={() => goto(`/products/${product.id}`)}>
                <td class={styles.text_left}>{product.id}</td>
                <td class={styles.text_left}>{product.product_name}</td>
                <td class={styles.text_left}>{product.category}</td>
                <td>{product.price.toFixed(2)}</td>
                <td>{product.rating}</td>
                <td>{product.stock || 0}</td>
                <td class={styles.text_left}>
                  <button
                    onclick={(event) => {
                      event.stopPropagation();
                      goto(`/products/${product.id}/edit`);
                    }}
                  >
                    Edit
                  </button>

                  <button
                    onclick={(e) => {
                      e.stopPropagation();
                      openDeleteModal(product.id);
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
  </div>
  <ModalConfirm
    show={isDeleteModalOpen}
    message="Are you sure you want to delete this order item?"
    onConfirm={handleDelete}
    onCancel={() => (isDeleteModalOpen = false)}
  />
  <MessageModal show={isDeleteItem} {message} onClose={onCloseModal} />
</div>

<MessageModal show={showModal} {message} onClose={() => (showModal = false)} />
