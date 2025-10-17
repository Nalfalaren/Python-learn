<script lang="ts">
    import { env } from "$env/dynamic/public";
    import { goto } from "$app/navigation";
    import styles from "$lib/styles/header/accounts.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
    import { page } from "$app/state";

    interface SearchParams {
        id?: string;
        owner?: string;
    }

    interface FormDataProps {
        id: string;
        owner: string;
        balance: number;
        interest_rate: number;
        max_withdraw_count: number;
    }

    let formData: FormDataProps = $state({
        id: "",
        owner: "",
        balance: 0,
        interest_rate: 0,
        max_withdraw_count: 0,
    });
    let searchResult: FormDataProps[] = $state([]);
    let loadingState: "loading" | "idle" | "error" = $state("idle");
    let id = page.url.searchParams.get("search_id");
    let owner = page.url.searchParams.get("search_account");
    let inputRef: HTMLInputElement | null = $state(null);
    let message = $state("");

    function handleChange(name: string, value: string) {
        formData = { ...formData, [name]: value };
    }

    async function fetchAllAccount(url: URL) {
        let response = await fetch(url);
        if (response.ok) {
            let res = await response.json();
            loadingState = "idle";
            searchResult = res.search_result;
        }
    }

    function buildAccountUrl({ id, owner }: SearchParams) {
        const url = new URL(`${env.PUBLIC_API_URL}/account`);
        const params = { search_id: id, search_account: owner };

        Object.entries(params).forEach(([key, value]) => {
            if (value) url.searchParams.set(key, value);
        });

        return url;
    }

    async function handleSubmit() {
        loadingState = "loading";
        try {
            const url = buildAccountUrl(formData);
            goto(`${url.pathname}?${url.searchParams.toString()}`, {
                replaceState: true,
            });
            fetchAllAccount(url);
        } catch (error) {
            console.error("Error", error);
            loadingState = "error";
        }
    }

    async function handleDeleteRow(account_id: string) {
        loadingState = "loading";
        try {
            const url = new URL(`${env.PUBLIC_API_URL}/account/${account_id}`);
            const response = await fetch(url, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (response.ok) {
                message = await response.json();
                fetchAllAccount(buildAccountUrl({ id, owner } as SearchParams))
                loadingState = "idle";
            }
        } catch (error) {
            console.error(error);
            loadingState = "error";
        }
    }

    function handleNavigate(location: string) {
        goto("/account/sign-up");
    }

    $effect(() => {
        const url = buildAccountUrl({ id, owner } as SearchParams);
        fetchAllAccount(url);
    });
</script>

<div>
    <div class={styles.headerContainer}>
        <div class={styles.headerContent}>
            <div><h1>Content</h1></div>
            <button onclick={() => handleNavigate("/account/sign-up")}
                >+ Add Content</button
            >
        </div>
        <TabNavigation />
    </div>
    <div class={styles.tableSearch}>
        <div class={styles.tableSearchInput}>
            <TextField
                title="ID"
                type="text"
                name="id"
                {inputRef}
                placeholder="Input ID"
                value={id || ""}
                onValueChange={(value: string) => handleChange("id", value)}
            />
        </div>
        <div class={styles.tableSearchInput}>
            <TextField
                title="Account Name"
                type="text"
                name="owner"
                placeholder="Input account name"
                value={owner || ""}
                onValueChange={(value: string) => handleChange("owner", value)}
            />
        </div>
        <button
            type="button"
            onclick={handleSubmit}
            aria-label="Search"
            class={styles.tableSearchButton}
        >
            Search
        </button>
    </div>
    <div class={styles.tableContainer}>
        {#if loadingState == "loading"}
            <p>Loading...</p>
        {:else if loadingState == "error" || searchResult.length == 0}
            <p>No result found</p>
        {:else}
            <table class={styles.table}>
                <thead>
                    <tr>
                        <th>Account ID</th>
                        <th>Owner</th>
                        <th>Balance</th>
                        <th>Interest Rate</th>
                        <th>Max Withdraw Count</th>
                    </tr>
                </thead>

                <tbody>
                    {#each searchResult as account}
                        <tr>
                            <td>{account?.id}</td>
                            <td>{account?.owner}</td>
                            <td>${account?.balance.toLocaleString()}</td>
                            <td>{account?.interest_rate}%</td>
                            <td>{account?.max_withdraw_count}</td>
                            <td
                                style="background-color: blue; color: white; font-weight: bold; padding: 8px; border-radius: 4px;"
                                onclick={() => goto(`/account/update/${account.id}`)}
                                >Update</td
                            >
                            <td
                                style="background-color: red; color: white; font-weight: bold; padding: 8px; border-radius: 4px;"
                                onclick={() => handleDeleteRow(account.id)}
                                >x</td
                            >
                        </tr>
                    {/each}
                </tbody>
            </table>
        {/if}
    </div>
</div>
