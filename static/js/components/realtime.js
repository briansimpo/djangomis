let realtime = null;
let handlers = [];
let initialized = false;

export async function initialize() {
    if (initialized) return;

    realtime = globalThis.Djangospice?.Realtime;

    if (!realtime) {
        console.warn("Djangospice Realtime is unavailable.");
        return;
    }

    const events = {
        connected: () => {
            console.log("Djangospice Realtime connected");
        },

        disconnected: () => {
            console.log("Djangospice Realtime disconnected");
        },

        reconnect_failed: event => {
            console.error("Realtime reconnection failed:", event);
        },

        error: event => {
            console.error("Realtime error:", event);
        },
    };

    for (const [event, callback] of Object.entries(events)) {
        realtime.on(event, callback);
        handlers.push([event, callback]);
    }

    initialized = true;

    try {
        await realtime.connect();
    } catch (error) {
        console.error("Realtime connection failed:", error);
    }

    return destroy;
}

export function destroy() {
    if (!realtime) return;

    for (const [event, callback] of handlers) {
        realtime.off?.(event, callback);
    }

    handlers = [];

    // Disconnect if the Realtime implementation supports it.
    realtime.disconnect?.();

    realtime = null;
    initialized = false;
}