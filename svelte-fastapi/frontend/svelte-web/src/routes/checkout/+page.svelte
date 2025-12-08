<script lang="ts">
  import { goto } from "$app/navigation";
  import { CartStore } from "$lib/stores/CartStore";
  import { get } from "svelte/store";
  import { authCustomer } from "$lib/stores/AuthCustomer"
  import { clientApi } from "../../hooks/apiFetch";

  let cart = get(CartStore);

  // Customer form
  let name = "";
  let email = "";
  let phone = "";
  let address = "";

  $: total = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);
  async function handleCheckout() {
    if (!name || !email || !phone || !address) {
      alert("Please fill in all fields");
      return;
    }
    let customer_id = $authCustomer.id
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
      const token = localStorage.getItem('accessToken')
      const res = await clientApi(`${import.meta.env.VITE_API_BASE_URL}/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        alert("Order placed successfully!");
        CartStore.set([]);
        goto("/");
      } else {
        const error = await res.json()
        alert(error.detail || "Failed to place order");
      }
    } catch (e) {
      console.error(e);
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
        <ul class="cart-list">
          {#each cart as item}
            <li class="item">
              <div class="info">
                <strong>{item.product_name}</strong>
                <span class="qty">x{item.quantity}</span>
              </div>

              <strong class="price">{Number(item.price * item.quantity).toFixed(2).replace(/\.00$/, "") + "$"}</strong>
            </li>
          {/each}
        </ul>

        <div class="total-box">
          <span>Total</span>
          <strong class="total">{Number(total).toFixed(2).replace(/\.00$/, "") + "$"}</strong>
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
        <input bind:value={email} placeholder="you@example.com" />
      </div>

      <div class="field">
        <label>Phone Number</label>
        <input bind:value={phone} placeholder="0123 456 789" />
      </div>

      <div class="field">
        <label>Shipping Address</label>
        <textarea
          bind:value={address}
          placeholder="House number, street, ward, district, city"
        ></textarea>
      </div>

      <button class="btn" on:click={handleCheckout}>Place Order</button>
    </section>
  </div>
</div>

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
    padding: 14px 0;
    border-bottom: 1px solid #f1f1f1;
  }

  .item:last-child {
    border-bottom: none;
  }

  .info {
    display: flex;
    flex-direction: column;
  }

  .qty {
    font-size: 14px;
    color: #777;
  }

  .price {
    font-size: 16px;
    color: #111;
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
    font-size: 22px;
    color: #007bff;
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
    width: 100%;
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

  .btn:hover {
    background: linear-gradient(135deg, #0063d8, #004fb5);
    transform: translateY(-1px);
  }

  @media (max-width: 768px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>
