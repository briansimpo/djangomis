
import "@fortawesome/fontawesome-free/js/all";

import "@/css/main.css";
import "@/css/app.css";

import htmx from "htmx.org";
import Alpine from "alpinejs";
import Sortable from "sortablejs";


// --------------------------------------------------
// Global libraries
// --------------------------------------------------

window.htmx = htmx;
window.Alpine = Alpine;
window.Sortable = Sortable;


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
// Djangospice Notifications
// --------------------------------------------------

async function initializeNotifications() {
    const notification = globalThis.Djangospice?.Notification;

    if (!notification) {
        console.error(
            "Djangospice Notification is unavailable. " +
            "Check that notification assets are loaded before app.js."
        );
        return;
    }

    await notification.initialize();

}

// --------------------------------------------------
// Djangospice Realtime
// --------------------------------------------------

function initializeRealtime() {

    const Realtime = globalThis.Djangospice?.Realtime;

    if (!Realtime) {
        console.error(
            "Djangospice Realtime is unavailable. " +
            "Check that websocket assets are loaded before app.js."
        );
        return;
    }

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

    // Initialize notification listeners before connecting.
    initializeNotifications();

    // Connect using automatic same-origin configuration.
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
