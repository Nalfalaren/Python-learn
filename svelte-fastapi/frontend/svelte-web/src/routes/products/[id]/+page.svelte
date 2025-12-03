<script lang="ts">
  import { onMount } from "svelte";
  import styles from "$lib/styles/detail/customer-detail.module.css"; 
  // vẫn dùng lại CSS cũ cho đồng nhất giao diện
  import { goto } from "$app/navigation";
  import { authStore } from "$lib/stores/AuthStore";

  let productId: string;
  export let params;

  let product = {
    product_name: "",
    category: "",
    price: 0,
    created_at: "",
    updated_at: "",
  };

  productId = params.id;

  onMount(async () => {
    if (!$authStore.isAuthenticated) goto("/employees/login");

    const token = localStorage.getItem("accessToken");

    const res = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/products/${productId}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (res.ok) {
      product = await res.json();
    } else {
      alert("❌ Failed to load product details");
      goto("/products");
    }
  });

  function goBack() {
    goto("/products");
  }
</script>

<div class={styles.wrapper}>
  <div class={styles.card}>
    <h2>📦 Product Details</h2>
    <p class={styles.subtitle}>View detailed information about this product.</p>

    <div class={styles.info}>
      <div class={styles.row}>
        <span class={styles.label}>Product Name:</span>
        <span class={styles.value}>{product.product_name}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Category:</span>
        <span class={styles.value}>{product.category}</span>
      </div>

      <div class={styles.row}>
        <span class={styles.label}>Price:</span>
        <span class={styles.value}>${product.price}</span>
      </div>

      {#if product.created_at}
        <div class={styles.row}>
          <span class={styles.label}>Created At:</span>
          <span class={styles.value}>
            {new Date(product.created_at).toLocaleString()}
          </span>
        </div>
      {/if}

      {#if product.updated_at}
        <div class={styles.row}>
          <span class={styles.label}>Last Updated:</span>
          <span class={styles.value}>
            {new Date(product.updated_at).toLocaleString()}
          </span>
        </div>
      {/if}
    </div>

    <button on:click={goBack} class={styles.button}>⬅ Back to List</button>
  </div>
</div>
