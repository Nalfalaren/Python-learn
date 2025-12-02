<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/update-employee/update.module.css";
  import { env } from "$env/dynamic/public";
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
  // Fetch employee
  onMount(async () => {
    const token = localStorage.getItem("accessToken");
    const res = await fetch(`${env.PUBLIC_API_URL}/employee/${employeeId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      employee = await res.json();
      active_status = employee.is_active === "Active";
    } else {
      alert("❌ Failed to load employee data");
    }
  });

  // Update employee
  async function handleUpdate() {
    const token = localStorage.getItem("accessToken");
    const res = await fetch(`${env.PUBLIC_API_URL}/employee/${employeeId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(employee),
    });

    if (res.ok) {
      alert("✅ Employee updated successfully!");
      goto("/employees");
    } else {
      const err = await res.json().catch(() => ({}));
      alert(`❌ Error: ${err.detail || "Update failed"}`);
    }
  }

  onMount(() => {
    if (!authStore.isAuthenticated) goto("/employees/login");
  });
</script>

<div class={styles.wrapper}>
  <div class={styles.card}>
    <h2>✏️ Update Employee</h2>
    <p class={styles.subtitle}>Edit employee details and save changes.</p>

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
      <select bind:value={employee.role} class={styles.input}>
        <option value="admin">Admin</option>
        <option value="leader">Leader</option>
        <option value="EMPLOYEE">Employee</option>
      </select>
    </div>

    <div class={styles.formGroup}>
      <label class={styles.label}>Email</label>
      <input
        type="email"
        bind:value={employee.email}
        class={styles.input}
        placeholder="employee@example.com"
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
