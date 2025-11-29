<script lang="ts">
    import styles from './TextField.module.css';

    export let title: string;
    export let name: string;
    export let type: string = "text";
    export let placeholder: string = "";
    export let value: string = ""
    export let inputRef: HTMLInputElement | null = null
    export let onValueChange: (value: string) => void;
</script>

<div class={styles.textFieldContainer}>
    <label style="font-family: system-ui, sans-serif;">
        {title}
        <input
            name={name}
            type={type}
            placeholder={placeholder}
            class={styles.textFieldInput}
            bind:value={value}
            bind:this={inputRef}
            on:input={(e) => onValueChange((e.target as HTMLInputElement).value)}
        />
    </label>
</div>
