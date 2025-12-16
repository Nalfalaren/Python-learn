<script lang="ts">
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import styles from "$lib/styles/header/orders.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
    import { adminAuthStore } from "$lib/stores/AuthStore";
    import { adminApi } from "../../hooks/apiFetch";
    import MessageModal from "../../components/modal-success/MessageModal.svelte";
    import Header from "../../components/header/header.svelte";

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

    let orders: Order[] = $state([]);
    let loading = $state(false);
    let message = $state("");
    let employee_name = $state("")
    let totalRecords = $state(0);

    let pageSize = 10;
    let page = 1;

    let searchId = $state("");
    let searchName = $state("");

    let showAssignModal = $state(false);
    let selectedOrder: Order | null = null;
    let employees = $state([]);
    let selectedEmployee: string | null = null;

    // message modal
    let showMessageModal = $state(false);
    let messageType: "success" | "error" = "success";

    function showMessage(msg: string, type: "success" | "error" = "success") {
        message = msg;
        messageType = type;
        showMessageModal = true;

        setTimeout(() => {
            showMessageModal = false;
        }, 2500);
    }

    function buildUrl() {
        const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/orders`);
        url.searchParams.set("limit", String(pageSize));
        if (searchId) url.searchParams.set("search_id", searchId);
        if (searchName) url.searchParams.set("customer_name", searchName);
        return url;
    }

    async function fetchOrders() {
        loading = true;
        try {
            const res = await adminApi(buildUrl());

            if (!res.ok) throw new Error("Failed to fetch");

            const data = await res.json();
            totalRecords = data.orders_count || 0;
            orders = data.search_result || [];
        } catch (err) {
            showMessage("Failed to load orders", "error");
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
        const res = await adminApi(
            `${import.meta.env.VITE_API_BASE_URL}/employees?role=EMPLOYEE`,
        );

        const data = await res.json();
        employees = data?.search_result || [];
    }

    async function handleAssignOrder() {
        if (!selectedEmployee)
            return showMessage("Please choose employee", "error");

        try {
            const res = await adminApi(
                `${import.meta.env.VITE_API_BASE_URL}/orders/${selectedOrder!.id}/assign`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        order_id: selectedOrder!.id,
                        employee_id: selectedEmployee,
                    }),
                },
            );

            if (!res.ok) return showMessage("Assign failed", "error");

            showMessage("Assigned successfully!", "success");
            showAssignModal = false;
            fetchOrders();
        } catch {
            showMessage("Error assigning employee", "error");
        }
    }

    async function handleDelete(id: string) {
        const res = await adminApi(
            `${import.meta.env.VITE_API_BASE_URL}/orders/${id}`,
            {
                method: "DELETE",
            },
        );

        if (res.ok) {
            showMessage("Order deleted!", "success");
            fetchOrders();
        } else {
            showMessage("Delete failed", "error");
        }
    }

    function handleLogout() {
        localStorage.removeItem("admin_access_token");
        localStorage.removeItem("admin_refresh_token");
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

    onMount(() => {
        fetchOrders()
        employee_name = localStorage.getItem("employee_name")
    });
</script>

<!-- HEADER -->
<Header {handleLogout} username={employee_name || ""} />
<div style="display: flex; min-height: 100vh">
    <TabNavigation is_admin={$adminAuthStore.role === "ADMIN"} />
    <div style="width: 100%; background: #f5f5f5; padding: 20px">
        <div>
            <span
                style="font-size: 20px; color: rgb(26 59 105); font-weight: 700"
                >Orders</span
            >
        </div>
        <!-- SEARCH -->
        <div class={styles.tableSearch}>
            <TextField
                name="id"
                title="ID"
                placeholder="Search ID"
                value={searchId}
                onValueChange={(v) => (searchId = v)}
            />

            <TextField
                name="customer_name"
                title="Customer Name"
                placeholder="Search Customer Name"
                value={searchName}
                onValueChange={(v) => (searchName = v)}
            />

            <button
                onclick={handleSearch}
                style="background-color: white; border: 1px solid #d9d9d9; color: rgba(0, 0, 0, 0.88)"
                >Search</button
            >
        </div>

        <!-- TABLE -->
        <div class={styles.tableContainer}>
            {#if loading}
                <p>Loading...</p>
            {:else if $adminAuthStore.role !== "ADMIN"}
                <p>403 Forbidden</p>
            {:else if orders.length === 0}
                <p>No Orders found.</p>
            {:else}
                <table class={styles.table}>
                    <thead>
                        <tr>
                            <th>ID</th><th>Name</th><th>Email</th>
                            <th>Phone</th><th>Address</th><th>Total</th>
                            <th>Status</th><th>Actions</th>
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
                                <td>{order.total}$</td>
                                <td>{order.status.toUpperCase()}</td>
                                <td>
                                    <button
                                        onclick={(e) => {
                                            e.stopPropagation();
                                            goto(`/orders/${order.id}/edit`);
                                        }}
                                        disabled={order.status ===
                                            "COMPLETED" ||
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
                                        disabled={order.status !==
                                            "COMPLETED" &&
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
                            <option value="" disabled selected
                                >Chọn nhân viên</option
                            >
                            {#each employees as emp}
                                <option value={emp.id}
                                    >{emp.employee_name}</option
                                >
                            {/each}
                        </select>

                        <div class={styles.modalButtons}>
                            <button onclick={handleAssignOrder}>
                                Assign
                            </button>

                            <button
                                onclick={() => {
                                    showAssignModal = false;
                                }}>Cancel</button
                            >
                        </div>
                    </div>
                {/if}

                <!-- Pagination -->
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
    </div>
</div>

<!-- MESSAGE MODAL -->
<MessageModal show={showMessageModal} {message} type={messageType} />
