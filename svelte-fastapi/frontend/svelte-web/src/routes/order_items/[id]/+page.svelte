<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/detail/employee-detail.module.css"; 
  // dùng lại style EXACT để giống hoàn toàn
  import { goto } from "$app/navigation";
  import { authStore } from "$lib/stores/AuthStore";

  let itemId: string;
  export let params;

  let orderItem = {
    id: "",
    order_id: "",
    product_name: "",
    qty: 0,
    price: 0,
    total_price: 0,
    created_at: "",
    updated_at: "",
  };

  itemId = params.id;

  onMount(async () => {
    if (!authStore.isAuthenticated) goto("/employees/login");

    const token = localStorage.getItem("accessToken");
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/order_items/${itemId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      orderItem = await res.json();
      orderItem = {...orderItem, total_price: (orderItem.qty * orderItem.price)}
    } else {
      alert("❌ Failed to load order item");
      goto("/orders");
    }
  });

  function goBack() {
    goto("/orders");
  }
</script>

<div class={styles.wrapper}>
  <div class={styles.card}>
    <h2>📦 Order Item Details</h2>
    <p class={styles.subtitle}>Full information about this order item.</p>

    <div class={styles.info}>
      <div class={styles.row}>
        <span class={styles.label}>Product:</span>
        <span class={styles.value}>{orderItem.product_name}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Quantity:</span>
        <span class={styles.value}>{orderItem.qty}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Price:</span>
        <span class={styles.value}>${orderItem.price}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Total:</span>
        <span class={styles.value}>${orderItem.total_price}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Order ID:</span>
        <span class={styles.value}>{orderItem.order_id || 'N/A'}</span>
      </div>

      {#if orderItem.created_at}
        <div class={styles.row}>
          <span class={styles.label}>Created At:</span>
          <span class={styles.value}>
            {new Date(orderItem.created_at).toLocaleString()}
          </span>
        </div>
      {/if}

      {#if orderItem.updated_at}
        <div class={styles.row}>
          <span class={styles.label}>Updated At:</span>
          <span class={styles.value}>
            {new Date(orderItem.updated_at).toLocaleString()}
          </span>
        </div>
      {/if}
    </div>

    <button on:click={goBack} class={styles.button}>⬅ Back to Orders</button>
  </div>
</div>
