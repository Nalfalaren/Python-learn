<script lang="ts">
  import styles from "$lib/styles/register/Register.module.css";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { get } from "svelte/store";

  // form state
  let product_id: string = "";
  let product_name: string = "";
  let category: string = "";
  let price: number | string = "";
  let is_active: boolean = true;
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
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`${env.PUBLIC_API_URL}/products/${productId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || "Failed to fetch product");
      }

      const data = await res.json();

      // Fill form fields (adapt to your backend response shape)
      product_id = data.id ?? data.product_id ?? "";
      product_name = data.product_name ?? "";
      category = data.category ?? "";
      price = data.price ?? "";
      is_active = typeof data.is_active === "number" ? Boolean(data.is_active) : !!data.is_active;

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

    // basic validation
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
        is_active: is_active ? 1 : 0,
      };

      const token = localStorage.getItem("accessToken");
      const res = await fetch(`${env.PUBLIC_API_URL}/products/${productId}`, {
        method: "PUT", // or PATCH depending on your backend
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Failed to update product");
      }

      const data = await res.json();
      message = "✅ Product updated successfully!";
      console.log("Updated:", data);

      // redirect back to list (optional)
      goto("/products");
    } catch (err) {
      console.error("Error updating product:", err);
      message = "❌ Failed to update product — check console";
    } finally {
      saving = false;
    }
  }

  function handleReset() {
    // optionally re-fetch or clear — here we re-fetch by calling onMount logic
    onMount; // no-op to satisfy linter; to re-load you can call the fetch block logic instead
    // simple reset to blank if you prefer:
    // product_name = ""; category = ""; price = ""; is_active = true;
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
          bind:checked={is_active}
          class={styles.checkbox}
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
            // simple reset to initial values by reloading the page or refetching
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
