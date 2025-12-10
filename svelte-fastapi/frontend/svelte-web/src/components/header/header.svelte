<script lang="ts">
  import UserMenu from "../../components/user-menu/UserMenu.svelte";
  import styles from "$lib/styles/header/employees.module.css";

  export let handleLogout: () => void = () => {};
  export let username: string = "";
</script>

<div class={styles.pageWrapper}>
  <div class={styles.headerContainer}>
    <div style="display: flex; justify-content: flex-end">
      <UserMenu username={username} signOut={handleLogout} />
    </div>
  </div>
</div>