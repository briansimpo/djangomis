
import { initializeDropdown } from "./dropdown.js"; 

export async function initialize() {
    const notification = globalThis.Djangospice?.Notification;

    if (!notification) {
        console.warn("Djangospice Notification is unavailable.");
        return;
    }

    const dropdown = initializeDropdown();

    if (!dropdown) {
        console.warn("Notification dropdown is unavailable.");
        return;
    }

    await notification.initialize();

    const unsubscribers = [];

    // --------------------------------------------------
    // Notification created
    // --------------------------------------------------

    unsubscribers.push(
        notification.on("notification_created", (data) => {
            dropdown.append(
                data.notification,
                data.unread_count
            );
        })
    );

    // --------------------------------------------------
    // Notification read
    // --------------------------------------------------

    unsubscribers.push(
        notification.on("notification_read", (data) => {
            dropdown.updateNotification(
                data.notification,
                data.unread_count
            );
        })
    );

    // --------------------------------------------------
    // Notification unread
    // --------------------------------------------------

    unsubscribers.push(
        notification.on("notification_unread", (data) => {
            dropdown.updateNotification(
                data.notification,
                data.unread_count
            );
        })
    );

    // --------------------------------------------------
    // Notification deleted
    // --------------------------------------------------

    unsubscribers.push(
        notification.on("notification_deleted", (data) => {
            dropdown.remove(
                data.notification?.id,
                data.unread_count
            );
        })
    );

    return () => {
        unsubscribers.forEach(unsubscribe => unsubscribe());
    };
}
