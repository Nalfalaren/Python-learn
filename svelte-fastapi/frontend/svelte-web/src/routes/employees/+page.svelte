<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import styles from "$lib/styles/header/employees.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
  import { jwtDecode } from "jwt-decode"; /** Product type */
  import { authStore } from "$lib/stores/AuthStore";

  interface Employee {
    id: string;
    employee_name: string;
    role: string;
    email: string;
    is_active: string;
    created_at: string;
  }

  // === Reactive state ===
  let employees: Employee[] = $state([]);
  let loading = $state(false);
  let message = $state("");
  let totalRecords = $state(0);

  // pagination states
  let pageSize = 10;
  let nextCursor: string | null = null;
  let currentCursor: string | null = null;
  let cursorStack: (string | null)[] = []; // keep history for Previous
  let loadedCount = $state(0);

  // search
  let searchId = $state("");
  let searchName = $state("");
  let searchRole = $state("");

  // === Helper ===
  function buildUrl(cursor: string | null = null) {
    const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/employees`);
    url.searchParams.set("limit", String(pageSize));
    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_employee", searchName);
    if (searchRole) url.searchParams.set("role", searchRole);
    if (cursor) url.searchParams.set("next_cursor", cursor);
    return url;
  }

  async function fetchEmployees(cursor: string | null = null) {
    loading = true;
    const token = localStorage.getItem("admin_access_token");
    try {
      const response = await fetch(buildUrl(cursor), {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch employees");

      const res = await response.json();
      console.log(res);
      employees = res.search_result || [];
      totalRecords = res.total_employee || 0;
      nextCursor = res.next_cursor || null;
      currentCursor = cursor; // record which cursor we used
      loadedCount = (cursorStack.length + 1) * pageSize;
    } catch (error) {
      console.error(error);
      message = "Failed to load employees";
    } finally {
      loading = false;
    }
  }

  function handleNext() {
    if (!nextCursor) return;
    // Save current cursor before moving forward
    cursorStack.push(currentCursor);
    fetchEmployees(nextCursor);
  }

  function handlePrev() {
    if (cursorStack.length === 0) return; // Already first page
    const prevCursor = cursorStack.pop() ?? null;
    fetchEmployees(prevCursor);
  }

  function handleSearch() {
    // Reset pagination when search changes
    cursorStack = [];
    currentCursor = null;
    nextCursor = null;
    fetchEmployees(null);
  }

  async function handleDelete(id: string) {
    const token = localStorage.getItem("admin_access_token");
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/employee/${id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (response.ok) {
      message = "Employee deleted";
      await fetchEmployees(currentCursor); // reload current page
    } else {
      message = "Delete failed";
    }
  }

  async function handleLogout() {
    try {
      const token = localStorage.getItem("admin_access_token");
      const decoded = token ? jwtDecode<{ id: string }>(token) : null;
      const currentUserId = decoded?.id;
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/logout`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ id: currentUserId }),
        },
      );

      if (!res.ok) {
        console.error("Logout API failed:", res.status);
      }
    } catch (err) {
      console.error("Logout request error:", err);
    } finally {
      localStorage.removeItem("admin_access_token");
      localStorage.removeItem("refreshToken");
      goto("/employees/login");
    }
  }

  onMount(() => {
    if (!$authStore.isAuthenticated) {
      goto("/employees/login");
    }
    fetchEmployees(null);
  });
</script>

<!-- === UI === -->
<div>
  <div class={styles.headerContainer}>
    <div class={styles.headerContent}>
      <div><h1 style="font-family: system-ui, sans-serif;">Employees</h1></div>
      <div>
        {#if $authStore.role === "ADMIN"}
          <button onclick={() => goto("/employees/signup")}
            >+ Add Employee</button
          >
        {/if}
        <button onclick={handleLogout}>Logout</button>
      </div>
    </div>
    <TabNavigation is_admin={$authStore.role === "ADMIN"} />
  </div>

  <!-- Search -->
  <div class={styles.tableSearch}>
    <div class={styles.tableSearchInput}>
      <TextField
        name="id"
        title="ID"
        type="text"
        placeholder="Search ID"
        value={searchId}
        onValueChange={(v: string) => (searchId = v)}
      />
    </div>
    <div class={styles.tableSearchInput}>
      <TextField
        name="employee_name"
        title="Employee Name"
        type="text"
        placeholder="Search Employee Name"
        value={searchName}
        onValueChange={(v: string) => (searchName = v)}
      />
    </div>
    <div class={styles.tableSearchInput}>
      <label style="font-family: system-ui, sans-serif;">
        Search Role
        <select bind:value={searchRole} class={styles.selectInput}>
          <option value="" disabled selected hidden>Select role…</option>
          <option value="ADMIN">Admin</option>
          <option value="EMPLOYEE">Employee</option>
        </select>
      </label>
    </div>
    <button onclick={handleSearch}>Search</button>
  </div>

  <!-- Table -->
  <div class={styles.tableContainer}>
    {#if loading}
      <p>Loading...</p>
    {:else if $authStore.role !== "ADMIN" && $authStore.role !== "EMPLOYEE"}
      <div class={styles.forbiddenBox}>
        <h2>403 – Forbidden</h2>
        <p>You do not have permission to access this page.</p>
      </div>
    {:else if employees.length === 0}
      <p>No employees found.</p>
    {:else}
      <table class={styles.table}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Employee Name</th>
            <th>Role</th>
            <th>Email</th>
            <th>Status</th>
            {#if $authStore.role === "ADMIN"}<th>Action</th>{/if}
          </tr>
        </thead>
        <tbody>
          {#each employees as emp}
            <tr onclick={() => goto(`/employees/${emp.id}`)}>
              <td>{emp.id}</td>
              <td>{emp.employee_name}</td>
              <td>{emp.role}</td>
              <td>{emp.email}</td>
              <td>{emp.is_active === "Active" ? "Active" : "Inactive"}</td>
              {#if $authStore.role === "ADMIN"}
                <td>
                  <button
                    onclick={(e) => {
                      e.stopPropagation();
                      goto(`/employees/update/${emp.id}`);
                    }}>Edit</button
                  >
                  <button
                    onclick={(e) => {
                      e.stopPropagation();
                      handleDelete(emp.id);
                    }}>Delete</button
                  >
                </td>
              {/if}
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
