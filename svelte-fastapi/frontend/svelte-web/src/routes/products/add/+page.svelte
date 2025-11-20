<script lang="ts">
  import styles from "$lib/styles/register/Register.module.css";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";

  // Form state
  let product_id: string = "";
  let product_name: string = "";
  let category: string = "";
  let price: number | string = "";
  let status: boolean = true;
  let message: string = "";

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    // Basic validation
    if (!product_id.trim() || !product_name.trim() || !category.trim() || !price) {
      alert("Please fill in all required fields");
      return;
    }

    const payload = {
      product_id: product_id.trim(),
      product_name: product_name.trim(),
      category: category.trim(),
      price: Number(price),
      is_active: status ? 1 : 0,
    };

    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`${env.PUBLIC_API_URL}/products`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Failed to create product");
      }

      const data = await res.json();
      message = "✅ Product created successfully!";
      console.log("Product created:", data);

      // Reset form
      product_id = "";
      product_name = "";
      category = "";
      price = "";
      status = true;

      // Redirect to product list
      goto("/products");
    } catch (err) {
      console.error("Error creating product:", err);
      message = "❌ Failed to create product — check console for details";
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Add Product</h1>

  <form class={styles.form} on:submit|preventDefault={handleSubmit}>
    <label class={styles.field}>
      <span class={styles.label}>Product ID</span>
      <input
        class={styles.input}
        type="text"
        bind:value={product_id}
        placeholder="Enter product ID"
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Product Name</span>
      <input
        class={styles.input}
        type="text"
        bind:value={product_name}
        placeholder="Enter product name"
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Category</span>
      <input
        class={styles.input}
        type="text"
        bind:value={category}
        placeholder="Enter category"
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Price</span>
      <input
        class={styles.input}
        type="number"
        step="0.01"
        bind:value={price}
        placeholder="Enter price"
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Active</span>
      <input
        type="checkbox"
        bind:checked={status}
        class={styles.checkbox}
      />
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Create</button>
      <button
        type="button"
        class={styles.secondary}
        on:click={() => {
          product_id = "";
          product_name = "";
          category = "";
          price = "";
          status = true;
        }}
      >
        Reset
      </button>
    </div>
  </form>

  {#if message}
    <p class={styles.message}>{message}</p>
  {/if}
</main>
