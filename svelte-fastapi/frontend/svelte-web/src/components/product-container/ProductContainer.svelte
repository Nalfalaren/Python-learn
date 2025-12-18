<script lang="ts">
    import styles from "$lib/styles/landing/landing.module.css"
    export let keyNumber: number = 0
</script>

<div class={styles.dealCard} style={`animation-delay: ${keyNumber * 60}ms`}>
    <slot />
</div>
