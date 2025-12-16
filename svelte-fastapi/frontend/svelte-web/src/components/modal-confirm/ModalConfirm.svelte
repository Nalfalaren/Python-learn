<script lang="ts">
  export let show = false;
  export let message = "Are you sure you want to delete this item?";
  export let onConfirm = () => {};
  export let onCancel = () => {};

  function stop(e: MouseEvent) {
    e.stopPropagation();
  }
</script>

{#if show}
  <div class="overlay" onclick={onCancel}>
    <div class="modal" onclick={stop}>
      <p class="message">{message}</p>
      <div class="actions">
        <button class="btn cancel" onclick={onCancel}>
          Cancel
        </button>
        <button class="btn confirm" onclick={onConfirm}>
          Delete
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
  }

  .modal {
    background: white;
    padding: 24px 32px;
    border-radius: 10px;
    min-width: 320px;
    text-align: center;
    font-family: system-ui, sans-serif;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    animation: scaleIn 0.15s ease-out;
  }

  .message {
    font-size: 16px;
    margin-bottom: 22px;
    color: #333;
  }

  .actions {
    display: flex;
    justify-content: center;
    gap: 12px;
  }

  .btn {
    padding: 8px 18px;
    border-radius: 6px;
    cursor: pointer;
    border: none;
    font-size: 14px;
  }

  .btn.cancel {
    background: #e5e7eb;
    color: #111;
  }

  .btn.cancel:hover {
    background: #d1d5db;
  }

  .btn.confirm {
    background: #dc2626;
    color: white;
  }

  .btn.confirm:hover {
    background: #b91c1c;
  }

  @keyframes scaleIn {
    from {
      transform: scale(0.95);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  }
</style>
