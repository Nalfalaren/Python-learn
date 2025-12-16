<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import styles from "$lib/styles/header/customers.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
  import { adminAuthStore } from "$lib/stores/AuthStore";
  import { adminApi } from "../../hooks/apiFetch";
  import Header from "../../components/header/header.svelte";

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
  let employee_name = $state("");

  let searchId = $state("");
  let searchName = $state("");

  const pageSize = 10;
  let totalRecords = $state(0);

  let cursorStack: (string | null)[] = $state([]);
  let nextCursor: string | null = $state(null);
  let currentCursor: string | null = null;
  let loadedCount = $state(0);

  function buildUrl(cursor: string | null = null) {
    const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/customers`);
    url.searchParams.set("limit", String(pageSize));

    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_name", searchName);

    if (cursor) url.searchParams.set("next_cursor", cursor);

    return url;
  }

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
    employee_name = localStorage.getItem("employee_name") || ''
    fetchCustomers(null);
  });
</script>

<Header handleLogout={() => adminAuthStore.logout()} username={employee_name ?? ""}/>
<div style="display: flex; min-height: 100vh">
  <TabNavigation is_admin={$adminAuthStore.role === "ADMIN"} />
  <div style="width: 100%; background: #f5f5f5; padding: 20px">
    <div>
      <span style="font-size: 20px; color: rgb(26 59 105); font-weight: 700"
        >Customers</span
      >
    </div>

    <div class={styles.tableSearch}>
      <div class={styles.tableSearchInput}>
        <TextField
          name="id"
          title="ID"
          placeholder="Search ID"
          value={searchId}
          onValueChange={(v) => (searchId = v)}
        />
      </div>
      <div class={styles.tableSearchInput}>
        <TextField
          name="customer_name"
          title="Customer Name"
          placeholder="Search Name"
          value={searchName}
          onValueChange={(v) => (searchName = v)}
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
          onclick={() => goto("/employees/signup")}>+ Add Customer</button
        >
      {/if}
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
</div>
