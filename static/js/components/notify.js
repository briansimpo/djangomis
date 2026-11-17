export async function initialize() {
    const socket = globalThis.spice?.socket;
    const body = document.body;

    const unsubscribers = [];

    // --------------------------------------------------
    // Notification created
    // --------------------------------------------------

    unsubscribers.push(
        socket.on("notification_created", (data) => {
            htmx.trigger(body, "refresh-notifications");
        })
    );


    unsubscribers.push(
        socket.on("notification_read", (data) => {
            htmx.trigger(body, "refresh-notifications");
        })
    );
    
    unsubscribers.push(
        socket.on("notification_read_all", (data) => {
            htmx.trigger(body, "refresh-notifications");
        })
    );
    return () => {
        unsubscribers.forEach(unsubscribe => unsubscribe());
    };
}