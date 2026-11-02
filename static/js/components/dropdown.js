
const MAX_NOTIFICATIONS = 10;

export function initializeDropdown() {
    const list = document.querySelector(
        "[data-notification-list]"
    );

    if (!list) return;

    const countBadge = document.querySelector(
        "[data-notification-count]"
    );

    const newCount = document.querySelector(
        "[data-notification-new-count]"
    );

    function updateCount(count) {
        const value = Math.max(0, Number(count) || 0);

        if (countBadge) {
            countBadge.textContent = value;
            countBadge.hidden = value === 0;
        }

        if (newCount) {
            newCount.textContent = `${value} New`;
            newCount.hidden = value === 0;
        }
    }

    function find(id) {
        return list.querySelector(
            `[data-notification-id="${CSS.escape(String(id))}"]`
        );
    }

    function append(notification, unreadCount) {
        if (!notification?.id) return;

        // Remove an existing item before refreshing it.
        find(notification.id)?.remove();

        const item = document.createElement("a");

        item.dataset.notificationId = notification.id;
        item.className = "flex px-4 py-3 bg-indigo-50/40 hover:bg-gray-100 transition-colors";

        const url = notification.url;

        item.href = (
            typeof url === "string" &&
            url.startsWith("/") &&
            !url.startsWith("//")
        ) ? url : "#";

        const icon = document.createElement("div");
        icon.className = "flex-shrink-0 mr-3";

        const iconWrapper = document.createElement("span");
        iconWrapper.className = "inline-flex items-center justify-center h-8 w-8 rounded-full bg-blue-100 text-blue-600";

        iconWrapper.textContent = "●";
        icon.append(iconWrapper);

        const content = document.createElement("div");
        content.className = "w-full";

        const verb = document.createElement("p");
        verb.className = "text-sm text-gray-800 font-medium";
        verb.textContent = notification.verb || "New notification";

        const description = document.createElement("p");
        description.className = "text-xs text-gray-500 mt-0.5 truncate";
        description.textContent = notification.description || "";

        const timespan = document.createElement("p");
        timespan.className = "text-[11px] text-gray-400 mt-1";
        timespan.textContent = notification.timespan || "Just now";

        content.append(verb, description, timespan);

        const indicator = document.createElement("div");
        indicator.className = "flex-shrink-0 self-center ml-2";

        const dot = document.createElement("span");
        dot.className = "h-2 w-2 bg-indigo-600 rounded-full inline-block";

        indicator.append(dot);

        item.append(icon, content, indicator);

        list.prepend(item);

        while (list.children.length > MAX_NOTIFICATIONS) {
            list.lastElementChild.remove();
        }

        if (unreadCount !== undefined && unreadCount !== null) {
            updateCount(unreadCount);
        }
    }

    function remove(id, unreadCount) {
        if (id) {
            find(id)?.remove();
        }

        if (unreadCount !== undefined && unreadCount !== null) {
            updateCount(unreadCount);
        }
    }

    function updateNotification(notification, unreadCount) {
        if (!notification?.id) return;

        if (notification.unread) {
            append(notification, unreadCount);
        } else {
            remove(notification.id, unreadCount);
        }
    }

    return {
        append,
        remove,
        find,
        updateCount,
        updateNotification,
    };
}
