<script lang="ts">
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
  import styles from "$lib/styles/header/employees.module.css";
  import TextField from "../../components/input/TextField.svelte";
  import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";

  // === Types ===
  interface Employee {
    id: string;
    employee_name: string;
    role: string;
    email: string;
    is_active: boolean;
    created_at: string;
  }

  // === States ===
  let employees: Employee[] = $state([]);
  let loading = $state(false);
  let message = $state("");
  let totalRecords = $state(0);
  let currentPage = $state(1);
  let pageSize = $state(20); // 👈 fixed 20 per page
  let totalPages = $derived(Math.ceil(totalRecords / pageSize));

  // Search form
  let searchId = $state("");
  let searchName = $state("");

  // === Helper ===
  function buildUrl() {
    const url = new URL(`${env.PUBLIC_API_URL}/employees`);
    url.searchParams.set("page", String(currentPage));
    url.searchParams.set("page_size", String(pageSize));
    if (searchId) url.searchParams.set("search_id", searchId);
    if (searchName) url.searchParams.set("search_employee", searchName);
    return url;
  }

  async function fetchEmployees() {
    loading = true;
    const token = localStorage.getItem("accessToken");
    const response = await fetch(buildUrl(), {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const res = await response.json();
      employees = res.search_result || [];
      totalRecords = res.total_employee || res.count || 0;
      loading = false;
    } else {
      loading = false;
      message = "Failed to load employees";
    }
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
      await fetchEmployees();
    } else {
      message = "Delete failed";
    }
  }

  function handleSearch() {
    currentPage = 1;
    fetchEmployees();
  }

  function handlePageChange(newPage: number) {
    if (newPage < 1 || newPage > totalPages) return;
    currentPage = newPage;
    fetchEmployees();
  }

  function handleLogout() {
    localStorage.removeItem("accessToken");
    goto("/login");
  }

  // === On Mount ===
  $effect(() => {
    fetchEmployees();
  });
</script>

<!-- === UI === -->
<div>
  <div class={styles.headerContainer}>
    <div class={styles.headerContent}>
      <div><h1>Employees</h1></div>
      <div>
        <button onclick={() => goto("/employee/sign-up")}>+ Add Employee</button>
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
            <tr>
              <td>{emp.id}</td>
              <td>{emp.employee_name}</td>
              <td>{emp.role}</td>
              <td>{emp.email}</td>
              <td>{emp.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button onclick={() => goto(`/employee/update/${emp.id}`)}>Edit</button>
                <button onclick={() => handleDelete(emp.id)}>Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>

      <!-- Pagination -->
      <div class={styles.paginationControls}>
        <button onclick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>
          Previous
        </button>
        <span>Page {currentPage} / {totalPages || 1}</span>
        <button
          onclick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    {/if}
  </div>
</div>
