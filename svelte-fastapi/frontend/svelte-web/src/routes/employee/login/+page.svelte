<script>
    import { env } from "$env/dynamic/public";
    import { onMount } from "svelte";

    let email = "";
    let password = "";
    let remember = false;
    let showPassword = false;
    let loading = false;
    let message = "";
    let errors = { email: "", password: "", confirmPassword: "" };

    function validate() {
        errors = { email: "", password: "", confirmPassword: "" };

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.trim()) errors.email = "Vui lòng nhập email.";
        else if (!emailRegex.test(email)) errors.email = "Email không hợp lệ.";

        if (!password) errors.password = "Vui lòng nhập mật khẩu.";
        else if (password.length < 6)
            errors.password = "Mật khẩu ít nhất 6 ký tự.";

        return !errors.email && !errors.password && !errors.confirmPassword;
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (!validate()) return;
        loading = true;
        try {
            const url = new URL(`${env.PUBLIC_API_URL}/auth/login`);
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                message = errorData.detail;
                return
            }
            const data = await res.json().catch(() => ({}));
            message = data.message;
            localStorage.setItem("accessToken", data.access_token);
            window.location.href = `/employee?role=${data?.role?.toLowerCase()}`;
        } catch (err) {
            console.error(err);
            message = "Không thể kết nối tới server.";
        } finally {
            loading = false;
        }
    }

    let emailInput;
    onMount(() => {
        emailInput && emailInput.focus();
    });
</script>

<section class="container">
    <form
        class="card"
        on:submit|preventDefault={handleSubmit}
        aria-describedby={message ? "status" : undefined}
    >
        <h1>Đăng nhập</h1>

        <label class="field">
            <span>Email</span>
            <input
                bind:this={emailInput}
                type="email"
                placeholder="you@example.com"
                bind:value={email}
                aria-invalid={errors.email ? "true" : "false"}
                aria-describedby={errors.email ? "email-error" : undefined}
            />
            {#if errors.email}
                <div id="email-error" class="error">{errors.email}</div>
            {/if}
        </label>

        <label class="field">
            <span>Mật khẩu</span>
            <div class="password-row">
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Mật khẩu"
                    bind:value={password}
                    aria-invalid={errors.password ? "true" : "false"}
                    aria-describedby={errors.password
                        ? "password-error"
                        : undefined}
                />
                <button
                    type="button"
                    class="toggle"
                    on:click={() => (showPassword = !showPassword)}
                    aria-pressed={showPassword}
                    aria-label="Hiện/ẩn mật khẩu"
                    >{showPassword ? "Ẩn" : "Hiện"}</button
                >
            </div>
            {#if errors.password}
                <div id="password-error" class="error">{errors.password}</div>
            {/if}
        </label>

        <label class="inline">
            <input type="checkbox" bind:checked={remember} />
            <span>Ghi nhớ đăng nhập</span>
        </label>

        <button
            class="submit"
            type="submit"
            disabled={loading}
            aria-busy={loading}
        >
            {#if loading}
                <span class="spinner" aria-hidden="true"></span> Đang xử lý...
            {:else}
                Đăng nhập
            {/if}
        </button>

        <div class="links">
            <a href="/employee/forgot">Quên mật khẩu?</a>
            <a href="/employee/signup">Tạo tài khoản mới</a>
        </div>

        {#if message}
            <div id="status" class="status">{message}</div>
        {/if}
    </form>
</section>

<style>
    :global(body) {
        font-family:
            system-ui,
            -apple-system,
            "Segoe UI",
            Roboto,
            "Helvetica Neue",
            Arial;
        background: linear-gradient(180deg, #f6f8fb 0%, #ffffff 100%);
        margin: 0;
        padding: 0;
        display: flex;
        min-height: 100vh;
        align-items: center;
        justify-content: center;
    }
    .container {
        width: 100%;
        max-width: 420px;
        padding: 16px;
    }
    .card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(12, 20, 30, 0.08);
        padding: 28px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    h1 {
        margin: 0 0 6px 0;
        font-size: 20px;
    }
    .field span {
        display: block;
        font-size: 13px;
        margin-bottom: 6px;
        color: #333;
    }
    input[type="email"],
    input[type="password"],
    input[type="text"] {
        width: 100%;
        padding: 10px 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        font-size: 14px;
        box-sizing: border-box;
    }
    .password-row {
        display: flex;
        gap: 8px;
    }
    .password-row .toggle {
        flex: 0 0 68px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: transparent;
        cursor: pointer;
        padding: 8px;
        font-size: 13px;
    }
    .inline {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    .submit {
        padding: 10px 12px;
        border-radius: 10px;
        border: none;
        background: #2563eb;
        color: white;
        font-weight: 600;
        cursor: pointer;
        font-size: 15px;
    }
    .submit[disabled] {
        opacity: 0.7;
        cursor: not-allowed;
    }
    .links {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        margin-top: 6px;
    }
    .links a {
        color: #2563eb;
        text-decoration: none;
    }
    .error {
        color: #b91c1c;
        font-size: 13px;
        margin-top: 6px;
    }
    .status {
        margin-top: 10px;
        font-size: 14px;
    }
    .spinner {
        display: inline-block;
        width: 14px;
        height: 14px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-left-color: white;
        border-radius: 50%;
        margin-right: 8px;
        animation: spin 1s linear infinite;
        vertical-align: middle;
    }
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    @media (max-width: 480px) {
        .card {
            padding: 20px;
        }
    }
</style>
