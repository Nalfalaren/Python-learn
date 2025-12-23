<script lang="ts">
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import styles from "$lib/styles/header/orders.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
    import { adminAuthStore } from "$lib/stores/AuthAdmin";
    import { adminApi } from "../../hooks/apiFetch";
    import Header from "../../components/header/header.svelte";
    import ModalConfirm from "../../components/modal-confirm/ModalConfirm.svelte";
    import MessageModal from "../../components/modal-success/MessageModal.svelte";

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
    let employee_name = $state("");
    let isDeleteModalOpen = $state(false);
    let deletingItemId: string | null = $state(null);
    let isDeleteItem = $state(false);

    let pageSize = 10;
    let page = 1;

    let searchProduct = $state("");
    let searchOrderId = $state("");

    function buildUrl() {
        const url = new URL(`${import.meta.env.VITE_API_BASE_URL}/order_items`);
        url.searchParams.set("limit", String(pageSize));
        url.searchParams.set("page", String(page));
        if (searchProduct) url.searchParams.set("product", searchProduct);
        if (searchOrderId) url.searchParams.set("order_id", searchOrderId);
        return url;
    }

    async function fetchItems() {
        loading = true;
        try {
            const res = await adminApi(buildUrl());
            if (!res.ok) throw new Error("Failed to fetch order items");
            const data = await res.json();
            totalRecords = data.items_count || 0;
            items = data.search_result || [];
        } catch (err) {
            console.error(err);
            message = "Failed to load order items";
        } finally {
            loading = false;
        }
    }

    function handleLogout() {
        localStorage.removeItem("admin_access_token");
        localStorage.removeItem("admin_refresh_token");
        localStorage.removeItem("employee_name");
        goto("/employees/login");
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

    function openDeleteModal(id: string) {
        deletingItemId = id;
        isDeleteModalOpen = true;
    }

    function onCloseModal() {
        isDeleteModalOpen = false;
        isDeleteItem = false;
    }

    async function deleteItem() {
        if (!deletingItemId) return;

        try {
            const res = await adminApi(
                `${import.meta.env.VITE_API_BASE_URL}/order_items/${deletingItemId}`,
                { method: "DELETE" },
            );

            if (!res.ok) throw new Error("Delete failed");

            message = "Deleted successfully!";
            isDeleteItem = true;
            fetchItems();
        } catch (err) {
            console.error(err);
            message = "Unable to delete Order Item.";
            isDeleteItem = true;
        } finally {
            isDeleteModalOpen = false;
            deletingItemId = null;
        }
    }

    onMount(() => {
        fetchItems();
        employee_name = localStorage.getItem("employee_name") || "";
    });
</script>

<Header {handleLogout} username={employee_name} />
<div style="display: flex; min-height: 100vh">
    <TabNavigation is_admin={$adminAuthStore.role === "ADMIN"} />
    <div style="width: 100%; background: #f5f5f5; padding: 20px">
        <div>
            <span
                style="font-size: 20px; color: rgb(26 59 105); font-weight: 700"
                >Order Item</span
            >
        </div>
        <div class={styles.tableSearch}>
            <TextField
                name="product_name"
                title="Product"
                placeholder="Search Product Name"
                value={searchProduct}
                onValueChange={(v: string) => (searchProduct = v)}
            />

            <TextField
                name="order_id"
                title="Order ID"
                placeholder="Search Order ID"
                value={searchOrderId}
                onValueChange={(v: string) => (searchOrderId = v)}
            />

            <button
                onclick={handleSearch}
                style="background-color: white; border: 1px solid #d9d9d9; color: rgba(0, 0, 0, 0.88)"
                >Search</button
            >
        </div>

        <div class={styles.tableContainer}>
            {#if loading}
                <p>Loading...</p>
            {:else if $adminAuthStore.role !== "ADMIN"}
                <div class={styles.forbiddenBox}>
                    <h2>403 – Forbidden</h2>
                    <p>You do not have permission to access this page.</p>
                </div>
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
                            <th>Created At</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each items as item}
                            <tr>
                                <td>{item.id}</td>
                                <td>{item.order_id}</td>
                                <td>{item.product_name}</td>
                                <td>{item.qty}</td>
                                <td>{item.price}$</td>
                                <td>
                                    {new Date(item?.created_at).toLocaleString(
                                        "vi-VN",
                                        {
                                            timeZone: "Asia/Ho_Chi_Minh",
                                        },
                                    )}
                                </td>
                                <td>
                                    <button
                                        style="color: white; background: red; padding: 6px 10px; border-radius: 4px; cursor: pointer"
                                        onclick={(e) => {
                                            e.stopPropagation();
                                            openDeleteModal(item.id);
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
                    <button
                        disabled={page === Math.ceil(totalRecords / pageSize)}
                        onclick={handleNextPage}>Next</button
                    >
                </div>
            {/if}
        </div>
    </div>
    <ModalConfirm
        show={isDeleteModalOpen}
        message="Are you sure you want to delete this order item?"
        onConfirm={deleteItem}
        onCancel={() => (isDeleteModalOpen = false)}
    />
    <MessageModal show={isDeleteItem} {message} onClose={onCloseModal} />
</div>
