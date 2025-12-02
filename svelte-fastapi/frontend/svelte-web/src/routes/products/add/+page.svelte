<script lang="ts">
  import styles from "$lib/styles/register/register.module.css";
  import { goto } from "$app/navigation";
  // Form state
  let product_id = "";
  let product_name = "";
  let category = "";
  let price: number | string = "";
  let message = "";

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!product_name || !category || !price) {
      alert("Please fill all required fields");
      return;
    }

    const token = localStorage.getItem("accessToken");

    const payload = {
      product_name: product_name?.trim(),
      category: category?.trim(),
      price
    }
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/products`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json", 
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Failed to create product");
      }

      message = "✅ Product created successfully!";

      // Reset
      product_id = "";
      product_name = "";
      category = "";
      price = "";
      goto("/products");
    } catch (err) {
      console.error("Product creation failed:", err);
      message = "❌ Failed to create product — check backend logs.";
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Add Product</h1>

  <form class={styles.form} on:submit|preventDefault={handleSubmit}>
    <label class={styles.field}>
      <span class={styles.label}>Product Name</span>
      <input class={styles.input} type="text" bind:value={product_name} required />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Category</span>
      <input class={styles.input} type="text" bind:value={category} required />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Price</span>
      <input class={styles.input} type="number" bind:value={price} step="0.01" required />
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Create</button>

      <button type="button" class={styles.secondary} on:click={() => {
        product_id = "";
        product_name = "";
        category = "";
        price = "";
      }}>
        Reset
      </button>
    </div>
  </form>

  {#if message}
    <p class={styles.message}>{message}</p>
  {/if}
</main>
