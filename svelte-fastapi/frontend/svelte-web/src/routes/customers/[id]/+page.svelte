<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/detail/customer-detail.module.css";
  import { goto } from "$app/navigation";
  import { adminAuthStore } from "$lib/stores/AuthStore"
  import { adminApi } from "../../../hooks/apiFetch";

  let customerId: string;
  export let params;

  let customer = {
    customer_name: "",
    email: "",
    phone: "",
    address: "",
    is_active: "Inactive",
    created_at: "",
    updated_at: "",
  };

  customerId = params.id;

  onMount(async () => {
    if (!$adminAuthStore.isAuthenticated) goto("/employees/login");
    const res = await adminApi(`${import.meta.env.VITE_API_BASE_URL}/customers/${customerId}`);
      customer = await res.json()
  });

  function goBack() {
    goto("/customers");
  }
</script>

<div class={styles.wrapper}>
  <div class={styles.card}>
    <h2>🧍 Customer Details</h2>
    <p class={styles.subtitle}>View full information about this customer.</p>

    <div class={styles.info}>
      <div class={styles.row}>
        <span class={styles.label}>Name:</span>
        <span class={styles.value}>{customer.customer_name}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Email:</span>
        <span class={styles.value}>{customer.email}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Phone:</span>
        <span class={styles.value}>{customer.phone}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Address:</span>
        <span class={styles.value}>{customer.address}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Status:</span>
        <span
          class={`${styles.badge} ${
            customer.is_active ? styles.active : styles.inactive
          }`}
        >
          {customer.is_active === "Active" ? "Active" : "Inactive"}
        </span>
      </div>

      {#if customer.created_at}
        <div class={styles.row}>
          <span class={styles.label}>Created At:</span>
          <span class={styles.value}>
            {new Date(customer.created_at).toLocaleString()}
          </span>
        </div>
      {/if}

      {#if customer.updated_at}
        <div class={styles.row}>
          <span class={styles.label}>Last Updated:</span>
          <span class={styles.value}>
            {new Date(customer.updated_at).toLocaleString()}
          </span>
        </div>
      {/if}
    </div>

    <button on:click={goBack} class={styles.button}>⬅ Back to List</button>
  </div>
</div>
