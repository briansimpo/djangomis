export function initialize() {
    function initializeAttributes(element, options) {
        const { to, target, select, transition, preload, method } = options;
        const resolvedTarget = target || 'app-view';
        const resolvedSelect = select || resolvedTarget; 
        const swapConfig = transition 
            ? 'innerHTML transition:true show:window:top' 
            : 'innerHTML show:window:top';

        const hxMethod = method || 'get';
        element.setAttribute(`hx-${hxMethod}`, to);
        element.setAttribute('hx-target', resolvedTarget);
        element.setAttribute('hx-select', resolvedSelect);
        element.setAttribute('hx-swap', swapConfig);
        
        if (hxMethod === 'get') {
            element.setAttribute('hx-push-url', 'true');
        }
        
        if (preload) element.setAttribute('preload', 'mouseover');
        
        if (window.htmx) {
            window.htmx.process(element);
        }
    }

    function processBoostContainer(container) {
        const target = container.getAttribute('target');
        const select = container.getAttribute('select');
        const transition = container.hasAttribute('transition');
        const preload = container.hasAttribute('preload');

        container.querySelectorAll('a[href]').forEach(a => {
            const to = a.getAttribute('href');
            if (to && !to.startsWith('http') && !to.startsWith('#') && !to.startsWith('mailto:')) {
                initializeAttributes(a, { to, target, select, transition, preload, method: 'get' });
            }
        });

        container.querySelectorAll('button[hx-get], button[hx-post], button[hx-put], button[hx-delete]').forEach(btn => {
            const resolvedTarget = target || 'app-view';
            const resolvedSelect = select || resolvedTarget;
            btn.setAttribute('hx-target', resolvedTarget);
            btn.setAttribute('hx-select', resolvedSelect);
            if (transition && !btn.hasAttribute('hx-swap')) {
                btn.setAttribute('hx-swap', 'innerHTML transition:true show:window:top');
            }
            if (window.htmx) {
                window.htmx.process(btn);
            }
        });
    }

    // 1. <app-view> Viewport Container
    if (!customElements.get('app-view')) {
        class AppView extends HTMLElement {
            connectedCallback() {
                if (this.hasAttribute('data-initialized')) return;
                this.setAttribute('data-initialized', 'true');
            }
        }
        customElements.define('app-view', AppView);
    }

    // 2. <spa-link> Custom Element (Guarded against double-init/back-button scaling)
    if (!customElements.get('spa-link')) {
        class SpaLink extends HTMLElement {
            connectedCallback() {
                if (this.hasAttribute('data-initialized')) return;
                this.setAttribute('data-initialized', 'true');

                const to = this.getAttribute('to') || '#';
                const target = this.getAttribute('target');
                const select = this.getAttribute('select');
                const transition = this.hasAttribute('transition');
                const preload = this.hasAttribute('preload');
                const customClass = this.getAttribute('class');

                const a = document.createElement('a');
                a.href = to;
                if (customClass) a.className = customClass;

                while (this.firstChild) {
                    a.appendChild(this.firstChild);
                }

                initializeAttributes(a, { to, target, select, transition, preload, method: 'get' });
                this.appendChild(a);

                this.updateActiveState();
                this._onNavigate = () => this.updateActiveState();
                window.addEventListener('popstate', this._onNavigate);
                document.body.addEventListener('htmx:pushedIntoHistory', this._onNavigate);
            }

            disconnectedCallback() {
                window.removeEventListener('popstate', this._onNavigate);
                document.body.removeEventListener('htmx:pushedIntoHistory', this._onNavigate);
                this.removeAttribute('data-initialized');
            }

            updateActiveState() {
                const a = this.querySelector('a');
                if (!a) return;
                const currentPath = window.location.pathname;
                const linkPath = new URL(a.href, window.location.origin).pathname;
                const isExact = this.hasAttribute('exact');
                const isActive = isExact 
                    ? currentPath === linkPath 
                    : currentPath.startsWith(linkPath) && (linkPath !== '/' || currentPath === '/');

                a.classList.toggle('active', isActive);
                if (isActive) a.setAttribute('aria-current', 'page');
                else a.removeAttribute('aria-current');
            }
        }
        customElements.define('spa-link', SpaLink);
    }

    // 3. <spa-button> Custom Element (Guarded against double-init/back-button scaling)
    if (!customElements.get('spa-button')) {
        class SpaButton extends HTMLElement {
            connectedCallback() {
                if (this.hasAttribute('data-initialized')) return;
                this.setAttribute('data-initialized', 'true');

                const to = this.getAttribute('to') || '#';
                const method = this.getAttribute('method') || 'get';
                const target = this.getAttribute('target');
                const select = this.getAttribute('select');
                const transition = this.hasAttribute('transition');
                const customClass = this.getAttribute('class');

                const btn = document.createElement('button');
                btn.type = 'button';
                if (customClass) btn.className = customClass;

                while (this.firstChild) {
                    btn.appendChild(this.firstChild);
                }

                this.appendChild(btn);
                initializeAttributes(btn, { to, target, select, transition, method });
            }

            disconnectedCallback() {
                this.removeAttribute('data-initialized');
            }
        }
        customElements.define('spa-button', SpaButton);
    }

    // 4. <app-loading> Custom Element (Global/Scoped request loader)
    if (!customElements.get('app-loading')) {
        class AppLoading extends HTMLElement {
            connectedCallback() {
                if (this.hasAttribute('data-initialized')) return;
                this.setAttribute('data-initialized', 'true');

                // Hide by default
                this.style.display = 'none';

                this._onBeforeRequest = () => {
                    this.style.display = '';
                    this.classList.add('loading', 'active');
                };

                this._onAfterRequest = () => {
                    this.style.display = 'none';
                    this.classList.remove('loading', 'active');
                };

                document.body.addEventListener('htmx:beforeRequest', this._onBeforeRequest);
                document.body.addEventListener('htmx:afterRequest', this._onAfterRequest);
            }

            disconnectedCallback() {
                document.body.removeEventListener('htmx:beforeRequest', this._onBeforeRequest);
                document.body.removeEventListener('htmx:afterRequest', this._onAfterRequest);
                this.removeAttribute('data-initialized');
            }
        }
        customElements.define('app-loading', AppLoading);
    }

    // 5. <spa-nav> Custom Element
    if (!customElements.get('spa-nav')) {
        class SpaNav extends HTMLElement {
            connectedCallback() {
                if (this.hasAttribute('data-initialized')) return;
                this.setAttribute('data-initialized', 'true');
                processBoostContainer(this);
            }
        }
        customElements.define('spa-nav', SpaNav);
    }

    // 6. <spa-boost> Custom Element
    if (!customElements.get('spa-boost')) {
        class SpaBoost extends HTMLElement {
            connectedCallback() {
                if (this.hasAttribute('data-initialized')) return;
                this.setAttribute('data-initialized', 'true');
                processBoostContainer(this);
            }
        }
        customElements.define('spa-boost', SpaBoost);
    }

    // Attribute-based [spa-boost] containers
    document.querySelectorAll('[spa-boost]').forEach(container => {
        processBoostContainer(container);
    });
}