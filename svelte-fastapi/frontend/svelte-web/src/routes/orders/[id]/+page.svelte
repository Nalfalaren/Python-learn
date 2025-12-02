<script lang="ts">
    import { onMount } from "svelte";
    import styles from "$lib/styles/detail/order-detail.module.css";
    import { goto } from "$app/navigation";

    let orderId: string;
    export let params;
    interface OrderDetail {
        order: {
            id: string;
            customer_name: string;
            email: string;
            phone: string;
            address: string;
            status: string;
            created_at: string;
            assigned_to: string | null
            total: number;
        };
        items: {
            product_id: string;
            product_name: string;
            qty: number;
            price: number;
        }[];
    }
    let orderInformation: OrderDetail = {
        order: {
            id: "",
            customer_name: "",
            email: "",
            phone: "",
            address: "",
            status: "",
            created_at: "",
            assigned_to: "",
            total: 0,
        },
        items: [],
    };

    orderId = params.id;

    onMount(async () => {
        const token = localStorage.getItem("accessToken");
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/orders/${orderId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });

        if (res.ok) {
            orderInformation = await res.json();
        } else {
            alert("❌ Failed to load order details");
            goto("/orders");
        }
    });

    function goBack() {
        goto("/orders");
    }
</script>

<div class={styles.wrapper}>
    <div class={styles.card}>
        <h2>Order Details</h2>
        <p class={styles.subtitle}>
            View full information about customer order.
        </p>

        <div class={styles.info}>
            <div class={styles.row}>
                <span class={styles.label}>Customer Name:</span>
                <span class={styles.value}
                    >{orderInformation?.order?.customer_name}</span
                >
            </div>

            <div class={styles.row}>
                <span class={styles.label}>Email:</span>
                <span class={styles.value}
                    >{orderInformation?.order?.email}</span
                >
            </div>

            <div class={styles.row}>
                <span class={styles.label}>Phone:</span>
                <span class={styles.value}
                    >{orderInformation?.order?.phone}</span
                >
            </div>

            <div class={styles.row}>
                <span class={styles.label}>Status:</span>
                <span class={`${styles.badge}`}>
                    {orderInformation?.order?.status}
                </span>
            </div>

            {#if orderInformation?.order.created_at}
                <div class={styles.row}>
                    <span class={styles.label}>Created At:</span>
                    <span class={styles.value}>
                        {new Date(
                            orderInformation?.order.created_at,
                        ).toLocaleString()}
                    </span>
                </div>
            {/if}

            <div class={styles.row}>
                <span class={styles.label}>Assigned To:</span>
                <span class={styles.value}>
                    {#if orderInformation?.order.assigned_to}
                        {orderInformation?.order.assigned_to}
                    {:else}
                        <p>N/A</p>
                    {/if}
                </span>
            </div>
        </div>
        <h2>Order Items</h2>
        <p class={styles.subtitle}>
            View full information about customer order items.
        </p>
        <div class={styles.orderItemsContainer}>
            {#if orderInformation?.items?.length > 0}
                <table class={styles.itemsTable}>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Qty</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each orderInformation?.items as item}
                            <tr>
                                <td>{item.product_name}</td>
                                <td>{item.qty}</td>
                                <td>{item.price}$</td>
                                <td>{item.qty * item.price}$</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <p>No items in this order.</p>
            {/if}
        </div>
        <button on:click={goBack} class={styles.button}>⬅ Back to List</button>
    </div>
</div>
