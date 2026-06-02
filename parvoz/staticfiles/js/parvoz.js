document.addEventListener("DOMContentLoaded", () => {
    initMessages();
    setActiveNavigation();
    initTablePicker();
    initCategoryFilters();
    initOrderFilters();
    initSimplePolling();
});

function initMessages() {
    const closeToast = (toast) => {
        if (!toast || toast.classList.contains("is-leaving")) return;
        toast.classList.add("is-leaving");
        window.setTimeout(() => toast.remove(), 180);
    };

    document.addEventListener("click", (event) => {
        const button = event.target.closest("[data-message-close]");
        if (button) closeToast(button.closest("[data-message-toast]"));
    });

    document.querySelectorAll("[data-message-toast]").forEach((toast) => {
        window.setTimeout(() => closeToast(toast), 5200);
    });
}

function setActiveNavigation() {
    const page = document.body.dataset.page;
    if (!page) return;
    document.querySelectorAll("[data-nav]").forEach((link) => {
        link.classList.toggle("active", link.dataset.nav === page);
    });
}

function initTablePicker() {
    const buttons = document.querySelectorAll(".table-btn[data-table]");
    const input = document.querySelector("[data-table-input]");
    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            buttons.forEach((item) => item.classList.remove("is-selected"));
            button.classList.add("is-selected");
            if (input) input.value = button.dataset.table;
        });
    });
}

function initCategoryFilters() {
    const pills = document.querySelectorAll("[data-category]");
    const cards = document.querySelectorAll("[data-dish-category]");
    if (!pills.length || !cards.length) return;
    pills.forEach((pill) => {
        pill.addEventListener("click", () => {
            const category = pill.dataset.category;
            pills.forEach((item) => item.classList.remove("active"));
            pill.classList.add("active");
            cards.forEach((card) => {
                const show = category === "all" || card.dataset.dishCategory === category;
                card.hidden = !show;
            });
        });
    });
}

function initOrderFilters() {
    const pills = document.querySelectorAll("[data-order-filter]");
    const cards = document.querySelectorAll("[data-order-status]");
    if (!pills.length || !cards.length) return;
    pills.forEach((pill) => {
        pill.addEventListener("click", () => {
            const status = pill.dataset.orderFilter;
            pills.forEach((item) => item.classList.remove("active"));
            pill.classList.add("active");
            cards.forEach((card) => {
                const show = status === "all" || card.dataset.orderStatus === status;
                card.hidden = !show;
            });
        });
    });
}

function initSimplePolling() {
    const target = document.querySelector("[data-poll-url]");
    if (!target) return;

    const url = target.dataset.pollUrl;
    const interval = Number(target.dataset.pollInterval || 5000);
    let lastSignature = null;
    let isChecking = false;

    async function checkForUpdates() {
        if (isChecking || document.hidden) return;
        isChecking = true;

        try {
            const response = await fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
                cache: "no-store",
            });
            if (!response.ok) return;

            const data = await response.json();
            if (!data || !data.signature) return;

            if (lastSignature === null) {
                lastSignature = data.signature;
                return;
            }

            if (lastSignature !== data.signature) {
                window.location.reload();
            }
        } catch (error) {
            console.log("Polling error:", error);
        } finally {
            isChecking = false;
        }
    }

    window.setTimeout(checkForUpdates, 600);
    window.setInterval(checkForUpdates, interval);
}
