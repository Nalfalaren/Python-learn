<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/update-employee/update.module.css";
  import { goto } from "$app/navigation";
  import { authStore } from "$lib/stores/AuthStore";

  let employeeId: string;
  let employee = {
    employee_name: "",
    role: "",
    email: "",
    is_active: "",
  };

  export let params;
  employeeId = params.id;
  let active_status = false;

  // Fetch employee data
  onMount(async () => {
    const token = localStorage.getItem("admin_access_token");
    const res = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/employee/${employeeId}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    if (res.ok) {
      employee = await res.json();
      active_status = employee.is_active === "Active";
    } else {
      alert("❌ Failed to load employee data");
    }
  });

  // Update employee data
  async function handleUpdate() {
    const token = localStorage.getItem("admin_access_token");
    const res = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/employee/${employeeId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(employee),
      },
    );

    if (res.ok) {
      alert("✅ Employee updated successfully!");
      goto("/employees");
    } else {
      const err = await res.json().catch(() => ({}));
      alert(`❌ Error: ${err.detail || "Update failed"}`);
    }
  }

  onMount(() => {
    if (!$authStore.isAuthenticated) goto("/employees/login");
  });
</script>

<div class={styles.wrapper}>
  <div class={styles.card}>
    <h2>✏️ Update Employee</h2>
    <p class={styles.subtitle}>Edit the employee details and save your changes.</p>

    <div class={styles.formGroup}>
      <label class={styles.label}>Employee Name</label>
      <input
        type="text"
        bind:value={employee.employee_name}
        class={styles.input}
        placeholder="Enter employee name"
      />
    </div>

    <div class={styles.formGroup}>
      <label class={styles.label}>Role</label>
      <select
        bind:value={employee.role}
        class={`${styles.input} ${styles.roleSelectDisable}`}
        disabled
      >
        <option value="ADMIN">Admin</option>
        <option value="EMPLOYEE">Employee</option>
      </select>
    </div>

    <div class={styles.formGroup}>
      <label class={styles.label}>Email</label>
      <input
        type="email"
        bind:value={employee.email}
        class={`${styles.input} ${styles.roleSelectDisable}`}
        placeholder="employee@example.com"
        disabled
      />
    </div>

    <div class={styles.checkboxGroup}>
      <label class={styles.checkboxLabel}>
        <input
          type="checkbox"
          bind:checked={active_status}
          class={styles.checkbox}
          disabled
        />
        Active Employee
      </label>
    </div>

    <button on:click={handleUpdate} class={styles.button}>
      💾 Save Changes
    </button>
  </div>
</div>
