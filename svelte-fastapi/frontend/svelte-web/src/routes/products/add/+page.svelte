<script lang="ts">
  import styles from "$lib/styles/register/register.module.css";
  import { goto } from "$app/navigation";
    import { adminApi } from "../../../hooks/apiFetch";
  
  // Form state
  let product_id = "";
  let product_name = "";
  let category = "";
  let price: number | string = "";
  let description = "";
  let rating: number | string = "";
  let stock: number = 0
  let message = "";

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!product_name || !category || !price) {
      alert("Please fill all required fields");
      return;
    }

    const token = localStorage.getItem("admin_access_token");

    const payload = {
      product_name: product_name?.trim(),
      category: category?.trim(),
      price,
      description: description?.trim(),
      rating: rating ? Number(rating) : undefined,
      stock: stock || 0
    };

    try {
      const res = await adminApi(`${import.meta.env.VITE_API_BASE_URL}/admin/products`, {
        method: "POST",
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
      description = "";
      rating = "";
      stock = 0
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
      <input class={styles.input} type="text" bind:value={product_name} required placeholder="Enter product name" />
    </label>

     <label class={styles.field}>
        <span class={styles.label}>Category</span>
        <select class={styles.input} bind:value={category} required>
          <option value="" disabled selected>Choose category</option>
          <option value="Multirotor">Multirotor</option>
          <option value="Fixed-wing">Fixed-wing</option>
        </select>
      </label>

    <label class={styles.field}>
      <span class={styles.label}>Price</span>
      <input class={styles.input} type="number" bind:value={price} step="0.01" required placeholder="Enter price" />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Description</span>
      <textarea class={styles.input} bind:value={description} placeholder="Enter product description"></textarea>
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Rating</span>
      <input class={styles.input} type="number" min="0" max="5" step="0.1" bind:value={rating} placeholder="0 - 5" />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Stock</span>
      <input class={styles.input} type="number" min="0" step="1" bind:value={stock} placeholder="Stock" />
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Create</button>

      <button type="button" class={styles.secondary} on:click={() => {
        product_id = "";
        product_name = "";
        category = "";
        price = "";
        description = "";
        rating = "";
      }}>
        Reset
      </button>
    </div>
  </form>

  {#if message}
    <p class={styles.message}>{message}</p>
  {/if}
</main>
