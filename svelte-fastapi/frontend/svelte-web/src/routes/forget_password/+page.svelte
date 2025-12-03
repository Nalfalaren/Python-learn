<script>
  let email = "";
  let message = "";
  let error = "";
  let loading = false;
  let token = "";

  async function handleSubmit(e) {
    e.preventDefault();
    error = "";
    message = "";
    token = "";
    loading = true;

    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/customer/forget_password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );

      const data = await res.json();

      if (!res.ok) {
        error = data.detail || "Something went wrong";
        return;
      }

      message = data.message;
      token = data.token; 
      email = "";
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="container">
  <div class="card">
    <h1>Quên mật khẩu</h1>

    <form on:submit={handleSubmit}>
      <label>Email của bạn</label>
      <input
        type="email"
        bind:value={email}
        placeholder="Nhập email..."
        required
        disabled={loading}
      />

      <button type="submit" disabled={loading}>
        {#if loading}⏳ Đang gửi...{/if}
        {#if !loading}Gửi liên kết đặt lại mật khẩu{/if}
      </button>
    </form>

     {#if message}
      <div class="message success">
        <p>{message}</p>
        <!-- svelte-ignore a11y_consider_explicit_label -->
        <a href={`/reset_password?token=${token}`}>Link</a>
      </div>
    {/if}

    {#if error}
      <div class="message error">{error}</div>
    {/if}
  </div>
</div>

<style>
  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f5f6fa;
    padding: 20px;
  }

  .card {
    background: #fff;
    padding: 35px;
    border-radius: 16px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.3s ease;
  }

  h1 {
    text-align: center;
    margin-bottom: 25px;
    font-size: 26px;
    color: #333;
    font-weight: 600;
  }

  input {
    width: 100%;
    padding: 12px 14px;
    margin-top: 8px;
    border: 1px solid #ccc;
    border-radius: 10px;
    font-size: 15px;
    transition: border 0.2s;
  }

  input:focus {
    border-color: #4caf50;
    outline: none;
  }

  button {
    width: 100%;
    padding: 12px;
    margin-top: 15px;
    border: none;
    background: #4caf50;
    color: #fff;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.25s;
  }

  button:hover:not([disabled]) {
    background: #43a047;
  }

  button[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .message {
    margin-top: 20px;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
  }

  .success {
    background: #d4edda;
    color: #155724;
  }

  .error {
    background: #f8d7da;
    color: #721c24;
  }

  .reset-link-box {
    margin-top: 10px;
    word-break: break-all;
  }

  .copy-btn {
    margin-top: 10px;
    width: auto;
    padding: 6px 12px;
    background: #2196f3;
    border: none;
    color: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
  }

  .copy-btn:hover {
    background: #1976d2;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px);}
    to { opacity: 1; transform: translateY(0);}
  }
</style>
