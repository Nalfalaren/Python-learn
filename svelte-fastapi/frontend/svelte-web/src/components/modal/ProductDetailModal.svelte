<script lang="ts">
  export let product: any = null;
  export let onClose: () => void;
</script>

{#if product}
  <div class="overlay">
    <div class="modal">
      <button class="close-btn" on:click={onClose}>✕</button>

      <img src={product.image} alt={product.name} class="image" />

      <h2 class="title">{product.name}</h2>
      <p class="desc">{product.description}</p>
      <p class="price">{product.price.toLocaleString()} VND</p>

      <button class="buy-btn" on:click={() => window.location.href = `/checkout/${product.id}`}>
        Mua ngay
      </button>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    width: 400px;
    background: white;
    padding: 20px;
    border-radius: 12px;
    position: relative;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    animation: fadeIn 0.2s ease-out;
  }

  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: #555;
  }

  .image {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 15px;
  }

  .title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .desc {
    color: #666;
    margin-bottom: 8px;
    font-size: 14px;
  }

  .price {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 20px;
  }

  .buy-btn {
    width: 100%;
    padding: 10px;
    background: #0070f3;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    transition: 0.2s;
  }

  .buy-btn:hover {
    background: #0059c9;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
</style>