<script lang="ts">
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import styles from "./tab-navigation.module.css";

    export let is_admin: boolean = false;

    let tabList = is_admin
        ? ["Employee", "Products", "Orders", "Order Items"]
        : ["Employee Orders"];

    $: currentPath = $page.url.pathname;
    
    $: chosenTab = tabList.find(tab => {
        const tabPath = tab.includes(" ")
            ? `/${tab.toLowerCase().replace(" ", "_")}`
            : `/${tab.toLowerCase()}`;
        return currentPath === tabPath;
    }) || tabList[0];

    const handleClick = (tabName: string) => {
        const path = tabName.includes(" ")
            ? `/${tabName.toLowerCase().replace(" ", "_")}`
            : `/${tabName.toLowerCase()}`;
        goto(path);
    };
</script>

{#if tabList.length > 0}
    <div class={styles.tabContainer}>
        {#each tabList as tabName}
            <button
                class={`${styles.tabButton} ${chosenTab === tabName ? styles.active : ""}`}
                on:click={() => handleClick(tabName)}
            >
                {tabName}
            </button>
        {/each}
    </div>
{/if}