export class ComponentRegistry {
    constructor() {
        this.components = new Map();
    }

    register(name, component) {
        if (this.components.has(name)) {
            throw new Error(
                `Component "${name}" is already registered.`
            );
        }

        if (typeof component?.initialize !== "function") {
            throw new TypeError(
                `Component "${name}" must implement initialize().`
            );
        }

        this.components.set(name, component);

        return this;
    }

    get(name) {
        return this.components.get(name);
    }

    has(name) {
        return this.components.has(name);
    }

    entries() {
        return this.components.entries();
    }

    values() {
        return this.components.values();
    }
}

export const registry = new ComponentRegistry();