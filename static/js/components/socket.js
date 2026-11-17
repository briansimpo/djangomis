/**
 * SpiceSocket Initializer & Lifecycle Manager
 */

let socket = null;
let handlers = [];
let initialized = false;

export async function initialize() {
    if (initialized) return destroy;

    const socket = globalThis.spice?.socket;

    if (!socket) {
        console.warn("Socket is unavailable.");
        return;
    }

    const events = {
        connected: () => {
            console.log("Socket connected");
        },

        disconnected: () => {
            console.log("Socket disconnected");
        },

        reconnect_failed: event => {
            console.error("Socket reconnection failed:", event);
        },

        error: event => {
            console.error("Socket error:", event);
        },
    };

    for (const [event, callback] of Object.entries(events)) {
        socket.on(event, callback);
        handlers.push([event, callback]);
    }

    initialized = true;

    try {
        await socket.connect();
    } catch (error) {
        console.error("Socket connection failed:", error);
    }

    return destroy;
}

export function destroy() {
    if (!socket) return;

    for (const [event, callback] of handlers) {
        socket.off?.(event, callback);
    }

    handlers = [];

    socket.disconnect?.();

    socket = null;
    initialized = false;
}