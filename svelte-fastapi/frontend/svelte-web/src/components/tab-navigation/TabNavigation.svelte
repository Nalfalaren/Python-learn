<script lang="ts">
    import styles from "./tab-navigation.module.css";
    let tabList = ["Content", "Files", "Media"];
    let chosenTab = "Content";
    const handleClick = (tabListName: string) => {
        chosenTab = tabListName;
    };
</script>

<div class={styles.tabContainer}>
    {#each tabList as tabName}
        <div class={styles.tabElement}>
            <button onclick={() => handleClick(tabName)}>{tabName}</button>
        </div>
    {/each}
</div>
