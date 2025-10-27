<script lang="ts">
    import { env } from "$env/dynamic/public";
    import { goto } from "$app/navigation";
    import styles from "$lib/styles/header/employees.module.css";
    import TextField from "../../components/input/TextField.svelte";
    import TabNavigation from "../../components/tab-navigation/TabNavigation.svelte";
    import { page } from "$app/state";

    interface SearchParams {
        id?: string;
        employee_name?: string;
        page?: number;
        limit?: number;
    }

    interface FormDataProps {
        id: string;
        employee_name: string;
        role: string;
        email: string;
        is_active: boolean;
    }

    let formData: FormDataProps = $state({
        id: "",
        employee_name: "",
        role: "",
        email: "",
        is_active: false,
    });

    let searchResult: FormDataProps[] = $state([]);
    let loadingState: "loading" | "idle" | "error" = $state("idle");
    let message = $state("");

    // pagination state
    let currentPage = $state(1);
    let pageSize = $state(10);
    let totalRecords = $state(0);
    let totalPages = $derived(Math.ceil(totalRecords / pageSize));

    // query params
    let id = page.url.searchParams.get("search_id") || "";
    let employee_name = page.url.searchParams.get("search_employee") || "";

    function handleChange(name: string, value: string) {
        formData = { ...formData, [name]: value };
    }

    function buildEmployeeUrl({
        id,
        employee_name,
        page,
        limit,
    }: SearchParams) {
        const url = new URL(`${env.PUBLIC_API_URL}/employees`);
        const params = {
            search_id: id,
            search_employee: employee_name,
            page,
            limit,
        };
        Object.entries(params).forEach(([key, value]) => {
            if (value) url.searchParams.set(key, String(value));
        });
        return url;
    }

    async function fetchAllEmployee(url: URL) {
        const token = localStorage.getItem("accessToken");
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const res = await response.json();
            loadingState = "idle";
            searchResult = res.search_result || [];
            totalRecords = res.total_employee || res.count || 0; // your backend should send this
        } else {
            loadingState = "error";
        }
    }

    async function handleSubmit() {
        loadingState = "loading";
        try {
            currentPage = 1; // reset to first page when searching
            const url = buildEmployeeUrl({
                id: formData.id,
                employee_name: formData.employee_name,
                page: currentPage,
                limit: pageSize,
            });
            goto(`?${url.searchParams.toString()}`, { replaceState: true });
            await fetchAllEmployee(url);
        } catch (error) {
            console.error("Error", error);
            loadingState = "error";
        }
    }

    async function handleDeleteRow(employee_id: string) {
        loadingState = "loading";
        const token = localStorage.getItem("accessToken");
        try {
            const url = new URL(
                `${env.PUBLIC_API_URL}/employee/${employee_id}`,
            );
            const response = await fetch(url, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                message = await response.json();
                fetchAllEmployee(
                    buildEmployeeUrl({
                        id,
                        employee_name,
                        page: currentPage,
                        limit: pageSize,
                    }),
                );
            }
        } catch (error) {
            console.error(error);
            loadingState = "error";
        }
    }

    function handlePageChange(newPage: number) {
        if (newPage < 1 || newPage > totalPages) return;
        currentPage = newPage;
        const url = buildEmployeeUrl({
            id: formData.id,
            employee_name: formData.employee_name,
            page: currentPage,
            limit: pageSize,
        });
        fetchAllEmployee(url);
    }

    function handlePageSizeChange(event: Event) {
        const newSize = Number((event.target as HTMLSelectElement).value);
        pageSize = newSize;
        currentPage = 1;
        const url = buildEmployeeUrl({
            id: formData.id,
            employee_name: formData.employee_name,
            page: currentPage,
            limit: pageSize,
        });
        goto(`?${url.searchParams.toString()}`, { replaceState: true });
        fetchAllEmployee(url);
    }

    $effect(() => {
        const url = buildEmployeeUrl({
            id,
            employee_name,
            page: currentPage,
            limit: pageSize,
        });
        fetchAllEmployee(url);
    });
</script>

<div>
    <div class={styles.headerContainer}>
        <div class={styles.headerContent}>
            <div><h1>Content</h1></div>
            <button onclick={() => goto("/employee/sign-up")}
                >+ Add Content</button
            >
        </div>
        <TabNavigation />
    </div>

    <!-- Search Section -->
    <div class={styles.tableSearch}>
        <div class={styles.tableSearchInput}>
            <TextField
                title="ID"
                type="text"
                name="id"
                placeholder="Input ID"
                value={id || ""}
                onValueChange={(value: string) => handleChange("id", value)}
            />
        </div>
        <div class={styles.tableSearchInput}>
            <TextField
                title="Employee Name"
                type="text"
                name="employee_name"
                placeholder="Input Employee Name"
                value={employee_name || ""}
                onValueChange={(value: string) =>
                    handleChange("employee_name", value)}
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

    <!-- Table Section -->
    <div class={styles.tableContainer}>
        {#if loadingState == "loading"}
            <p>Loading...</p>
        {:else if loadingState == "error" || searchResult.length == 0}
            <p>No result found</p>
        {:else}
            <table class={styles.table}>
                <thead>
                    <tr>
                        <th>UUID</th>
                        <th>Employee Name</th>
                        <th>Role</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th colspan="2">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {#each searchResult as employee}
                        <tr>
                            <td>{employee.id}</td>
                            <td>{employee.employee_name}</td>
                            <td>{employee.role}</td>
                            <td>{employee.email}</td>
                            <td>{employee.is_active ? "Active" : "Inactive"}</td
                            >
                            <td
                                style="background-color: blue; color: white; font-weight: bold; padding: 8px; border-radius: 4px; cursor: pointer;"
                                onclick={() =>
                                    goto(`/employee/update/${employee.id}`)}
                            >
                                Update
                            </td>
                            <td
                                style="background-color: red; color: white; font-weight: bold; padding: 8px; border-radius: 4px; cursor: pointer;"
                                onclick={() => handleDeleteRow(employee.id)}
                            >
                                x
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>

            <!-- Pagination Controls -->
            <div class={styles.paginationControls}>
                <button
                    onclick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                >
                    Previous
                </button>
                <span>Page {currentPage} / {totalPages || 1}</span>
                <button
                    onclick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                >
                    Next
                </button>

                <label>
                    Show:
                    <select
                        bind:value={pageSize}
                        onchange={handlePageSizeChange}
                    >
                        <option value={10}>10</option>
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                    </select>
                    per page
                </label>
            </div>
        {/if}
    </div>
</div>
