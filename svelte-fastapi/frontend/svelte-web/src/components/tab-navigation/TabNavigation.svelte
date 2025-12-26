<script lang="ts">
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import styles from "./tab-navigation.module.css";
    import customer from "$lib/assets/customer.png";
    import employee from "$lib/assets/employee.png";
    import product from "$lib/assets/product.png";
    import order from "$lib/assets/order.png";
    import orderItem from "$lib/assets/order_item.png";


    const { is_admin } = $props();
    
 let tabList = is_admin
    ? [
        { tabName: "Employees", icon: employee },
        { tabName: "Customers", icon: customer },
        { tabName: "Products", icon: product },
        { tabName: "Orders", icon: order },
        { tabName: "Order Items", icon: orderItem },
      ]
    : [
        { tabName: "Employees", icon: employee },
        { tabName: "Employee Orders", icon: order },
      ];


    let currentPath = $derived($page.url.pathname);
    
    let chosenTab = $derived.by(() => {
        return tabList.find(tab => {
            const tabPath = tab.tabName.includes(" ")
                ? `/${tab.tabName.toLowerCase().replace(" ", "_")}`
                : `/${tab.tabName.toLowerCase()}`;
            return currentPath === tabPath;
        }) || tabList[0];
    });

    const handleClick = (tabName: string) => {
        const path = tabName.includes(" ")
            ? `/${tabName.toLowerCase().replace(" ", "_")}`
            : `/${tabName.toLowerCase()}`;
        goto(path);
    };
</script>

{#if tabList.length > 0}
    <div class={styles.tabContainer}>
        {#each tabList as tab}
            <button
                class={`${styles.tabButton} ${chosenTab.tabName === tab.tabName ? styles.active : ""}`}
                onclick={() => handleClick(tab.tabName)}
            >
                <img
                    src={tab.icon}
                    alt={tab.tabName}
                    class={styles.tabIcon}
                    style={"width: 30px; height: 30px"}
                />
                <span>{tab.tabName}</span>
            </button>
        {/each}
    </div>
{/if}
