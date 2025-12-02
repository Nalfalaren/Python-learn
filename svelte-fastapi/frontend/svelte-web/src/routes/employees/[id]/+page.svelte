<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/detail/employee-detail.module.css";
  import { goto } from "$app/navigation";
  import { authStore } from "$lib/stores/AuthStore";

  let employeeId: string;
  export let params;

  let employee = {
    employee_name: "",
    role: "",
    email: "",
    is_active: "Inactive",
    created_at: "",
    updated_at: "",
  };

  employeeId = params.id;

  onMount(async () => {
    if(!authStore.isAuthenticated) goto("/employees/login")
    const token = localStorage.getItem("accessToken");
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/employee/${employeeId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      employee = await res.json();
    } else {
      alert("❌ Failed to load employee details");
      goto("/employees");
    }
  });

  function goBack() {
    goto("/employees");
  }
</script>

<div class={styles.wrapper}>
  <div class={styles.card}>
    <h2>👤 Employee Details</h2>
    <p class={styles.subtitle}>View full information about this employee.</p>

    <div class={styles.info}>
      <div class={styles.row}>
        <span class={styles.label}>Name:</span>
        <span class={styles.value}>{employee.employee_name}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Role:</span>
        <span class={styles.value}>{employee.role}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Email:</span>
        <span class={styles.value}>{employee.email}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Status:</span>
        <span
          class={`${styles.badge} ${
            employee.is_active ? styles.active : styles.inactive
          }`}
        >
          {employee.is_active === 'Active' ? "Active" : "Inactive"}
        </span>
      </div>

      {#if employee.created_at}
        <div class={styles.row}>
          <span class={styles.label}>Created At:</span>
          <span class={styles.value}>
            {new Date(employee.created_at).toLocaleString()}
          </span>
        </div>
      {/if}

      {#if employee.updated_at}
        <div class={styles.row}>
          <span class={styles.label}>Last Updated:</span>
          <span class={styles.value}>
            {new Date(employee.updated_at).toLocaleString()}
          </span>
        </div>
      {/if}
    </div>

    <button on:click={goBack} class={styles.button}>⬅ Back to List</button>
  </div>
</div>
