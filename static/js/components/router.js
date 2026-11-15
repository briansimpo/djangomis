export function initializeSpaRouter() {
  function applySpaAttributes(element, options) {
    const { to, target, select, transition, preload, method } = options;
    const resolvedTarget = target || '#app-viewport';
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

    // Boost standard anchor links
    container.querySelectorAll('a[href]').forEach(a => {
      const to = a.getAttribute('href');
      if (to && !to.startsWith('http') && !to.startsWith('#') && !to.startsWith('mailto:')) {
        applySpaAttributes(a, { to, target, select, transition, preload, method: 'get' });
      }
    });

    // Boost action buttons with hx-get, hx-post, hx-put, hx-delete
    container.querySelectorAll('button[hx-get], button[hx-post], button[hx-put], button[hx-delete]').forEach(btn => {
      const resolvedTarget = target || '#app-viewport';
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

  // 1. <spa-link> Custom Element
  if (!customElements.get('spa-link')) {
    class SpaLink extends HTMLElement {
      connectedCallback() {
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

        applySpaAttributes(a, { to, target, select, transition, preload, method: 'get' });
        this.appendChild(a);

        this.updateActiveState();
        this._onNavigate = () => this.updateActiveState();
        window.addEventListener('popstate', this._onNavigate);
        document.body.addEventListener('htmx:pushedIntoHistory', this._onNavigate);
      }

      disconnectedCallback() {
        window.removeEventListener('popstate', this._onNavigate);
        document.body.removeEventListener('htmx:pushedIntoHistory', this._onNavigate);
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

  // 2. <spa-button> Custom Element
  if (!customElements.get('spa-button')) {
    class SpaButton extends HTMLElement {
      connectedCallback() {
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

        applySpaAttributes(btn, { to, target, select, transition, method });
        this.appendChild(btn);
      }
    }
    customElements.define('spa-button', SpaButton);
  }

  // 3. <spa-nav> Custom Element
  if (!customElements.get('spa-nav')) {
    class SpaNav extends HTMLElement {
      connectedCallback() {
        processBoostContainer(this);
      }
    }
    customElements.define('spa-nav', SpaNav);
  }

  // 4. <spa-boost> Custom Element
  if (!customElements.get('spa-boost')) {
    class SpaBoost extends HTMLElement {
      connectedCallback() {
        processBoostContainer(this);
      }
    }
    customElements.define('spa-boost', SpaBoost);
  }

  // 5. Query and process any element carrying the `spa-boost` attribute on startup
  document.querySelectorAll('[spa-boost]').forEach(container => {
    processBoostContainer(container);
  });
}