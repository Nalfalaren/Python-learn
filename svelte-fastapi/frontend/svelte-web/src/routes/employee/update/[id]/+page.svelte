<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/update-employee/Update.module.css";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";

  let employeeId: string;
  let employee = {
    employee_name: "",
    role: "",
    email: "",
    is_active: false,
  };

  export let params;
  employeeId = params.id;

  // Fetch current employee data
  onMount(async () => {
    const token = localStorage.getItem("accessToken");
    const res = await fetch(`${env.PUBLIC_API_URL}/employee/${employeeId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      employee = await res.json();
    } else {
      alert("❌ Failed to load employee data");
    }
  });

  // Update employee info
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
      goto("/employee");
    } else {
      const err = await res.json().catch(() => ({}));
      alert(`❌ Error: ${err.detail || "Update failed"}`);
    }
  }
</script>

<div class={styles.container}>
  <h2>Update Employee</h2>

  <div class={styles.formGroup}>
    <label class={styles.label}>Employee Name</label>
    <input
      type="text"
      bind:value={employee.employee_name}
      class={styles.input}
    />
  </div>

  <div class={styles.formGroup}>
    <label class={styles.label}>Role</label>
    <input type="text" bind:value={employee.role} class={styles.input} />
  </div>

  <div class={styles.formGroup}>
    <label class={styles.label}>Email</label>
    <input type="email" bind:value={employee.email} class={styles.input} />
  </div>

  <div class={styles.formGroup}>
    <label class={styles.label}> Active Status </label>

    <input
      type="checkbox"
      bind:checked={employee.is_active}
      class={styles.checkbox}
    />
  </div>

  <button on:click={handleUpdate} class={styles.button}>Save Changes</button>
</div>
