export function initialize() {
    const handler = event => {
        const csrfToken = document
            .querySelector('meta[name="csrf-token"]')
            ?.getAttribute("content");

        if (csrfToken) {
            event.detail.headers["X-CSRFToken"] = csrfToken;
        }
    };

    document.addEventListener("htmx:configRequest", handler);

    return () => {
        document.removeEventListener(
            "htmx:configRequest",
            handler
        );
    };
}