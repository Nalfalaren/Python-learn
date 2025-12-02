<script lang="ts">
    import { env } from "$env/dynamic/public";
    import { onMount } from "svelte";
    import styles from "$lib/styles/header/orders.module.css";
    import { authStore } from "$lib/stores/AuthStore";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
    import TextField from "../../components/input/TextField.svelte";
    import { goto } from "$app/navigation";

    interface Order {
        id: string;
        customer_name: string;
        email: string;
        phone: string;
        address: string;
        status: string;
        created_at: string;
        employee_id: string;
        total: number;
        items: string[];
    }

    let orders: Order[] = [];
    let loading = false;
    let message = "";
    let totalRecords = 0;

    // Pagination
    let pageSize = 10;
    let page = 1;

    // Search
    let searchId = "";
    let searchName = "";

    // Build URL
    function buildUrl() {
        const url = new URL(`${env.PUBLIC_API_URL}/orders`);
        url.searchParams.set("limit", String(pageSize));
        url.searchParams.set("page", String(page));
        url.searchParams.set("employee_id", String($authStore.id));

        if (searchId) url.searchParams.set("search_id", searchId);
        if (searchName) url.searchParams.set("customer_name", searchName);

        return url;
    }

    async function fetchOrders() {
        loading = true;
        const token = localStorage.getItem("accessToken");
        if (!token) {
            message = "Bạn chưa đăng nhập!";
            loading = false;
            return;
        }

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

    function handleSearch() {
        page = 1;
        fetchOrders();
    }

    onMount(() => fetchOrders());
</script>

<div class={styles.headerContainer}>
    <div class={styles.headerContent}>
        <div>
            <h1 style="font-family: system-ui, sans-serif;">Customer Orders</h1>
        </div>
        <div>
            <button onclick={() => authStore.logout()}>Logout</button>
        </div>
    </div>
    <TabNavigation is_admin={$authStore.role === "ADMIN"} />
</div>

<!-- Search -->
<div class={styles.tableSearch}>
    <div class={styles.tableSearchInput}>
        <TextField
            name="id"
            title="ID"
            placeholder="Search ID"
            value={searchId}
            onValueChange={(v) => (searchId = v)}
        />
    </div>

    <div class={styles.tableSearchInput}>
        <TextField
            name="customer_name"
            title="Customer Name"
            placeholder="Search Name"
            value={searchName}
            onValueChange={(v) => (searchName = v)}
        />
    </div>

    <button onclick={handleSearch}>Search</button>
</div>

<!-- Table -->
<div class={styles.tableContainer}>
    {#if loading}
        <p>Loading...</p>
    {:else if orders.length === 0}
        <p>No Orders found.</p>
    {:else}
        <table class={styles.table}>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Customer Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Address</th>
                    <th>Total</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {#each orders as order}
                    <tr>
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
                                disabled={order.status === "COMPLETED" ||
                                    order.status === "CANCELLED"}
                                class={styles.disabledButton}
                            >
                                Edit
                            </button>
                            {#if $authStore.role == "ADMIN"}
                            <button
                                onclick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(order.id);
                                }}
                                disabled={order.status !== "COMPLETED" &&
                                    order.status !== "CANCELLED"}
                                class={styles.disabledButton}
                            >
                                Delete
                            </button>
                            {/if}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        <!-- Pagination -->
        <div class={styles.paginationControls}>
            <button onclick={handlePrevPage} disabled={page === 1}
                >Previous</button
            >
            <button
                onclick={handleNextPage}
                disabled={page === Math.ceil(totalRecords / pageSize)}
                >Next</button
            >
        </div>
    {/if}
</div>
