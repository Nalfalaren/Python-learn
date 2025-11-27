<script lang="ts">
    import { goto } from "$app/navigation";
    import styles from "./tab-navigation.module.css";
    let tabList = ["Employee", "Products", "Orders", "Order Items"];
    let chosenTab = "Content";
    const handleClick = (tabListName: string) => {
        chosenTab = tabListName;
        goto(`/${tabListName.toLowerCase()}`)
    };
</script>

<div class={styles.tabContainer}>
    {#each tabList as tabName}
        <div class={styles.tabElement}>
            <button onclick={() => handleClick(tabName)}>{tabName}</button>
        </div>
    {/each}
</div>
