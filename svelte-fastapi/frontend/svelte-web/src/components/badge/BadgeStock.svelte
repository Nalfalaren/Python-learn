<script>
    let { stock = 0 } = $props();
</script>

<div class="card-badge">
    {#if stock === 0}
        <span class="badge sold-out">OUT OF STOCK</span>
    {:else if stock < 10}
        <span class="badge low-stock">Low Stock</span>
    {:else}
        <span class="badge in-stock">In Stock</span>
    {/if}
</div>

<style>
    .card-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        z-index: 10;
    }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge.sold-out {
        background: rgba(153, 153, 153, 0.9);
        color: white;
    }

    .badge.low-stock {
        background: rgba(239, 68, 68, 0.9);
        color: white;
    }

    .badge.in-stock {
        background: rgba(34, 197, 94, 0.9);
        color: white;
    }
</style>
