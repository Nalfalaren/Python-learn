<script lang="ts">
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import styles from "$lib/styles/header/employees.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";

  interface Employee {
    id: string;
    employee_name: string;
    role: string;
    email: string;
    is_active: boolean;
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

  // search
  let searchId = $state("");
  let searchName = $state("");

  // === Helper ===
  function buildUrl(cursor: string | null = null) {
    const url = new URL(`${env.PUBLIC_API_URL}/employees`);
    url.searchParams.set("limit", String(pageSize));
    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_employee", searchName);
    if (cursor) url.searchParams.set("next_cursor", cursor);
    return url;
  }

  async function fetchEmployees(cursor: string | null = null) {
    loading = true;
    const token = localStorage.getItem("accessToken");
    try {
      const response = await fetch(buildUrl(cursor), {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch employees");

      const res = await response.json();
      employees = res.search_result || [];
      totalRecords = res.total_employee || 0;
      nextCursor = res.next_cursor || null;
      currentCursor = cursor; // record which cursor we used
      console.log("✅ Employees fetched:", { cursor, nextCursor });
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
    const token = localStorage.getItem("accessToken");
    const response = await fetch(`${env.PUBLIC_API_URL}/employee/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      message = "Employee deleted";
      await fetchEmployees(currentCursor); // reload current page
    } else {
      message = "Delete failed";
    }
  }

  function handleLogout() {
    localStorage.removeItem("accessToken");
    goto("/login");
  }

  onMount(() => {
    fetchEmployees(null);
  });
</script>


<!-- === UI === -->
<div>
  <div class={styles.headerContainer}>
    <div class={styles.headerContent}>
      <div><h1>Employees</h1></div>
      <div>
        <button onclick={() => goto("/employee/sign-up")}>+ Add Employee</button
        >
        <button onclick={handleLogout}>Logout</button>
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
        title="Employee Name"
        type="text"
        placeholder="Search Employee Name"
        value={searchName}
        onValueChange={(v: string) => (searchName = v)}
      />
    </div>
    <button onclick={handleSearch}>Search</button>
  </div>

  <!-- Table -->
  <div class={styles.tableContainer}>
    {#if loading}
      <p>Loading...</p>
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
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {#each employees as emp}
            <tr onclick={() => goto(`/employee/${emp.id}`)}>
              <td>{emp.id}</td>
              <td>{emp.employee_name}</td>
              <td>{emp.role}</td>
              <td>{emp.email}</td>
              <td>{emp.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button onclick={() => goto(`/employee/update/${emp.id}`)}
                  >Edit</button
                >
                <button onclick={() => handleDelete(emp.id)}>Delete</button>
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
        <button onclick={handleNext} disabled={!nextCursor}> Next </button>
      </div>
    {/if}
  </div>
</div>
