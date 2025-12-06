<script lang="ts">
  import styles from "$lib/styles/register/register.module.css";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { authStore } from "$lib/stores/AuthStore";

  // --- Reactive states ---
  let order_id = "";
  let customer_name = "";
  let email = "";
  let phone = "";
  let address = "";
  let status = "";
  let message = "";

  // --- Fetch current order info on mount ---
  onMount(async () => {
    const id = $page.params.id; // assuming route: /orders/edit/[id]
    if (!id) return;

    const token = localStorage.getItem("admin_access_token");
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/orders/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to fetch order");

      const data = await res.json();
      order_id = data?.order?.id;
      customer_name = data?.order?.customer_name;
      email = data?.order?.email;
      phone = data?.order?.phone;
      address = data?.order?.address;
      status = data?.order?.status;
    } catch (err) {
      console.error(err);
      message = "❌ Failed to load order";
    }
  });

  // --- Submit edit ---
  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!customer_name || !email || !phone) {
      alert("Please fill all required fields");
      return;
    }

    const token = localStorage.getItem("admin_access_token");

    const payload = {
      customer_name: customer_name.trim(),
      email: email.trim(),
      phone: phone.trim(),
      address: address.trim(),
      status: status.toUpperCase().trim(),
    };

    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/orders/${order_id}`, {
        method: "PUT", // or PATCH if backend supports partial update
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Failed to update order");

      message = "✅ Order updated successfully!";
      if ($authStore.role === "ADMIN") {
        goto("/orders");
      } else if ($authStore.role === "EMPLOYEE") {
        goto("/employee_orders");
      }
    } catch (err) {
      console.error("Order update failed:", err);
      message = "❌ Failed to update order — check backend logs.";
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Edit Order</h1>

  <form class={styles.form} on:submit|preventDefault={handleSubmit}>
    <label class={styles.field}>
      <span class={styles.label}>Customer Name</span>
      <input
        class={styles.input}
        disabled
        type="text"
        bind:value={customer_name}
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Email</span>
      <input
        class={styles.input}
        disabled
        type="email"
        bind:value={email}
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Phone</span>
      <input
        class={styles.input}
        disabled
        type="text"
        bind:value={phone}
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Address</span>
      <input class={styles.input} disabled type="text" bind:value={address} />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Status</span>
      <select bind:value={status} class={styles.input}>
        <option value="PENDING" disabled>Pending</option>
        <option value="ASSIGNED" disabled>Assigned</option>
        <option value="PROCESSING">Processing</option>
        <option value="COMPLETED">Completed</option>
        <option value="CANCELLED">Cancelled</option>
      </select>
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Update</button>
      <button
        type="button"
        class={styles.secondary}
        on:click={() => {
          if ($authStore.role === "ADMIN") {
            goto("/orders");
          } else if ($authStore.role === "EMPLOYEE") {
            goto("/employee_orders");
          }
        }}
      >
        Cancel
      </button>
    </div>
  </form>

  {#if message}
    <p class={styles.message}>{message}</p>
  {/if}
</main>
