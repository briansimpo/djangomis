import "@fortawesome/fontawesome-free/js/all";

import htmx from "htmx.org";
import Alpine from "alpinejs";
import Sortable from "sortablejs";

export function initializeLibraries() {
    globalThis.htmx = htmx;
    globalThis.Alpine = Alpine;
    globalThis.Sortable = Sortable;

    return { htmx, Alpine, Sortable };
}