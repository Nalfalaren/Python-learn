<script lang="ts">
    import { env } from "$env/dynamic/public";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import styles from "$lib/styles/header/Orders.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";

    interface Order {
        id: string;
        customer_name: string;
        email: string;
        phone: string;
        address: string;
        status: string;
        created_at: string;
        total: number;
        items: string[];
    }

    // === Reactive States ===
    let orders: Order[] = $state([]);
    let loading = $state(false);
    let message = $state("");
    let totalRecords = $state(0);

    // pagination states
    let pageSize = 10;
    let page = 1;

    // search
    let searchId = $state("");
    let searchName = $state("");

    // === Helper: Build URL ===
    function buildUrl() {
        const url = new URL(`${env.PUBLIC_API_URL}/orders`);
        url.searchParams.set("limit", String(pageSize));
        if (searchId) url.searchParams.set("search_id", searchId);
        if (searchName) url.searchParams.set("order_name", searchName);

        return url;
    }

    console.log("A: component loaded");

onMount(() => {
    console.log("B: onMount triggered");
    console.log("C: API URL = ", `${env.PUBLIC_API_URL}/orders`);
    fetchOrders();
});

    // === Fetch Orders ===
    async function fetchOrders() {
        loading = true;
        const token = localStorage.getItem("accessToken");

        try {
            const res = await fetch(buildUrl(), {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) throw new Error("Failed to fetch Orders");

            const data = await res.json();
            totalRecords = data.orders_count || 0;
            orders = data.search_result || [];
        } catch (err) {
            console.error(err);
            message = "Failed to load Orders";
        } finally {
            loading = false;
        }
    }

    // === Delete ===
    async function handleDelete(id: string) {
        const token = localStorage.getItem("accessToken");

        const res = await fetch(`${env.PUBLIC_API_URL}/orders/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) {
            message = "Order deleted";
        } else {
            message = "Delete failed";
        }
    }

    function handleLogout() {
        localStorage.removeItem("accessToken");
        goto("/login");
    }

    function handleSearch() {
        page = 1;
        fetchOrders();
    }

    function handlePrevPage() {
        if (page > 1) {
            page--;
            fetchOrders();
        }
    }

    function handleNextPage() {
        if (page < Math.ceil(totalRecords / pageSize)) {
            page++;
            fetchOrders();
        }
    }

    onMount(() => fetchOrders());
</script>

<!-- HEADER -->

<div class={styles.headerContainer}>
    <div class={styles.headerContent}>
        <h1>Orders</h1>
        <div>
            <button onclick={handleLogout}>Logout</button>
        </div>
    </div>
    <TabNavigation />
</div>

<!-- SEARCH -->

<div class={styles.tableSearch}>
    <TextField
        title="ID"
        placeholder="Search ID"
        value={searchId}
        onValueChange={(v: string) => (searchId = v)}
    />

    <TextField
        title="Customer Name"
        placeholder="Search Customer Name"
        value={searchName}
        onValueChange={(v: string) => (searchName = v)}
    />

    <button onclick={handleSearch}>Search</button>
</div>

<!-- TABLE -->

<div class={styles.tableContainer}>
    {#if loading}
        <p>Loading...</p>
    {:else if orders.length === 0}
        <p>No Orders found.</p>
    {:else}
        <table class={styles.table}>
            <thead>
                <tr>
                    <th>ID</th> <th>Customer Name</th> <th>Email</th>
                    <th>Phone</th> <th>Address</th> <th>Order Total</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {#each orders as order}
                    <tr onclick={() => goto(`/orders/${order.id}`)}>
                        <td>{order.id}</td>
                        <td>{order.customer_name}</td>
                        <td>{order.email}</td>
                        <td>{order.phone}</td>
                        <td>{order.address}</td>
                        <td>{order.total}đ</td>
                        <td>{order.status.toUpperCase()}</td>
                        <td>
                            <button
                                onclick={(e) => {
                                    e.stopPropagation();
                                    goto(`/orders/${order.id}/edit`);
                                }}
                            >
                                Edit
                            </button>

                            <button
                                onclick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(order.id);
                                }}
                            >
                                Delete
                            </button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        <div class={styles.paginationControls}>
            <button disabled={page === 1} onclick={handlePrevPage}
                >Previous</button
            >
            <span>Page {page} / {Math.ceil(totalRecords / pageSize)}</span>
            <button
                disabled={page === Math.ceil(totalRecords / pageSize)}
                onclick={handleNextPage}>Next</button
            >
        </div>
    {/if}
</div>
