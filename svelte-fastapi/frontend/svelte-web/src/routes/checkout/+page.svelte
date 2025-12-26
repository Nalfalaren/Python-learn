<script lang="ts">
  import { goto } from "$app/navigation";
  import { CartStore } from "$lib/stores/CartStore";
  import { get } from "svelte/store";
  import { authCustomer } from "$lib/stores/AuthCustomer";
  import { clientApi } from "../../hooks/apiFetch";
  import MessageModal from "../../components/modal-success/MessageModal.svelte";

  let cart = $state(get(CartStore));

  // Subscribe to CartStore changes
  CartStore.subscribe((value) => {
    cart = value;
  });

  // Customer form
  let name = $state("");
  let email = $state("");
  let phone = $state("");
  let address = $state("");
  let message = $state("");
  let isCloseModal = $state(false);

  let total = $derived(cart.reduce((sum, i) => sum + i.price * i.quantity, 0));

  function increaseQuantity(itemId: number) {
    const updatedCart = cart.map((item) => {
      if (item.id === itemId && item.quantity < (item.stock ?? 99)) {
        return { ...item, quantity: item.quantity + 1 };
      }
      return item;
    });
    CartStore.set(updatedCart);
  }

  function decreaseQuantity(itemId: string) {
    const updatedCart = cart.map((item) => {
      if (item.id === itemId && item.quantity > 1) {
        return { ...item, quantity: item.quantity - 1 };
      }
      return item;
    });
    CartStore.set(updatedCart);
  }

  function updateQuantity(itemId: string, newQuantity: number) {
    const qty = Math.max(1, Math.min(newQuantity, 99));
    const updatedCart = cart.map((item) => {
      if (item.id === itemId) {
        return { ...item, quantity: qty };
      }
      return item;
    });
    CartStore.set(updatedCart);
  }

  function removeItem(itemId: string) {
    const updatedCart = cart.filter((item) => item.id !== itemId);
    CartStore.set(updatedCart);
  }

  async function handleCheckout() {
    if (!name || !email || !phone || !address) {
      message = "Please fill in all fields";
      isCloseModal = true;
      return;
    }
    let customer_id = $authCustomer.id;
    try {
      const payload = {
        customer: { customer_id, name, email, phone, address },
        cart: cart.map((i) => ({
          product_id: i.id,
          product_name: i.product_name,
          qty: i.quantity,
          price: i.price,
        })),
      };
      const token = localStorage.getItem("accessToken");
      const res = await clientApi(
        `${import.meta.env.VITE_API_BASE_URL}/checkout`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        },
      );

      if (res.ok) {
        message = "Order placed successfully!";
        isCloseModal = true;
        CartStore.set([]);
      } else {
        const error = await res.json();
        message = error.detail || "Failed to place order";
        isCloseModal = true;
      }
    } catch (e) {
      console.error(e);
      message = "An error occurred. Please try again.";
      isCloseModal = true;
    }
  }

  function onClose() {
    isCloseModal = false;
    if (message.includes("successfully")) {
      goto("/");
    }
  }
</script>

