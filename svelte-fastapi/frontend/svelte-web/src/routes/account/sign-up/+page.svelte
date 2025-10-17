<script lang="ts">
  import styles from "$lib/styles/register/Register.module.css";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";

  // form state
  let owner: string = "";
  let type: "saving" | "business" = "saving";
  let message: string = $state('')

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!owner.trim()) {
      alert("Vui lòng nhập tên owner");
      return;
    }

    const payload = { owner: owner.trim(), type };

    try {
      const res = await fetch(`${env.PUBLIC_API_URL}/account`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        // nếu backend trả lỗi, cố gắng đọc message
        let text = await res.text();
        throw new Error(text || "Failed to create account");
      }

      const data = await res.json();
      console.log(data);
      message = data
      goto("/account")

      // reset form
      owner = "";
      type = "saving";
    } catch (err) {
      console.error(err);
      alert("Tạo account thất bại — kiểm tra console để biết chi tiết");
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Đăng ký tài khoản</h1>

  <form class={styles.form} on:submit|preventDefault={handleSubmit} aria-label="create-account-form">
    <label class={styles.field}>
      <span class={styles.label}>Owner</span>
      <input
        class={styles.input}
        type="text"
        placeholder="Tên chủ sở hữu"
        bind:value={owner}
        required
        aria-required="true"
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Account Type</span>
      <select class={styles.select} bind:value={type}>
        <option value="saving">Saving Account</option>
        <option value="business">Business Account</option>
      </select>
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Sign up</button>
      <button type="button" class={styles.secondary} on:click={() => { owner=""; type="saving"; }}>
        Reset
      </button>
    </div>
  </form>
  <div>
    {message}
  </div>
</main>
