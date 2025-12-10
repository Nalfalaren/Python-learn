<script lang="ts">
	let { children } = $props();
</script>

<svelte:head></svelte:head>

{@render children?.()}

<style global>
    body {
        margin: 0;
		padding: 0;
		box-sizing: border-box;
		font-family: system-ui, sans-serif;
    }
</style>
