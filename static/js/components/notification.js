export async function initialize() {
    const realtime = globalThis.Djangospice?.Realtime;
    const body = document.body;

    if (!realtime) {
        console.warn("Djangospice Realtime is unavailable.");
        return;
    }

    const unsubscribers = [];

    // --------------------------------------------------
    // Notification created
    // --------------------------------------------------

    unsubscribers.push(
        realtime.on("notification_created", (data) => {
            htmx.trigger(body, "refresh-notifications");
        })
    );


    unsubscribers.push(
        realtime.on("notification_read", (data) => {
            htmx.trigger(body, "refresh-notifications");
        })
    );
    
    unsubscribers.push(
        realtime.on("notification_read_all", (data) => {
            htmx.trigger(body, "refresh-notifications");
        })
    );
    return () => {
        unsubscribers.forEach(unsubscribe => unsubscribe());
    };
}