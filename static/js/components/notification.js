export async function initialize() {
    const notification = globalThis.Djangospice?.Notification;

    if (!notification) {
        console.warn("Djangospice Notification is unavailable.");
        return;
    }

    await notification.initialize();

    const unsubscribe = notification.on("created", data => {
        console.log("Notification created:", data);

        // Application notification handling.
    });

    return unsubscribe;
}