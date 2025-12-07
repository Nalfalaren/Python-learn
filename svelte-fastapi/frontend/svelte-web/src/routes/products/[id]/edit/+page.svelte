<script lang="ts">
  import styles from "$lib/styles/register/register.module.css";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { get } from "svelte/store";
    import { adminApi } from "../../../../hooks/apiFetch";

  // form state
  let product_id: string = "";
  let product_name: string = "";
  let category: string = "";
  let price: number | string = "";
  let description: string = "";
  let rating: number | string = "";
  let stock: number = 0;
  let message: string = "";
  let loading = false;
  let saving = false;

  // get id from route params
  const productId = get(page).params.id;

  onMount(async () => {
    if (!productId) {
      message = "❌ Missing product id in URL";
      return;
    }

    loading = true;
    try {
      const res = await adminApi(
        `${import.meta.env.VITE_API_BASE_URL}/products/${productId}`,
      );

      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || "Failed to fetch product");
      }

      const data = await res.json();

      product_id = data.id ?? data.product_id ?? "";
      product_name = data.product_name ?? "";
      category = data.category ?? "";
      price = data.price ?? "";
      description = data.description ?? "";
      rating = data.rating ?? "";
      stock = data.stock ?? 0

      message = "";
    } catch (err) {
      console.error("Fetch product error:", err);
      message = "❌ Failed to load product — check console";
    } finally {
      loading = false;
    }
  });

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!product_name.trim() || !category.trim() || price === "" || price === null) {
      alert("Please fill required fields");
      return;
    }

    saving = true;
    try {
      const payload = {
        product_name: product_name.trim(),
        category: category.trim(),
        price: Number(price),
        description: description.trim(),
        rating: rating ? Number(rating).toFixed(2) : 0,
        stock: stock || 0
      };
      const res = await adminApi(
        `${import.meta.env.VITE_API_BASE_URL}/admin/products/${productId}`,
        {
          method: "PUT",
          body: JSON.stringify(payload),
        },
      );

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Failed to update product");
      }

      const data = await res.json();
      message = "✅ Product updated successfully!";
      console.log("Updated:", data);

      goto("/products");
    } catch (err) {
      console.error("Error updating product:", err);
      message = "❌ Failed to update product — check console";
    } finally {
      saving = false;
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Edit Product</h1>

  {#if loading}
    <p class={styles.message}>Loading product...</p>
  {:else}
    <form class={styles.form} on:submit|preventDefault={handleSubmit}>
      <label class={styles.field}>
        <span class={styles.label}>Product ID</span>
        <input
          class={styles.input}
          type="text"
          bind:value={product_id}
          placeholder="Product ID"
          disabled
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
        <select class={styles.input} bind:value={category} required>
          <option value="" disabled selected>Choose category</option>
          <option value="Multirotor">Multirotor</option>
          <option value="Fixed-wing">Fixed-wing</option>
        </select>
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
        <span class={styles.label}>Description</span>
        <textarea
          class={styles.input}
          bind:value={description}
          placeholder="Enter product description"
        ></textarea>
      </label>

      <label class={styles.field}>
        <span class={styles.label}>Rating</span>
        <input
          class={styles.input}
          type="number"
          min="0"
          max="5"
          step="0.1"
          bind:value={rating}
          placeholder="0 - 5"
        />
      </label>

       <label class={styles.field}>
        <span class={styles.label}>Stock</span>
        <input
          class={styles.input}
          type="number"
          step="1"
          bind:value={stock}
          placeholder="Enter stock"
          required
        />
      </label>

      <div class={styles.actions}>
        <button class={styles.button} type="submit" disabled={saving}>
          {#if saving}Saving...{:else}Save{/if}
        </button>

        <button
          type="button"
          class={styles.secondary}
          on:click={() => {
            goto(`/products/${productId}/edit`, { replaceState: true });
          }}
        >
          Reset
        </button>

        <button
          type="button"
          class={styles.secondary}
          on:click={() => goto("/products")}
        >
          Cancel
        </button>
      </div>
    </form>

    {#if message}
      <p class={styles.message}>{message}</p>
    {/if}
  {/if}
</main>
