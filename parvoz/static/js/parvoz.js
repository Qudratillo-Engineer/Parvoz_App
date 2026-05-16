document.addEventListener("DOMContentLoaded", () => {
    initMessages();
    setActiveNavigation();
    initTablePicker();
    initCategoryFilters();
    initOrderFilters();
});

function initMessages() {
    const toasts = document.querySelectorAll("[data-message-toast]");
    if (!toasts.length) return;

    const closeToast = (toast) => {
        toast.classList.add("is-leaving");
        window.setTimeout(() => toast.remove(), 180);
    };

    toasts.forEach((toast) => {
        toast.querySelector("[data-message-close]")?.addEventListener("click", () => closeToast(toast));
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
