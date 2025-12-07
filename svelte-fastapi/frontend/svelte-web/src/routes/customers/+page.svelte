<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import styles from "$lib/styles/header/customers.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
  import { adminAuthStore } from "$lib/stores/AuthStore";
    import { adminApi } from "../../hooks/apiFetch";
  

  interface Customer {
    id: string;
    customer_name: string;
    phone: string;
    address: string;
    role: string;
    email: string;
    is_active: string;
    created_at: string;
  }

  let customers: Customer[] = $state([]);
  let loading = $state(false);
  let message = $state("");

  let searchId = $state("");
  let searchName = $state("");

  const pageSize = 10;
  let totalRecords = $state(0);

  // Cursor-based pagination
  let cursorStack: (string | null)[] = [];
  let nextCursor: string | null = null;
  let currentCursor: string | null = null;
  let loadedCount = $state(0);

  /** ============================
   *  Helpers
   * ============================ */
  function buildUrl(cursor: string | null = null) {
    const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/customers`);
    url.searchParams.set("limit", String(pageSize));

    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_name", searchName);

    if (cursor) url.searchParams.set("next_cursor", cursor);

    return url;
  }

  /** ============================
   *  Fetch Customers
   * ============================ */
  async function fetchCustomers(cursor: string | null = null) {
    loading = true;
    try {
      const res = await adminApi(buildUrl(cursor));

      if (!res.ok) throw new Error("Failed to fetch customers");

      const data = await res.json();

      customers = data.search_result || [];
      totalRecords = data.total_cusloyee || 0;
      nextCursor = data.next_cursor || null;

      currentCursor = cursor;
      loadedCount = customers.length + pageSize * cursorStack.length;
    } catch (err) {
      console.error(err);
      message = "Failed to load customers";
    } finally {
      loading = false;
    }
  }

  /** ============================
   *  Pagination
   * ============================ */
  function nextPage() {
    if (!nextCursor) return;
    cursorStack.push(currentCursor);
    fetchCustomers(nextCursor);
  }

  function prevPage() {
    if (!cursorStack.length) return;
    const prevCursor = cursorStack.pop() ?? null;
    fetchCustomers(prevCursor);
  }

  /** ============================
   *  Search
   * ============================ */
  function handleSearch() {
    cursorStack = [];
    currentCursor = null;
    nextCursor = null;
    fetchCustomers(null);
  }

  onMount(() => {
    if (!$adminAuthStore.isAuthenticated) {
      goto("/employees/login");
      return;
    }
    fetchCustomers(null);
  });
</script>

<div>
  <div class={styles.headerContainer}>
    <div class={styles.headerContent}>
      <div><h1 style="font-family: system-ui, sans-serif;">Customers</h1></div>
      <div>
        <button onclick={() => adminAuthStore.logout()}>Logout</button>
      </div>
    </div>
    <TabNavigation is_admin={$adminAuthStore.role === "ADMIN"} />
  </div>

  <!-- Search -->
  <div class={styles.tableSearch}>
    <div class={styles.tableSearchInput}>
      <TextField
        name="id"
        title="ID"
        placeholder="Search ID"
        value={searchId}
        onValueChange={v => (searchId = v)}
      />
    </div>

    <div class={styles.tableSearchInput}>
      <TextField
        name="customer_name"
        title="Customer Name"
        placeholder="Search Name"
        value={searchName}
        onValueChange={v => (searchName = v)}
      />
    </div>

    <button onclick={handleSearch}>Search</button>
  </div>

  <div class={styles.tableContainer}>
    {#if loading}
      <p>Loading...</p>

    {:else if $adminAuthStore.role !== "ADMIN"}
      <div class={styles.forbiddenBox}>
        <h2>403 – Forbidden</h2>
        <p>You do not have permission to access this page.</p>
      </div>

    {:else if customers.length === 0}
      <p>No customers found.</p>

    {:else}
      <table class={styles.table}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Customer Name</th>
            <th>Role</th>
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {#each customers as cus}
            <tr onclick={() => goto(`/customers/${cus.id}`)}>
              <td>{cus.id}</td>
              <td>{cus.customer_name}</td>
              <td>{cus.role}</td>
              <td>{cus.email}</td>
              <td>{cus.is_active === "Active" ? "Active" : "Inactive"}</td>
            </tr>
          {/each}
        </tbody>
      </table>

      <!-- Pagination -->
      <div class={styles.paginationControls}>
        <button onclick={prevPage} disabled={!cursorStack.length}>
          Previous
        </button>

        <button
          onclick={nextPage}
          disabled={!nextCursor || loadedCount >= totalRecords}
        >
          Next
        </button>
      </div>
    {/if}
  </div>
</div>
