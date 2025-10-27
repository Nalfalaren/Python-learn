<script lang="ts">
  import styles from "$lib/styles/register/Register.module.css";
  import { env } from "$env/dynamic/public";
  import { goto } from "$app/navigation";

  // Form state
  let employee_name: string = "";
  let role: string = "";
  let email: string = "";
  let is_active: boolean = true;
  let message: string = "";

  async function handleSubmit(e?: Event) {
    e?.preventDefault();

    if (!employee_name.trim() || !email.trim()) {
      alert("Please enter both employee name and email");
      return;
    }

    const payload = {
      employee_name: employee_name.trim(),
      role: role.trim(),
      email: email.trim(),
      is_active: is_active ? 1 : 0,
    };

    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch(`${env.PUBLIC_API_URL}/employees`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || "Failed to create employee");
      }

      const data = await res.json();
      message = "✅ Employee created successfully!";
      console.log("Employee created:", data);

      // reset form
      employee_name = "";
      role = "";
      email = "";
      is_active = true;

      // optional redirect
      goto("/employee");
    } catch (err) {
      console.error("Error creating employee:", err);
      message = "❌ Failed to create employee — check console for details";
    }
  }
</script>

<main class={styles.container}>
  <h1 class={styles.title}>Register Employee</h1>

  <form class={styles.form} on:submit|preventDefault={handleSubmit}>
    <label class={styles.field}>
      <span class={styles.label}>Employee Name</span>
      <input
        class={styles.input}
        type="text"
        bind:value={employee_name}
        placeholder="Enter employee name"
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Role</span>
      <input
        class={styles.input}
        type="text"
        bind:value={role}
        placeholder="Enter employee role"
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Email</span>
      <input
        class={styles.input}
        type="email"
        bind:value={email}
        placeholder="Enter employee email"
        required
      />
    </label>

    <label class={styles.field}>
      <span class={styles.label}>Active</span>
      <input
        type="checkbox"
        bind:checked={is_active}
        class={styles.checkbox}
      />
    </label>

    <div class={styles.actions}>
      <button type="submit" class={styles.button}>Create</button>
      <button
        type="button"
        class={styles.secondary}
        on:click={() => {
          employee_name = "";
          role = "";
          email = "";
          is_active = true;
        }}
      >
        Reset
      </button>
    </div>
  </form>

  {#if message}
    <p class={styles.message}>{message}</p>
  {/if}
</main>