<div class="checkout-wrapper">
  <h1 class="title">Checkout</h1>

  <div class="grid">
    <!-- LEFT: CART ITEMS -->
    <section class="card cart">
      <h2>Shopping Cart</h2>

      {#if cart.length === 0}
        <p class="empty">Your cart is currently empty.</p>
      {:else}
        <div class="cart-header">
  <div class="header-left">Product</div>
  <div class="header-right">
    <span>Price</span>
    <span>Quantity</span>
    <span>Total</span>
    <span style="width: 24px;"></span> <!-- Spacer for remove button -->
  </div>
</div>

<ul class="cart-list">
  {#each cart as item (item.id)}
    <li class="item">
      <div class="item-content">
        <a href={`/products/details/${item.id}`} class="info">
          <strong class="product-name">{item.product_name}</strong>
        </a>
      </div>

      <div class="item-right">
        <span class="unit-price">${Number(item.price).toFixed(2).replace(/\.00$/, "")}</span>
        <div class="quantity-controls">
          <button
            onclick={() => decreaseQuantity(item.id)}
            class="qty-btn"
            disabled={item.quantity <= 1}
            aria-label="Decrease quantity">−</button
          >
          <input
            type="number"
            value={item.quantity}
            oninput={(e) =>
              updateQuantity(
                item.id,
                parseInt(e.currentTarget.value) || 1,
              )}
            min="1"
            max={item.stock ?? 99}
            class="qty-input"
          />
          <button
            onclick={() => increaseQuantity(item.id)}
            class="qty-btn"
            disabled={item.quantity >= (item.stock ?? 99)}
            aria-label="Increase quantity">+</button
          >
        </div>
        <strong class="price">
          ${Number(item.price * item.quantity)
            .toFixed(2)
            .replace(/\.00$/, "")}
        </strong>
        <button
          class="remove-btn"
          onclick={() => removeItem(item.id)}
          aria-label="Remove item">×</button
        >
      </div>
    </li>
  {/each}
</ul>

        <div class="total-box">
          <span>Total</span>
          <strong class="total">
            ${Number(total).toFixed(2).replace(/\.00$/, "")}
          </strong>
        </div>
      {/if}
    </section>

    <!-- RIGHT: CUSTOMER FORM -->
    <section class="card form">
      <h2>Shipping Information</h2>

      <div class="field">
        <label>Full Name</label>
        <input bind:value={name} placeholder="Ex: John Doe" />
      </div>

      <div class="field">
        <label>Email</label>
        <input bind:value={email} placeholder="you@example.com" type="email" />
      </div>

      <div class="field">
        <label>Phone Number</label>
        <input bind:value={phone} placeholder="0123 456 789" type="tel" />
      </div>

      <div class="field">
        <label>Shipping Address</label>
        <textarea
          bind:value={address}
          placeholder="House number, street, ward, district, city"
        ></textarea>
      </div>

      <button class="btn" onclick={handleCheckout} disabled={cart.length === 0}>
        Place Order
      </button>
    </section>
  </div>
</div>

<MessageModal {message} {onClose} show={isCloseModal} />

<style>
  /* PAGE LAYOUT */
  .checkout-wrapper {
    max-width: 1100px;
    margin: 40px auto;
    padding: 0 20px;
  }

  .title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 25px;
    text-align: center;
    color: #222;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  /* CART HEADER */
.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right span:nth-child(1) {
  width: 80px;
  text-align: center;
}

.header-right span:nth-child(2) {
  width: 140px;
  text-align: center;
}

.header-right span:nth-child(3) {
  width: 80px;
  text-align: right;
}

@media (max-width: 768px) {
  .cart-header {
    display: none;
  }
}

  /* CARD BASE STYLE */
  .card {
    background: #fff;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
    transition: 0.25s ease;
  }

  .card:hover {
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08);
  }

  /* TITLES */
  h2 {
    margin-bottom: 18px;
    font-size: 22px;
    font-weight: 600;
    color: #111;
  }

  /* EMPTY STATE */
  .empty {
    padding: 20px;
    background: #f9fafb;
    border-radius: 10px;
    text-align: center;
    color: #666;
  }

  /* CART LIST */
  .cart-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid #f1f1f1;
    gap: 16px;
  }

  .item:last-child {
    border-bottom: none;
  }

  .item-content {
    flex: 1;
    display: flex;
    flex-direction: row;
    gap: 12px;
  }

  .info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-decoration: none;
    color: black;
  }

  .product-name, .unit-price {
    font-size: 16px;
    color: #111;
  }

  .item-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .price {
    font-size: 18px;
    color: #111;
    font-weight: 600;
  }

  /* QUANTITY CONTROLS */
  .quantity-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f8f9fa;
    padding: 6px;
    border-radius: 8px;
    width: fit-content;
  }

  .qty-btn {
    width: 32px;
    height: 32px;
    border: 1px solid #cbd5e1;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    color: #333;
  }

  .qty-btn:hover:not(:disabled) {
    background: #007bff;
    color: white;
    border-color: #007bff;
  }

  .qty-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .qty-input {
    width: 60px;
    height: 32px;
    text-align: center;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 15px;
    font-weight: 600;
    padding: 0;
    background: white;
  }

  .qty-input:focus {
    border-color: #007bff;
    outline: none;
  }

  /* REMOVE BUTTON */
  .remove-btn {
    width: 24px;
    height: 24px;
    border: none;
    background: #fee;
    color: #e11d48;
    border-radius: 50%;
    cursor: pointer;
    font-size: 20px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .remove-btn:hover {
    background: #e11d48;
    color: white;
  }

  /* TOTAL PRICE BOX */
  .total-box {
    margin-top: 18px;
    padding-top: 14px;
    border-top: 2px solid #ddd;
    display: flex;
    justify-content: space-between;
    font-size: 18px;
  }

  .total {
    font-size: 24px;
    color: #007bff;
    font-weight: 700;
  }

  /* FORM INPUTS */
  .field {
    margin-bottom: 18px;
  }

  .field label {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin-bottom: 6px;
    display: inline-block;
  }

  input,
  textarea {
    width: 95%;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #cbd5e1;
    font-size: 15px;
    transition: 0.2s;
    background: #fafafa;
  }

  input:focus,
  textarea:focus {
    border-color: #007bff;
    background: #fff;
    outline: none;
  }

  textarea {
    min-height: 90px;
    resize: vertical;
  }

  /* BUTTON */
  .btn {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, #007bff, #0063d8);
    border: none;
    color: #fff;
    border-radius: 12px;
    font-size: 17px;
    cursor: pointer;
    margin-top: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: 0.25s ease;
  }

  .btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #0063d8, #004fb5);
    transform: translateY(-1px);
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  @media (max-width: 768px) {
    .grid {
      grid-template-columns: 1fr;
    }

    .item {
      flex-direction: column;
      align-items: flex-start;
    }

    .item-right {
      width: 100%;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
    }
  }
</style>
