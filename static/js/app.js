
import "@fortawesome/fontawesome-free/js/all";

import "@/css/main.css";
import "@/css/app.css";

import htmx from "htmx.org";
import Alpine from "alpinejs";
import Sortable from "sortablejs";

import NProgress from "nprogress";
import "nprogress/nprogress.css";

// --------------------------------------------------
// Global libraries
// --------------------------------------------------

window.htmx = htmx;
window.Alpine = Alpine;
window.Sortable = Sortable;
window.NProgress = NProgress;

// --------------------------------------------------
// HTMX extensions
// --------------------------------------------------

// Load extensions only after HTMX has been initialized.
await import("htmx-ext-ws");

// --------------------------------------------------
// CSRF protection
// --------------------------------------------------

document.addEventListener("htmx:configRequest", (event) => {
    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

    if (csrfToken) {
        event.detail.headers["X-CSRFToken"] = csrfToken;
    }
});

// --------------------------------------------------
// Alpine.js
// --------------------------------------------------

function initializeAlpine() {
    Alpine.start();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeAlpine, {
        once: true,
    });
} else {
    initializeAlpine();
}

// --------------------------------------------------
// Djangospice Realtime
// --------------------------------------------------

function initializeRealtime() {
    if (!globalThis.Djangospice?.Realtime) {
        console.error(
            "Djangospice Realtime is unavailable. " +
            "Check that the websocket assets are loaded before app.js."
        );
        return;
    }

    const Realtime = Djangospice.Realtime;

    // Connection events
    Realtime.on("connected", () => {
        console.log("Djangospice Realtime connected");
    });

    Realtime.on("disconnected", () => {
        console.log("Djangospice Realtime disconnected");
    });

    Realtime.on("reconnect_failed", (event) => {
        console.error(
            "Djangospice Realtime reconnection failed:",
            event
        );
    });

    Realtime.on("error", (event) => {
        console.error("Djangospice Realtime error:", event);
    });

    // Connect
    Realtime.connect().catch((error) => {
        console.error(
            "Djangospice Realtime connection failed:",
            error
        );
    });
}

// Initialize after the document is ready.
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeRealtime, {
        once: true,
    });
} else {
    initializeRealtime();
}
