<script>
  let email = "";
  let message = "";
  let error = "";
  let loading = false;

  async function handleSubmit(e) {
    e.preventDefault();
    error = "";
    message = "";
    loading = true;

    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customer/forget_password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });

      const data = await res.json();

      if (!res.ok) {
        error = data.detail || "Something went wrong";
        return;
      }

      message = data.message;
      email = ""; // reset input
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<style>
  body, html {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background-color: #f5f5f5;
  }

  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
  }

  .card {
    background: #fff;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    max-width: 400px;
    width: 100%;
  }

  h1 {
    text-align: center;
    margin-bottom: 30px;
    color: #333;
  }

  input[type="email"] {
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
    background-color: #4CAF50;
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

<div class="container">
  <div class="card">
    <h1>Forgot Password</h1>
    <form on:submit={handleSubmit}>
      <input
        type="email"
        bind:value={email}
        placeholder="Enter your email"
        required
      />
      <button type="submit" disabled={loading}>
        {#if loading}Sending...{/if}
        {#if !loading}Send Reset Link{/if}
      </button>
    </form>

    {#if message}
      <div class="message success">{message}</div>
    {/if}

    {#if error}
      <div class="message error">{error}</div>
    {/if}
  </div>
</div>
