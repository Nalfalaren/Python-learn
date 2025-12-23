<script lang="ts">
  import styles from "$lib/styles/register/register.module.css";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { adminAuthStore } from "$lib/stores/AuthAdmin";
  import { adminApi } from "../../../../hooks/apiFetch";
    import MessageModal from "../../../../components/modal-success/MessageModal.svelte";

  // --- Reactive states ---
  let order_id = "";
  let customer_name = "";
  let email = "";
  let phone = "";
  let address = "";
  let status = "";
  let message = "";
  let showMessageModal = false;
  let messageType: "success" | "error" = "success";

  // Auto close modal
   function showMessage(msg: string, type: "success" | "error" = "success") {
        message = msg;
        messageType = type;
        showMessageModal = true;

        setTimeout(() => {
            showMessageModal = false;
        }, 2500);
    }

  onMount(async () => {
    const id = $page.params.id;
    if (!id) return;

    try {
      const res = await adminApi(`${import.meta.env.VITE_API_BASE_URL}/orders/${id}`);

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
      showMessage("❌ Failed to load order");
    }
  });

  // --- Submit edit ---
  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!customer_name || !email || !phone) {
      showMessage("⚠ Please fill all required fields");
      return;
    }

    const payload = {
      customer_name: customer_name.trim(),
      email: email.trim(),
      phone: phone.trim(),
      address: address.trim(),
      status: status.toUpperCase().trim(),
    };

    try {
      const res = await adminApi(`${import.meta.env.VITE_API_BASE_URL}/orders/${order_id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        showMessage(errData?.detail || "❌ Failed to update order.");
        return;
      }

      showMessage("✅ Order updated successfully!");

      setTimeout(() => {
        if ($adminAuthStore.role === "ADMIN") goto("/orders");
        else goto("/employee_orders");
      }, 1000);
    } catch (err) {
      console.error("Order update failed:", err);
      showMessage("❌ Failed to update order — check backend logs.");
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Edit Order</h1>

  <form class={styles.form} on:submit|preventDefault={handleSubmit}>
    <label class={styles.field}>
      <span class={styles.label}>Customer Name</span>
      <input class={styles.input} disabled type="text" bind:value={customer_name} required />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Email</span>
      <input class={styles.input} disabled type="email" bind:value={email} required />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Phone</span>
      <input class={styles.input} disabled type="text" bind:value={phone} required />
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
          if ($adminAuthStore.role === "ADMIN") goto("/orders");
          else goto("/employee_orders");
        }}
      >
        Cancel
      </button>
    </div>
  </form>

  <MessageModal show={showMessageModal} message={message} type={messageType} />
</main>

<style>
  .messageModalOverlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 50;
  }

  .messageModal {
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px 30px;
    border-radius: 8px;
    z-index: 100;
    text-align: center;
    width: 320px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    animation: pop 0.22s ease-out;
  }

  @keyframes pop {
    from { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
    to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
  }

  .closeBtn {
    margin-top: 15px;
    padding: 7px 16px;
    border-radius: 4px;
    background: #444;
    color: white;
  }

  .closeBtn:hover {
    background: #000;
  }
</style>
