<script lang="ts">
    import { env } from "$env/dynamic/public";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import styles from "$lib/styles/header/Orders.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";

    interface OrderItem {
        id: string;
        order_id: string;
        product_name: string;
        qty: number;
        price: number;
        total: number;
        created_at: string;
    }

    let items: OrderItem[] = $state([]);
    let loading = $state(false);
    let message = $state("");
    let totalRecords = $state(0);

    let pageSize = 10;
    let page = 1;

    let searchProduct = $state("");
    let searchOrderId = $state("");

    function buildUrl() {
        const url = new URL(`${env.PUBLIC_API_URL}/order_items`);
        url.searchParams.set("limit", String(pageSize));
        url.searchParams.set("page", String(page));
        if (searchProduct) url.searchParams.set("product", searchProduct);
        if (searchOrderId) url.searchParams.set("order_id", searchOrderId);
        return url;
    }

    async function fetchItems() {
        loading = true;
        const token = localStorage.getItem("accessToken");
        try {
            const res = await fetch(buildUrl(), {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) throw new Error("Failed to fetch order items");

            const data = await res.json();
            console.log(data);
            totalRecords = data.items_count || 0;
            items = data.search_result || [];
        } catch (err) {
            console.error(err);
            message = "Failed to load order items";
        } finally {
            loading = false;
        }
    }

    async function handleDelete(id: string) {
        const token = localStorage.getItem("accessToken");

        const res = await fetch(`${env.PUBLIC_API_URL}/order-items/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) message = "Item deleted";
        else message = "Failed to delete";
    }

    function handleLogout() {
        localStorage.removeItem("accessToken");
        goto("/login");
    }

    function handleSearch() {
        page = 1;
        fetchItems();
    }

    function handlePrevPage() {
        if (page > 1) {
            page--;
            fetchItems();
        }
    }

    function handleNextPage() {
        if (page < Math.ceil(totalRecords / pageSize)) {
            page++;
            fetchItems();
        }
    }

    onMount(() => fetchItems());
</script>

<div class={styles.headerContainer}>
    <div class={styles.headerContent}>
        <h1>Order Items</h1>
        <div>
            <button onclick={handleLogout}>Logout</button>
        </div>
    </div>
    <TabNavigation />
</div>

<div class={styles.tableSearch}>
    <TextField
        title="Product"
        placeholder="Search Product Name"
        value={searchProduct}
        onValueChange={(v: string) => (searchProduct = v)}
    />

    <TextField
        title="Order ID"
        placeholder="Search Order ID"
        value={searchOrderId}
        onValueChange={(v: string) => (searchOrderId = v)}
    />

    <button onclick={handleSearch}>Search</button>
</div>

<div class={styles.tableContainer}>
    {#if loading}
        <p>Loading...</p>
    {:else if items.length === 0}
        <p>No Order Items found.</p>
    {:else}
        <table class={styles.table}>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Order ID</th>
                    <th>Product</th>
                    <th>Qty</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {#each items as item}
                    <tr onclick={() => goto(`/order-items/${item.id}`)}>
                        <td>{item.id}</td>
                        <td>{item.order_id}</td>
                        <td>{item.product_name}</td>
                        <td>{item.qty}</td>
                        <td>{item.price}đ</td>
                        <td>
                            <button
                                onclick={(e) => {
                                    e.stopPropagation();
                                    goto(`/order-items/${item.id}/edit`);
                                }}
                            >Edit</button>

                            <button
                                onclick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(item.id);
                                }}
                            >Delete</button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        <div class={styles.paginationControls}>
            <button disabled={page === 1} onclick={handlePrevPage}>Previous</button>

            <span>
                Page {page} / {Math.ceil(totalRecords / pageSize)}
            </span>

            <button
                disabled={page === Math.ceil(totalRecords / pageSize)}
                onclick={handleNextPage}
            >Next</button>
        </div>
    {/if}
</div>