<script lang="ts">
    import { cart } from "$lib/stores/CartStore";
    import styles from "$lib/styles/landing/landing.module.css";
    export let showAddToCardListModal: boolean = false;
    export let closeCartList: () => void = () => {};
    export let isLoggedIn: boolean = false;
    export let cartItems: any = [];
    export let shoppingCartImage: string = "";
    export let redirectToLogin: () => void = () => {};

    function deleteCart(id: string) {
        cart.removeItem(id);
    }
</script>

{#if showAddToCardListModal}
    <div
        class={styles.modalBackdrop}
        role="button"
        tabindex="0"
        aria-label="Close cart dialog"
        onkeydown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
                closeCartList();
            }
        }}
    >
        {#if isLoggedIn}
            <div
                class="{styles.modal} {styles.modalCart}"
                role="dialog"
                aria-modal="true"
                aria-labelledby="cart-dialog-title"
            >
                <button
                    type="button"
                    class={styles.modalClose}
                    aria-label="Close"
                    onclick={closeCartList}
                >
                    ×
                </button>

                <h2 id="cart-dialog-title" class={styles.modalTitle}>
                    Your Shopping Cart
                </h2>

                {#if cartItems.length === 0}
                    <div class={styles.emptyCart}>
                        <div class={styles.emptyIcon}>
                            <img src={shoppingCartImage} alt="cart_img" />
                        </div>
                        <p>Your cart is empty</p>
                        <button
                            type="button"
                            class={styles.btnPrimaryFull}
                            onclick={closeCartList}
                        >
                            Continue Shopping
                        </button>
                    </div>
                {:else}
                    <div class={styles.cartItems}>
                        {#each cartItems as item}
                            <div class={styles.cartItem}>
                                <img src={item.imgList[0].url} alt={item.product_name} />

                                <div class={styles.cartItemDetails}>
                                    <h4>{item.product_name}</h4>
                                    <div class={styles.cartItemMeta}>
                                        {item.category} • ${item.price}
                                    </div>
                                    <div class={styles.cartItemQuantity}>
                                        Qty: {item.quantity}
                                    </div>
                                </div>

                                <div class={styles.cartItemActions}>
                                    <div class={styles.cartItemPrice}>
                                        ${Number(
                                            (
                                                item.price * item.quantity
                                            ).toFixed(2),
                                        )}
                                    </div>
                                    <button
                                        type="button"
                                        class={styles.removeBtn}
                                        aria-label="Remove item"
                                        onclick={(e) => {
                                        e.stopPropagation()
                                        deleteCart(item.id!)
                                    }}
                                    >
                                        Remove
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>
                    <div class={styles.cartTotal}>
                        <div class="{styles.totalRow} {styles.totalFinal}">
                            <span>Total:</span>
                            <span>
                                ${Number(cart.getTotalPrice().toFixed(2))}
                            </span>
                        </div>
                    </div>

                    <div class={styles.cartActions}>
                        <button
                            type="button"
                            class={styles.btnSecondaryFull}
                            onclick={closeCartList}
                        >
                            Continue Shopping
                        </button>

                        <a class={styles.btnPrimaryFull} href="/checkout">
                            Proceed to Checkout
                        </a>
                    </div>
                {/if}
            </div>
        {:else}
            <div
                class="{styles.modal} {styles.modalSm}"
                role="dialog"
                aria-modal="true"
                aria-labelledby="login-required-title"
            >
                <button
                    type="button"
                    class={styles.modalClose}
                    aria-label="Close"
                    onclick={closeCartList}
                >
                    ×
                </button>

                <div class={styles.loginRequired}>
                    <div class={styles.loginIcon}>🔒</div>

                    <h3 id="login-required-title">Login Required</h3>

                    <p>
                        Please log in to view your cart and complete your
                        purchase.
                    </p>

                    <div class={styles.modalActions}>
                        <button
                            type="button"
                            class={styles.btnPrimaryFull}
                            onclick={redirectToLogin}
                        >
                            Login
                        </button>

                        <button
                            type="button"
                            class={styles.btnSecondaryFull}
                            onclick={closeCartList}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    </div>
{/if}
