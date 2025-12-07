<script lang="ts">
  export let show = false;
  export let message = "";
  export let onClose = () => {};

  $: visible = show && message.length > 0;
</script>

{#if visible}
  <div class="overlay" on:click={onClose}>
    <div class="modal" on:click|stopPropagation>
      <p>{message}</p>
      <button class="close-btn" on:click={onClose}>Close</button>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
  }

  .modal {
    background: white;
    padding: 20px 30px;
    border-radius: 8px;
    min-width: 300px;
    text-align: center;
    font-family: system-ui, sans-serif;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }

  .close-btn {
    margin-top: 15px;
    background: black;
    color: white;
    padding: 8px 18px;
    border-radius: 6px;
    cursor: pointer;
  }

  .close-btn:hover {
    opacity: 0.8;
  }
</style>
