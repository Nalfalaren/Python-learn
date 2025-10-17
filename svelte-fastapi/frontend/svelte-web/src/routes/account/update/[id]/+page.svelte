<script lang="ts">
  import { onMount } from "svelte";  
  import styles from "$lib/styles/update-account/Update.module.css";
    import { env } from "$env/dynamic/public";
    import { goto } from "$app/navigation";

  let accountId: string;
  let account = {
    owner: "",
    balance: 0,
    interest_rate: 0
  };

  // Lấy id từ URL (SvelteKit)
  export let params;
  accountId = params.id;

  // Fetch dữ liệu account hiện tại
  onMount(async () => {
    const res = await fetch(`${env.PUBLIC_API_URL}/account/${accountId}`);
    if (res.ok) {
      account = await res.json();
    }
  });

  // Gửi request update
  async function handleUpdate() {
    const res = await fetch(`${env.PUBLIC_API_URL}/account/${accountId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(account)
    });

    if (res.ok) {
      alert("✅ Account updated successfully!");
      goto("/account")
    } else {
      const err = await res.json();
      alert(`❌ Error: ${err.detail || "Update failed"}`);
    }
  }
</script>

<div class={styles.container}>
  <h2>Update Account</h2>

  <div class={styles.formGroup}>
    <label class={styles.label}>Owner</label>
    <input type="text" bind:value={account.owner} class={styles.input} />
  </div>

  <div class={styles.formGroup}>
    <label class={styles.label}>Balance</label>
    <input type="number" bind:value={account.balance} class={styles.input} />
  </div>

  <div class={styles.formGroup}>
    <label class={styles.label}>Interest Rate (%)</label>
    <input type="number" bind:value={account.interest_rate} step="0.01" class={styles.input} />
  </div>

  <button on:click={handleUpdate} class={styles.button}>Save Changes</button>
</div>
