
import "@/css/theme.css";
import "@/css/app.css";

import {
    initializeLibraries,
    registry,
    ApplicationLifecycle,
} from "./core/index.js";

import {
    initializeHTMX,
    initializeAlpine,
    initializeRealtime,
    initializeNotification,
} from "./components/index.js";

// --------------------------------------------------
// Application setup
// --------------------------------------------------

initializeLibraries();

// --------------------------------------------------
// Component registration
// --------------------------------------------------

registry
    .register("htmx", {
        initialize: initializeHTMX,
    })
    .register("alpine", {
        initialize: initializeAlpine,
    })
    .register("realtime", {
        initialize: initializeRealtime,
    })
    .register("notification", {
        initialize: initializeNotification,
    });

// --------------------------------------------------
// Application lifecycle
// --------------------------------------------------

const lifecycle = new ApplicationLifecycle(registry);

async function initializeApp() {
    await lifecycle.initialize();
}

async function destroyApp() {
    await lifecycle.destroy();
}

// --------------------------------------------------
// Document lifecycle
// --------------------------------------------------

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeApp, {
        once: true,
    });
} else {
    initializeApp();
}

export {
    initializeApp,
    destroyApp,
};
