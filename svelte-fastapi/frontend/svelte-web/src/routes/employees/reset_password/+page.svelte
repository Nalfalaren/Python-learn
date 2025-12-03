<script>
    import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { onMount } from "svelte";

  let password = "";
  let confirmPassword = "";
  let token = "";

  let loading = false;
  let error = "";
  let message = "";

  onMount(() => {
    token = $page.url.searchParams.get("token");
  });

  async function handleSubmit(e) {
    e.preventDefault();
    error = "";
    message = "";

    if (password !== confirmPassword) {
      error = "Mật khẩu không trùng khớp!";
      return;
    }

    loading = true;

    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/employee/reset_password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token, new_password: password, confirm_password: confirmPassword}),
        }
      );

      const data = await res.json();
      if (!res.ok) {
        error = data.detail || "Có lỗi xảy ra!";
        return;
      }

      message = data.message || "Đặt lại mật khẩu thành công!";
      password = "";
      confirmPassword = "";
      goto('/employees/login')
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="container">
  <div class="card">
    <h1>Đặt lại mật khẩu</h1>

    {#if !token}
      <p class="message error">Token không hợp lệ hoặc đã hết hạn.</p>
    {:else}
      <form on:submit={handleSubmit}>
        <label>Mật khẩu mới:</label>
        <input
          type="password"
          bind:value={password}
          placeholder="Nhập mật khẩu mới"
          required
        />

        <label>Nhập lại mật khẩu:</label>
        <input
          type="password"
          bind:value={confirmPassword}
          placeholder="Nhập lại mật khẩu"
          required
        />

        <button type="submit" disabled={loading}>
          {#if loading}Đang xử lý...{/if}
          {#if !loading}Đặt lại mật khẩu{/if}
        </button>
      </form>
    {/if}

    {#if message}
      <div class="message success">{message}</div>
    {/if}

    {#if error}
      <div class="message error">{error}</div>
    {/if}
  </div>
</div>

<style>
  body, html {
    margin: 0;
    padding: 0;
    font-family: system-ui, sans-serif;
    background-color: #f5f5f5;
  }

  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
    font-family: system-ui, sans-serif;
  }

  .card {
    background: #fff;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    max-width: 400px;
    width: 100%;
  }

  h1 {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
  }

  input {
    width: 100%;
    padding: 12px 15px;
    margin-bottom: 15px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 16px;
    box-sizing: border-box;
  }

  button {
    width: 100%;
    padding: 12px;
    background-color: #4caf50;
    color: white;
    border: none;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s;
  }

  button:hover {
    background-color: #45a049;
  }

  .message {
    text-align: center;
    margin-top: 15px;
    padding: 10px;
    border-radius: 8px;
    font-weight: bold;
  }

  .success {
    background-color: #d4edda;
    color: #155724;
  }

  .error {
    background-color: #f8d7da;
    color: #721c24;
  }
</style>
