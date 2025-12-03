<script>
    import { onMount } from "svelte";

    let name = "";
    let email = "";
    let phone = "";
    let address = "";
    let is_active = 'Inactive';
    let password = "";
    let confirmPassword = "";
    let showPassword = false;
    let loading = false;
    let message = "";

    let errors = {
        name: "",
        email: "",
        phone: "",
        address: "",
        password: "",
        confirmPassword: "",
    };

    // Validate
    function validate() {
        errors = { name: "", email: "", phone: "", address: "", password: "", confirmPassword: "" };
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!phone.trim()) errors.phone = "Please enter phone number.";
        else if (!/^[0-9]{9,11}$/.test(phone))
            errors.phone = "Invalid phone number.";

        if (!address.trim()) errors.address = "Please enter address.";

        if (!name.trim()) errors.name = "Please enter full name.";

        if (!email.trim()) errors.email = "Please enter email.";
        else if (!emailRegex.test(email)) errors.email = "Invalid email address.";

        if (!password.trim()) errors.password = "Please enter password.";
        else if (password.length < 6)
            errors.password = "Password must be at least 6 characters.";

        if (confirmPassword !== password)
            errors.confirmPassword = "Passwords do not match.";

        return (
            !errors.name &&
            !errors.email &&
            !errors.phone &&
            !errors.address &&
            !errors.password &&
            !errors.confirmPassword
        );
    }

    // Submit
    async function handleSubmit(e) {
        e.preventDefault();
        message = "";

        if (!validate()) return;

        loading = true;

        try {
            const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    customer_name: name,
                    email,
                    phone,
                    address,
                    password,
                    confirmPassword,
                    is_active: 'Inactive'
                }),
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                message = data.detail || "Registration failed.";
            } else {
                message = data.message || "Registration successful!";
                window.location.href = "/login";
            }
        } catch (err) {
            message = "Unable to connect to the server.";
        } finally {
            loading = false;
        }
    }

    let emailInput;
    onMount(() => emailInput?.focus());
</script>

<section class="container">
    <form class="card" on:submit|preventDefault={handleSubmit}>
        <h1>Customer Registration</h1>

        <label class="field">
            <span>Full Name</span>
            <input type="text" bind:value={name} placeholder="John Doe" />
            {#if errors.name}<div class="error">{errors.name}</div>{/if}
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
            <span>Phone Number</span>
            <input type="text" bind:value={phone} placeholder="0123456789" />
            {#if errors.phone}<div class="error">{errors.phone}</div>{/if}
        </label>

        <label class="field">
            <span>Address</span>
            <input
                type="text"
                bind:value={address}
                placeholder="Street, City, District..."
            />
            {#if errors.address}<div class="error">{errors.address}</div>{/if}
        </label>

        <label class="field">
            <span>Password</span>
            <div class="password-row">
                <input
                    type={showPassword ? "text" : "password"}
                    bind:value={password}
                    placeholder="Enter password"
                />
                <button
                    type="button"
                    class="toggle"
                    on:click={() => (showPassword = !showPassword)}
                >{showPassword ? "Hide" : "Show"}</button>
            </div>
            {#if errors.password}<div class="error">{errors.password}</div>{/if}
        </label>

        <label class="field">
            <span>Confirm Password</span>
            <input
                type="password"
                bind:value={confirmPassword}
                placeholder="Confirm password"
            />
            {#if errors.confirmPassword}<div class="error">{errors.confirmPassword}</div>{/if}
        </label>

        <button class="submit" type="submit" disabled={loading}>
            {#if loading}<span class="spinner"></span> Processing...{:else}Register{/if}
        </button>

        <div class="links">
            <a href="/customer/login">Already have an account? Login</a>
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
