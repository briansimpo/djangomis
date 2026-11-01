import Alpine from "alpinejs";

let initialized = false;

export function initialize() {
    if (initialized) return;

    Alpine.start();
    initialized = true;
}