<script lang="ts">
    import { env } from "$env/dynamic/public";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import styles from "$lib/styles/header/Orders.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
    import { authStore } from "$lib/stores/AuthStore";

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

    let showAssignModal = $state(false);
    let selectedOrder: Order | null = null;
    let employees = $state([]);
    let selectedEmployee: string | null = null;

    // === Helper: Build URL ===
    function buildUrl() {
        const url = new URL(`${env.PUBLIC_API_URL}/orders`);
        url.searchParams.set("limit", String(pageSize));
        if (searchId) url.searchParams.set("search_id", searchId);
        if (searchName) url.searchParams.set("customer_name", searchName);

        return url;
    }

    onMount(() => {
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

    function openAssignModal(order: Order) {
        selectedOrder = order;
        showAssignModal = true;
        fetchEmployees();
    }

    async function fetchEmployees() {
        const token = localStorage.getItem("accessToken");

        const res = await fetch(
            `${env.PUBLIC_API_URL}/employees?role=EMPLOYEE`,
            {
                headers: { Authorization: `Bearer ${token}` },
            },
        );

        const data = await res.json();
        employees = data?.search_result || [];
    }

    async function handleAssignOrder() {
        if (!selectedEmployee || !selectedOrder) {
            message = "Vui lòng chọn nhân viên!";
            return;
        }

        const token = localStorage.getItem("accessToken");
        if (!token) {
            message = "Bạn chưa đăng nhập!";
            return;
        }

        try {
            const res = await fetch(
                `${env.PUBLIC_API_URL}/orders/${selectedOrder.id}/assign`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        order_id: selectedOrder?.id,
                        employee_id: selectedEmployee,
                    }),
                },
            );

            if (!res.ok) throw new Error("Assign failed");

            message = "Assigned successfully!";

            orders = orders.map((o) =>
                o.id === selectedOrder?.id
                    ? { ...o, assigned_employee_id: selectedEmployee }
                    : o,
            );
            fetchOrders();
            showAssignModal = false;
        } catch (err) {
            console.error(err);
            message = "Có lỗi xảy ra khi gán nhân viên";
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
            fetchOrders()
        } else {
            message = "Delete failed";
        }
    }

    function handleLogout() {
        localStorage.removeItem("accessToken");
        goto("/employees/login");
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
        <h1 style="font-family: system-ui, sans-serif;">Orders</h1>
        <div>
            <button onclick={handleLogout}>Logout</button>
        </div>
    </div>
    <TabNavigation is_admin={$authStore.role === "ADMIN"} />
</div>

<!-- SEARCH -->

<div class={styles.tableSearch}>
    <TextField
        name="id"
        title="ID"
        placeholder="Search ID"
        value={searchId}
        onValueChange={(v: string) => (searchId = v)}
    />

    <TextField
        name="customer_name"
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
    {:else if $authStore.role !== "ADMIN"}
        <div class={styles.forbiddenBox}>
            <h2>403 – Forbidden</h2>
            <p>You do not have permission to access this page.</p>
        </div>
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
                                disabled={order.status === "COMPLETED" ||
                                    order.status === "CANCELLED"}
                                class={styles.disabledButton}
                            >
                                Edit
                            </button>

                            <button
                                onclick={(e) => {
                                    e.stopPropagation();
                                    openAssignModal(order);
                                }}
                                disabled={order.status !== "PENDING"}
                                class={order.status !== "PENDING"
                                    ? styles.disabledButton
                                    : ""}
                            >
                                {order.status !== "PENDING"
                                    ? "Assigned"
                                    : "Assign"}
                            </button>
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
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>

        {#if showAssignModal && selectedOrder}
            <!-- Modal Backdrop -->
            <div class={styles.modalBackdrop}></div>

            <!-- Modal -->
            <div class={styles.modal}>
                <h2>Assign Order: {selectedOrder.id}</h2>
                <p>Customer: {selectedOrder.customer_name}</p>

                <label>Chọn nhân viên:</label>
                <select bind:value={selectedEmployee}>
                    <option value="" disabled selected>Chọn nhân viên</option>
                    {#each employees as emp}
                        <option value={emp.id}>{emp.employee_name}</option>
                    {/each}
                </select>

                <div class={styles.modalButtons}>
                    <button onclick={handleAssignOrder}> Assign </button>

                    <button
                        onclick={() => {
                            showAssignModal = false;
                        }}>Cancel</button
                    >
                </div>
            </div>
        {/if}

        <div class={styles.paginationControls}>
            <button disabled={page === 1} onclick={handlePrevPage}
                >Previous</button
            >
            <button
                disabled={page === Math.ceil(totalRecords / pageSize)}
                onclick={handleNextPage}>Next</button
            >
        </div>
    {/if}
</div>
