export class ApplicationLifecycle {
    constructor(registry) {
        this.registry = registry;
        this.cleanups = [];
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;

        this.initialized = true;

        try {
            for (const [name, component] of this.registry.entries()) {
                try {
                    const cleanup = await component.initialize();

                    if (typeof cleanup === "function") {
                        this.cleanups.push(cleanup);
                    }
                } catch (error) {
                    console.error(
                        `Failed to initialize component "${name}":`,
                        error
                    );
                }
            }
        } catch (error) {
            this.initialized = false;
            throw error;
        }
    }

    async destroy() {
        for (const cleanup of this.cleanups.reverse()) {
            try {
                await cleanup();
            } catch (error) {
                console.error("Component cleanup failed:", error);
            }
        }

        this.cleanups = [];
        this.initialized = false;
    }
}