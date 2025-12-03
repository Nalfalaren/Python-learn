<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { authStore } from "$lib/stores/AuthStore";
    let employeeName = "";
    let email = "";
    let password = "";
    let confirmPassword = "";
    let role = "EMPLOYEE";
    let showPassword = false;
    let loading = false;
    let message = "";
    let errors = {
        employeeName: "",
        email: "",
        password: "",
        confirmPassword: "",
        role: "",
    };

    // ✅ Kiểm tra dữ liệu form
    function validate() {
        errors = {
            employeeName: "",
            email: "",
            password: "",
            confirmPassword: "",
            role: "",
        };
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if(!employeeName.trim()) errors.employeeName = "Vui lòng nhập tên nhân viên"
        if (!email.trim()) errors.email = "Vui lòng nhập email.";
        else if (!emailRegex.test(email)) errors.email = "Email không hợp lệ.";

        if (!password.trim()) errors.password = "Vui lòng nhập mật khẩu.";
        else if (password.length < 6)
            errors.password = "Mật khẩu ít nhất 6 ký tự.";

        if (confirmPassword !== password)
            errors.confirmPassword = "Mật khẩu xác nhận không trùng khớp.";

        return !errors.employeeName && !errors.email && !errors.password && !errors.confirmPassword;
    }

    // ✅ Gửi dữ liệu đăng ký tới API FastAPI
    async function handleSubmit(e) {
        e.preventDefault();
        message = "";

        if (!validate()) return;
        loading = true;

        try {
            const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    employee_name: employeeName,
                    email,
                    password,
                    confirmPassword,
                    role,
                }),
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                message = data.detail || "Đăng ký thất bại. Vui lòng thử lại.";
            } else {
                message = data.message || "Đăng ký thành công!";
                // 👉 Có thể redirect sang trang đăng nhập
                window.location.href = `/employees?role=${data?.role?.toLowerCase()}`;
            }
        } catch (err) {
            console.error(err);
            message = "Không thể kết nối tới server.";
        } finally {
            loading = false;
        }
    }

    let emailInput;
    onMount(() => emailInput?.focus());

    onMount(() => {
    if(!$authStore.isAuthenticated) goto("/employees/login")
    })
</script>

<section class="container">
    <form class="card" on:submit|preventDefault={handleSubmit}>
        <h1>Tạo tài khoản</h1>

        <label class="field">
            <span>Employee Name</span>
            <input
                type="text"
                bind:value={employeeName}
                placeholder="Ryan"
            />
            {#if errors.employeeName}<div class="error">{errors.employeeName}</div>{/if}
        </label>

        <label class="field">
            <span>Email</span>
            <input
                bind:this={emailInput}
                type="email"
                bind:value={email}
                placeholder="you@example.com"
            />
            {#if errors.email}<div class="error">{errors.email}</div>{/if}
        </label>

        <label class="field">
            <span>Mật khẩu</span>
            <div class="password-row">
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Nhập mật khẩu"
                    bind:value={password}
                />
                <button
                    type="button"
                    class="toggle"
                    on:click={() => (showPassword = !showPassword)}
                >
                    {showPassword ? "Ẩn" : "Hiện"}
                </button>
            </div>
            {#if errors.password}<div class="error">{errors.password}</div>{/if}
        </label>

        <label class="field">
            <span>Xác nhận mật khẩu</span>
            <input
                type="password"
                placeholder="Nhập lại mật khẩu"
                bind:value={confirmPassword}
            />
            {#if errors.confirmPassword}
                <div class="error">{errors.confirmPassword}</div>
            {/if}
        </label>

        <label class="field">
            <span>Role</span>
            <input type="text" bind:value={role} disabled>
            {#if errors.role}
                <div class="error">{errors.role}</div>
            {/if}
        </label>

        <button class="submit" type="submit" disabled={loading}>
            {#if loading}
                <span class="spinner"></span> Đang xử lý...
            {:else}
                Đăng ký
            {/if}
        </button>

        <div class="links">
            <a href="/login">Đã có tài khoản? Đăng nhập</a>
        </div>

        {#if message}<div class="status">{message}</div>{/if}
    </form>
</section>

<style>
    :global(body) {
        font-family: system-ui, sans-serif;
        background: linear-gradient(180deg, #eef2f7, #fff);
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
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
    .field select {
        width: 100%;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #ccc;
    }
    h1 {
        margin: 0 0 10px;
        font-size: 20px;
    }
    .field span {
        display: block;
        font-size: 13px;
        margin-bottom: 4px;
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
    }
    .password-row {
        display: flex;
        gap: 8px;
    }
    .toggle {
        flex: 0 0 68px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: transparent;
        cursor: pointer;
        padding: 8px;
        font-size: 13px;
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
        animation: spin 1s linear infinite;
        vertical-align: middle;
    }
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>