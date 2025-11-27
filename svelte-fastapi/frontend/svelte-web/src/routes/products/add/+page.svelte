<script lang="ts">
  import styles from "$lib/styles/register/Register.module.css";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import { v4 as uuidv4 } from 'uuid';
  // Form state
  let product_id = "";
  let product_name = "";
  let category = "";
  let price: number | string = "";
  let status = true;
  let message = "";

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!product_name || !category || !price) {
      alert("Please fill all required fields");
      return;
    }

    const token = localStorage.getItem("accessToken");

    // 👇 Create multipart form data
    const formData = new FormData();
    formData.append("product_id", String(uuidv4()));
    formData.append("product_name", product_name.trim());
    formData.append("category", category.trim());
    formData.append("price", String(price));
    formData.append("is_active", status ? "1" : "0");

    try {
      const res = await fetch(`${env.PUBLIC_API_URL}/products`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
        body: formData, // 👈 Send file + text
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
      status = true;
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

    <label class={styles.field}>
      <span class={styles.label}>Active</span>
      <input type="checkbox" bind:checked={status} class={styles.checkbox} />
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Create</button>

      <button type="button" class={styles.secondary} on:click={() => {
        product_id = "";
        product_name = "";
        category = "";
        price = "";
        status = true;
      }}>
        Reset
      </button>
    </div>
  </form>

  {#if message}
    <p class={styles.message}>{message}</p>
  {/if}
</main>
