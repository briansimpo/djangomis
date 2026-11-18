var Djangospice = (() => {
  var __defProp = Object.defineProperty;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);

  // ../djangospice/src/djangospice/spice/static/spice/js/html/root.js
  if (!customElements.get("spice-app")) {
    customElements.define(
      "spice-app",
      class extends HTMLElement {
        connectedCallback() {
          this.dispatchEvent(
            new CustomEvent("spice:app:connected", {
              bubbles: true,
              composed: true,
              detail: { element: this }
            })
          );
        }
      }
    );
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/utils/config.js
  var DEFAULTS = {
    target: "spice-app",
    select: "spice-app",
    swap: "innerHTML show:window:top",
    transition: false,
    preload: false,
    pushUrl: true
  };
  var HTTP_METHODS = /* @__PURE__ */ new Set([
    "get",
    "post",
    "put",
    "patch",
    "delete"
  ]);
  var CONTAINER_SELECTOR = [
    "spice-app",
    "spice-nav",
    "spice-boost",
    "[spice-boost]"
  ].join(",");
  var ROUTER_EVENTS = {
    READY: "spice:router:ready",
    BEFORE_NAVIGATE: "spice:router:before-navigate",
    BEFORE_SWAP: "spice:router:before-swap",
    AFTER_SWAP: "spice:router:after-swap",
    NAVIGATE: "spice:router:navigate",
    LOCATION_CHANGE: "spice:router:location-change",
    NAVIGATION_ERROR: "spice:router:navigation-error",
    LOADING: "spice:router:loading",
    LOADED: "spice:router:loaded"
  };
  function emit(target, name, detail = {}, options = {}) {
    return (target || document).dispatchEvent(
      new CustomEvent(name, {
        bubbles: true,
        composed: true,
        cancelable: options.cancelable ?? false,
        detail
      })
    );
  }
  function parseBoolean(value, fallback = false) {
    if (value === null || value === void 0) return fallback;
    if (value === "") return true;
    return !["false", "0", "off", "no"].includes(String(value).toLowerCase());
  }
  function normalizePath(path) {
    if (!path) return "/";
    let result = path.replace(/\/+/g, "/");
    if (result.length > 1) {
      result = result.replace(/\/$/, "");
    }
    return result || "/";
  }
  function isInternalURL(value) {
    if (!value) return false;
    try {
      const url = new URL(value, window.location.href);
      return ["http:", "https:"].includes(url.protocol) && url.origin === window.location.origin;
    } catch {
      return false;
    }
  }
  function shouldEnhanceAnchor(anchor) {
    if (!anchor?.hasAttribute("href")) return false;
    const href = anchor.getAttribute("href");
    if (!href || href.startsWith("#")) return false;
    try {
      const url = new URL(href, window.location.href);
      if (url.origin === window.location.origin && url.pathname === window.location.pathname && url.search === window.location.search && url.hash) {
        return false;
      }
    } catch {
      return false;
    }
    if (!isInternalURL(anchor.href)) return false;
    if (anchor.hasAttribute("download") || anchor.target === "_blank" || anchor.relList.contains("external") || anchor.getAttribute("hx-boost") === "false") {
      return false;
    }
    return true;
  }
  function resolveConfig(element) {
    const config = { ...DEFAULTS };
    const containers = [];
    let current = element;
    while (current && current !== document.documentElement) {
      if (current.matches?.(CONTAINER_SELECTOR)) {
        containers.push(current);
      }
      current = current.parentElement;
    }
    containers.reverse();
    const apply = (source, isRequestElement = false) => {
      if (!source?.getAttribute) return;
      const target = source.getAttribute(isRequestElement ? "hx-target" : "target");
      const select = source.getAttribute("select");
      const swap = source.getAttribute("swap");
      const transition = source.getAttribute("transition");
      const preload = source.getAttribute("preload");
      const pushUrl = source.getAttribute("push-url");
      if (target !== null) config.target = target;
      if (select !== null) config.select = select;
      if (swap !== null) config.swap = swap;
      if (transition !== null) {
        config.transition = parseBoolean(transition, config.transition);
      }
      if (preload !== null) {
        config.preload = parseBoolean(preload, config.preload);
      }
      if (pushUrl !== null) {
        config.pushUrl = parseBoolean(pushUrl, config.pushUrl);
      }
    };
    containers.forEach((container) => apply(container));
    apply(element, true);
    config.target || (config.target = "spice-app");
    config.select || (config.select = config.target);
    config.swap || (config.swap = DEFAULTS.swap);
    return config;
  }
  function copyAttributes(source, destination, excluded = /* @__PURE__ */ new Set()) {
    for (const attribute of source.attributes) {
      const name = attribute.name;
      if (excluded.has(name) || name.startsWith("data-spice-internal-")) {
        continue;
      }
      destination.setAttribute(name, attribute.value);
    }
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/html/link.js
  if (!customElements.get("spice-link")) {
    customElements.define(
      "spice-link",
      class extends HTMLElement {
        connectedCallback() {
          if (this.hasAttribute("data-initialized")) return;
          this.setAttribute("data-initialized", "true");
          const to = this.getAttribute("to") || "#";
          const anchor = document.createElement("a");
          anchor.href = to;
          copyAttributes(
            this,
            anchor,
            /* @__PURE__ */ new Set(["id", "to", "exact", "active-class", "match-query"])
          );
          anchor.dataset.spiceNavigation = "true";
          anchor.dataset.spiceLink = "true";
          if (this.hasAttribute("exact")) {
            anchor.dataset.spiceExact = "true";
          }
          const activeClass = this.getAttribute("active-class");
          if (activeClass) {
            anchor.dataset.spiceActiveClass = activeClass;
          }
          if (this.hasAttribute("match-query")) {
            anchor.dataset.spiceMatchQuery = "true";
          }
          while (this.firstChild) {
            anchor.appendChild(this.firstChild);
          }
          this.appendChild(anchor);
          const config = resolveConfig(this);
          anchor.setAttribute("hx-get", to);
          anchor.setAttribute("hx-target", config.target);
          anchor.setAttribute("hx-select", config.select);
          const swap = config.transition ? `${config.swap} transition:true` : config.swap;
          anchor.setAttribute("hx-swap", swap);
          anchor.setAttribute("hx-push-url", config.pushUrl ? "true" : "false");
          if (config.preload) {
            anchor.setAttribute("preload", "mouseover");
          }
          anchor.dataset.spiceRouterProcessed = "true";
          if (window.htmx) {
            window.htmx.process(anchor);
          }
        }
      }
    );
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/html/button.js
  if (!customElements.get("spice-button")) {
    customElements.define(
      "spice-button",
      class extends HTMLElement {
        connectedCallback() {
          if (this.hasAttribute("data-initialized")) return;
          this.setAttribute("data-initialized", "true");
          const to = this.getAttribute("to");
          const method = (this.getAttribute("method") || "get").toLowerCase();
          if (!to || !HTTP_METHODS.has(method)) {
            console.error("SpiceButton: Invalid configuration.", this);
            return;
          }
          const button = document.createElement("button");
          button.type = this.getAttribute("type") || "button";
          copyAttributes(this, button, /* @__PURE__ */ new Set(["id", "to", "method", "push-url"]));
          button.dataset.spiceNavigation = "true";
          while (this.firstChild) {
            button.appendChild(this.firstChild);
          }
          this.appendChild(button);
          const config = resolveConfig(this);
          const effectivePushUrl = parseBoolean(
            this.getAttribute("push-url"),
            method === "get"
          );
          button.setAttribute(`hx-${method}`, to);
          button.setAttribute("hx-target", config.target);
          button.setAttribute("hx-select", config.select);
          const swap = config.transition ? `${config.swap} transition:true` : config.swap;
          button.setAttribute("hx-swap", swap);
          if (method === "get") {
            button.setAttribute("hx-push-url", effectivePushUrl ? "true" : "false");
          } else if (effectivePushUrl) {
            button.setAttribute("hx-push-url", "true");
          }
          button.dataset.spiceRouterProcessed = "true";
          if (window.htmx) {
            window.htmx.process(button);
          }
        }
      }
    );
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/html/nav.js
  if (!customElements.get("spice-nav")) {
    customElements.define(
      "spice-nav",
      class extends HTMLElement {
        connectedCallback() {
          this.querySelectorAll("a[href]").forEach((anchor) => {
            if (anchor.dataset.spiceRouterProcessed === "true") return;
            if (!shouldEnhanceAnchor(anchor)) return;
            const to = anchor.getAttribute("href");
            const config = resolveConfig(anchor);
            anchor.setAttribute("hx-get", to);
            anchor.setAttribute("hx-target", config.target);
            anchor.setAttribute("hx-select", config.select);
            anchor.setAttribute("hx-swap", config.transition ? `${config.swap} transition:true` : config.swap);
            anchor.setAttribute("hx-push-url", config.pushUrl ? "true" : "false");
            anchor.dataset.spiceNavigation = "true";
            anchor.dataset.spiceLink = "true";
            anchor.dataset.spiceRouterProcessed = "true";
            if (window.htmx) {
              window.htmx.process(anchor);
            }
          });
        }
      }
    );
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/html/boost.js
  if (!customElements.get("spice-boost")) {
    customElements.define(
      "spice-boost",
      class extends HTMLElement {
        connectedCallback() {
          this.querySelectorAll("a[href]").forEach((anchor) => {
            if (anchor.dataset.spiceRouterProcessed === "true") return;
            if (!shouldEnhanceAnchor(anchor)) return;
            const to = anchor.getAttribute("href");
            const config = resolveConfig(anchor);
            anchor.setAttribute("hx-get", to);
            anchor.setAttribute("hx-target", config.target);
            anchor.setAttribute("hx-select", config.select);
            anchor.setAttribute(
              "hx-swap",
              config.transition ? `${config.swap} transition:true` : config.swap
            );
            anchor.setAttribute("hx-push-url", config.pushUrl ? "true" : "false");
            anchor.dataset.spiceNavigation = "true";
            anchor.dataset.spiceRouterProcessed = "true";
            if (window.htmx) {
              window.htmx.process(anchor);
            }
          });
        }
      }
    );
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/html/loading.js
  if (!customElements.get("spice-loading")) {
    customElements.define(
      "spice-loading",
      class extends HTMLElement {
        constructor() {
          super();
          this.requests = /* @__PURE__ */ new Set();
          this.fallbackRequestCount = 0;
          this.onBeforeRequest = this.handleBeforeRequest.bind(this);
          this.onAfterRequest = this.handleAfterRequest.bind(this);
          this.onRequestError = this.handleRequestError.bind(this);
        }
        connectedCallback() {
          if (this.hasAttribute("data-initialized")) return;
          this.setAttribute("data-initialized", "true");
          this.style.display = "none";
          document.addEventListener("htmx:beforeRequest", this.onBeforeRequest);
          document.addEventListener("htmx:afterRequest", this.onAfterRequest);
          [
            "htmx:sendError",
            "htmx:timeout",
            "htmx:sendAbort",
            "htmx:responseError"
          ].forEach((event) => {
            document.addEventListener(event, this.onRequestError);
          });
        }
        disconnectedCallback() {
          document.removeEventListener("htmx:beforeRequest", this.onBeforeRequest);
          document.removeEventListener("htmx:afterRequest", this.onAfterRequest);
          [
            "htmx:sendError",
            "htmx:timeout",
            "htmx:sendAbort",
            "htmx:responseError"
          ].forEach((event) => {
            document.removeEventListener(event, this.onRequestError);
          });
          this.removeAttribute("data-initialized");
        }
        matchesRequest(detail) {
          const trigger = detail?.elt || detail?.requestConfig?.elt;
          const actualTarget = detail?.target;
          const scope = this.getAttribute("scope");
          const selector = this.getAttribute("target");
          if (scope && (!trigger || !trigger.closest(scope))) {
            return false;
          }
          if (!selector) return true;
          try {
            return Boolean(actualTarget?.matches(selector));
          } catch {
            return false;
          }
        }
        getRequestKey(detail) {
          return detail?.xhr || null;
        }
        handleBeforeRequest(event) {
          const detail = event.detail || {};
          if (!this.matchesRequest(detail)) return;
          const key = this.getRequestKey(detail);
          if (key) {
            this.requests.add(key);
          } else {
            this.fallbackRequestCount++;
          }
          this.show();
        }
        handleAfterRequest(event) {
          const detail = event.detail || {};
          if (!this.matchesRequest(detail)) return;
          this.finishRequest(detail);
        }
        handleRequestError(event) {
          const detail = event.detail || {};
          if (!this.matchesRequest(detail)) return;
          this.finishRequest(detail);
        }
        finishRequest(detail) {
          const key = this.getRequestKey(detail);
          if (key) {
            this.requests.delete(key);
          } else if (this.fallbackRequestCount > 0) {
            this.fallbackRequestCount--;
          }
          if (this.requests.size === 0 && this.fallbackRequestCount === 0) {
            this.hide();
          }
        }
        show() {
          this.style.display = "";
          this.classList.add("loading", "active");
          emit(this, ROUTER_EVENTS.LOADING, { element: this });
        }
        hide() {
          this.style.display = "none";
          this.classList.remove("loading", "active");
          emit(this, ROUTER_EVENTS.LOADED, { element: this });
        }
      }
    );
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/html/toast.js
  var SpiceToastElement = class extends HTMLElement {
    connectedCallback() {
      if (this.initialized) return;
      this.initialized = true;
      this.classList.add(
        "fixed",
        "bottom-6",
        "left-6",
        "z-[9999]",
        "pointer-events-none",
        "flex",
        "flex-col",
        "gap-3"
      );
      if (!this.querySelector("template")) {
        this.innerHTML = `
                <template>
                    <div
                        data-toast
                        data-type="info"
                        role="alert"
                        class="
                            pointer-events-auto flex items-center justify-between gap-6
                            min-w-[360px] max-w-md px-5 py-4
                            bg-[#202124] text-white border border-white/10
                            border-l-4 border-l-blue-500
                            rounded-lg shadow-2xl
                            transition-all duration-300
                            translate-y-4 opacity-0">

                        <div class="flex-1 min-w-0">
                            <p
                                data-toast-message
                                class="text-base font-medium leading-relaxed tracking-wide">
                            </p>
                        </div>

                        <button
                            type="button"
                            data-dismiss="toast"
                            class="
                                shrink-0 text-gray-300 hover:text-white
                                transition-colors text-sm font-semibold
                                uppercase px-2 py-1 rounded hover:bg-white/10"
                            aria-label="Dismiss notification">
                            Dismiss
                        </button>
                    </div>
                </template>
            `;
      }
    }
  };
  if (!customElements.get("spice-toast")) {
    customElements.define("spice-toast", SpiceToastElement);
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/components/modal.js
  var Modal = class {
    constructor() {
      /**
       * Handle modal interactions.
       */
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="modal"]');
        if (toggle) {
          this.open(toggle, e);
          return;
        }
        const dismiss = e.target.closest('[data-dismiss="modal"]');
        if (dismiss) {
          e.preventDefault();
          const modal = dismiss.closest("[data-modal]");
          if (modal) this.close(modal);
          return;
        }
        if (e.target.matches("[data-modal]") && e.target.dataset.backdrop !== "static") {
          this.close(e.target);
        }
      });
      /**
       * Handle keyboard interactions.
       */
      __publicField(this, "handleKeydown", (e) => {
        if (e.key === "Escape") {
          this.closeTopModal();
          return;
        }
        if (e.key === "Tab") {
          this.trapFocus(e);
        }
      });
      this.activeModals = [];
    }
    /**
     * Initialize modal component.
     */
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
      document.addEventListener("keydown", this.handleKeydown);
    }
    /**
     * Initialize modal states.
     */
    initStates(root = document) {
      root.querySelectorAll("[data-modal]").forEach((modal) => {
        if (modal.dataset.open === "true") {
          this.show(modal);
        } else {
          modal.classList.add("hidden");
          modal.setAttribute("aria-hidden", "true");
        }
      });
    }
    /**
     * Open a modal using its trigger.
     */
    open(toggle, e) {
      if (e) e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      if (!targetSelector || targetSelector === "#") return;
      let modal;
      try {
        modal = document.querySelector(targetSelector);
      } catch {
        return;
      }
      if (!modal) return;
      modal.__triggerElement = toggle;
      this.show(modal);
    }
    /**
     * Show a modal.
     */
    show(modal) {
      if (!modal || this.activeModals.includes(modal)) return;
      modal.classList.remove("hidden");
      modal.setAttribute("aria-hidden", "false");
      document.body.classList.add("overflow-hidden");
      this.activeModals.push(modal);
      const focusable = this.getFocusableElements(modal);
      if (focusable.length > 0) {
        const autoFocusEl = modal.querySelector("[autofocus]") || focusable[0];
        requestAnimationFrame(() => autoFocusEl.focus());
      }
      modal.dispatchEvent(
        new CustomEvent("spice:modal:shown", { bubbles: true })
      );
    }
    /**
     * Close a modal.
     */
    close(modal) {
      if (!modal || !this.activeModals.includes(modal)) return;
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
      this.activeModals = this.activeModals.filter((m) => m !== modal);
      if (this.activeModals.length === 0) {
        document.body.classList.remove("overflow-hidden");
      }
      if (modal.__triggerElement && document.body.contains(modal.__triggerElement)) {
        modal.__triggerElement.focus();
      }
      modal.dispatchEvent(
        new CustomEvent("spice:modal:hidden", { bubbles: true })
      );
    }
    /**
     * Close the topmost modal.
     */
    closeTopModal() {
      if (this.activeModals.length === 0) return false;
      const topModal = this.activeModals[this.activeModals.length - 1];
      if (topModal.dataset.keyboard === "false") return false;
      this.close(topModal);
      return true;
    }
    /**
     * Trap keyboard focus inside the active modal.
     */
    trapFocus(e) {
      if (this.activeModals.length === 0) return;
      const topModal = this.activeModals[this.activeModals.length - 1];
      const focusable = this.getFocusableElements(topModal);
      if (focusable.length === 0) {
        e.preventDefault();
        topModal.focus();
        return;
      }
      const firstEl = focusable[0];
      const lastEl = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === firstEl) {
        e.preventDefault();
        lastEl.focus();
      } else if (!e.shiftKey && document.activeElement === lastEl) {
        e.preventDefault();
        firstEl.focus();
      }
    }
    /**
     * Get focusable elements inside a container.
     */
    getFocusableElements(container) {
      return Array.from(
        container.querySelectorAll(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      ).filter((el) => el.offsetParent !== null);
    }
    /**
     * Destroy component listeners.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
      document.removeEventListener("keydown", this.handleKeydown);
      this.activeModals.forEach((modal) => {
        modal.classList.add("hidden");
        modal.setAttribute("aria-hidden", "true");
      });
      this.activeModals = [];
      document.body.classList.remove("overflow-hidden");
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/offcanvas.js
  var Offcanvas = class {
    constructor() {
      /**
       * Handle offcanvas interactions.
       */
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="offcanvas"]');
        if (toggle) {
          this.open(toggle, e);
          return;
        }
        const dismiss = e.target.closest('[data-dismiss="offcanvas"]');
        if (dismiss) {
          e.preventDefault();
          const offcanvas = dismiss.closest("[data-offcanvas]");
          if (offcanvas) this.close(offcanvas);
          return;
        }
        const backdrop = e.target.closest("[data-offcanvas-backdrop]");
        if (backdrop && this.activeOffcanvas) {
          if (this.activeOffcanvas.dataset.backdrop !== "static") {
            this.close(this.activeOffcanvas);
          }
        }
      });
      /**
       * Handle keyboard interactions.
       */
      __publicField(this, "handleKeydown", (e) => {
        if (e.key === "Escape" && this.activeOffcanvas) {
          if (this.activeOffcanvas.dataset.keyboard !== "false") {
            this.close();
          }
        }
      });
      this.activeOffcanvas = null;
      this.closeTimer = null;
    }
    /**
     * Initialize offcanvas component.
     */
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
      document.addEventListener("keydown", this.handleKeydown);
    }
    /**
     * Initialize offcanvas states.
     */
    initStates(root = document) {
      root.querySelectorAll("[data-offcanvas]").forEach((offcanvas) => {
        if (offcanvas.dataset.open === "true") {
          this.show(offcanvas);
        } else {
          this.hide(offcanvas);
        }
      });
    }
    /**
     * Open offcanvas using its trigger.
     */
    open(toggle, e) {
      if (e) e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      if (!targetSelector || targetSelector === "#") return;
      let offcanvas;
      try {
        offcanvas = document.querySelector(targetSelector);
      } catch {
        return;
      }
      if (!offcanvas) return;
      offcanvas.__triggerElement = toggle;
      this.show(offcanvas);
    }
    /**
     * Show offcanvas.
     */
    show(offcanvas) {
      if (!offcanvas || this.activeOffcanvas === offcanvas) return;
      if (this.activeOffcanvas) {
        this.close(this.activeOffcanvas);
      }
      clearTimeout(this.closeTimer);
      const panel = offcanvas.querySelector("[data-offcanvas-panel]");
      const backdrop = offcanvas.querySelector("[data-offcanvas-backdrop]");
      offcanvas.classList.remove("pointer-events-none");
      offcanvas.setAttribute("aria-hidden", "false");
      document.body.classList.add("overflow-hidden");
      this.activeOffcanvas = offcanvas;
      requestAnimationFrame(() => {
        if (panel) {
          panel.classList.remove(
            "translate-x-full",
            "-translate-x-full",
            "translate-y-full",
            "-translate-y-full"
          );
        }
        if (backdrop) {
          backdrop.classList.remove("opacity-0");
        }
      });
      offcanvas.dispatchEvent(
        new CustomEvent("spice:offcanvas:shown", { bubbles: true })
      );
    }
    /**
     * Close offcanvas.
     */
    close(offcanvas = this.activeOffcanvas) {
      if (!offcanvas || this.activeOffcanvas !== offcanvas) return;
      const panel = offcanvas.querySelector("[data-offcanvas-panel]");
      const backdrop = offcanvas.querySelector("[data-offcanvas-backdrop]");
      const placement = offcanvas.dataset.placement || "right";
      const translateMap = {
        right: "translate-x-full",
        left: "-translate-x-full",
        top: "-translate-y-full",
        bottom: "translate-y-full"
      };
      if (panel) {
        panel.classList.add(translateMap[placement] || "translate-x-full");
      }
      if (backdrop) {
        backdrop.classList.add("opacity-0");
      }
      offcanvas.setAttribute("aria-hidden", "true");
      this.activeOffcanvas = null;
      if (offcanvas.__triggerElement && document.body.contains(offcanvas.__triggerElement)) {
        offcanvas.__triggerElement.focus();
      }
      this.closeTimer = setTimeout(() => {
        offcanvas.classList.add("pointer-events-none");
        if (!this.activeOffcanvas) {
          document.body.classList.remove("overflow-hidden");
        }
      }, 300);
      offcanvas.dispatchEvent(
        new CustomEvent("spice:offcanvas:hidden", { bubbles: true })
      );
    }
    /**
     * Hide offcanvas without animation.
     */
    hide(offcanvas) {
      if (!offcanvas) return;
      const panel = offcanvas.querySelector("[data-offcanvas-panel]");
      const backdrop = offcanvas.querySelector("[data-offcanvas-backdrop]");
      const placement = offcanvas.dataset.placement || "right";
      const translateMap = {
        right: "translate-x-full",
        left: "-translate-x-full",
        top: "-translate-y-full",
        bottom: "translate-y-full"
      };
      offcanvas.classList.add("pointer-events-none");
      offcanvas.setAttribute("aria-hidden", "true");
      if (panel) {
        panel.classList.add(translateMap[placement] || "translate-x-full");
      }
      if (backdrop) {
        backdrop.classList.add("opacity-0");
      }
      if (this.activeOffcanvas === offcanvas) {
        this.activeOffcanvas = null;
      }
    }
    /**
     * Destroy component listeners.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
      document.removeEventListener("keydown", this.handleKeydown);
      clearTimeout(this.closeTimer);
      if (this.activeOffcanvas) {
        this.hide(this.activeOffcanvas);
      }
      document.body.classList.remove("overflow-hidden");
      this.activeOffcanvas = null;
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/sidebar.js
  var Sidebar = class {
    constructor() {
      /**
       * Handle sidebar interactions.
       */
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="sidebar"]');
        if (toggle) {
          this.handleToggle(toggle, e);
          return;
        }
        if (e.target.closest("[data-sidebar-backdrop]")) {
          this.close();
        }
      });
      this.activeSidebar = null;
      this.backdrop = null;
      this.closeTimer = null;
    }
    /**
     * Initialize sidebar component.
     */
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
    }
    /**
     * Initialize sidebar states.
     */
    initStates(root = document) {
      root.querySelectorAll("[data-sidebar], aside[id]").forEach((sidebar) => {
        if (sidebar.dataset.open === "true") {
          this.show(sidebar);
        } else {
          this.hide(sidebar);
        }
      });
    }
    /**
     * Handle sidebar toggle.
     */
    handleToggle(toggle, e) {
      e.preventDefault();
      e.stopPropagation();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      if (!targetSelector || targetSelector === "#") return;
      let sidebar;
      try {
        sidebar = document.querySelector(targetSelector);
      } catch {
        return;
      }
      if (!sidebar) return;
      if (this.activeSidebar === sidebar) {
        this.close(sidebar);
      } else {
        this.open(sidebar, toggle);
      }
    }
    /**
     * Open sidebar.
     */
    open(sidebar, toggle = null) {
      if (!sidebar) return;
      if (this.activeSidebar && this.activeSidebar !== sidebar) {
        this.close(this.activeSidebar);
      }
      sidebar.__triggerElement = toggle;
      this.show(sidebar);
    }
    /**
     * Show sidebar.
     */
    show(sidebar) {
      if (!sidebar) return;
      clearTimeout(this.closeTimer);
      sidebar.classList.remove("-translate-x-full");
      sidebar.classList.add("translate-x-0");
      this.activeSidebar = sidebar;
      this.showBackdrop();
      sidebar.dispatchEvent(
        new CustomEvent("spice:sidebar:shown", { bubbles: true })
      );
    }
    /**
     * Show or create sidebar backdrop.
     */
    showBackdrop() {
      let backdrop = document.querySelector("#spice-sidebar-backdrop");
      if (!backdrop) {
        backdrop = document.createElement("div");
        backdrop.id = "spice-sidebar-backdrop";
        backdrop.className = [
          "fixed",
          "inset-0",
          "z-30",
          "bg-black/30",
          "lg:hidden",
          "pt-16",
          "transition-opacity",
          "opacity-0"
        ].join(" ");
        backdrop.setAttribute("data-sidebar-backdrop", "");
        document.body.appendChild(backdrop);
      } else {
        backdrop.classList.remove("hidden");
      }
      this.backdrop = backdrop;
      requestAnimationFrame(() => {
        backdrop.classList.remove("opacity-0");
      });
    }
    /**
     * Close sidebar.
     */
    close(sidebar = this.activeSidebar) {
      if (!sidebar || this.activeSidebar !== sidebar) return;
      sidebar.classList.remove("translate-x-0");
      sidebar.classList.add("-translate-x-full");
      this.hideBackdrop();
      if (sidebar.__triggerElement && document.body.contains(sidebar.__triggerElement)) {
        sidebar.__triggerElement.focus();
      }
      this.activeSidebar = null;
      sidebar.dispatchEvent(
        new CustomEvent("spice:sidebar:hidden", { bubbles: true })
      );
    }
    /**
     * Hide backdrop.
     */
    hideBackdrop() {
      if (!this.backdrop) return;
      const backdrop = this.backdrop;
      backdrop.classList.add("opacity-0");
      this.closeTimer = setTimeout(() => {
        if (this.activeSidebar) return;
        backdrop.classList.add("hidden");
      }, 200);
    }
    /**
     * Hide sidebar without animation events.
     */
    hide(sidebar) {
      if (!sidebar) return;
      sidebar.classList.remove("translate-x-0");
      sidebar.classList.add("-translate-x-full");
      if (this.activeSidebar === sidebar) {
        this.activeSidebar = null;
      }
    }
    /**
     * Destroy component listeners.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
      clearTimeout(this.closeTimer);
      if (this.activeSidebar) {
        this.hide(this.activeSidebar);
      }
      if (this.backdrop) {
        this.backdrop.remove();
        this.backdrop = null;
      }
      this.activeSidebar = null;
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/dropdown.js
  var Dropdown = class {
    constructor() {
      /**
       * Handle dropdown interactions.
       */
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="dropdown"]');
        if (toggle) {
          this.toggle(toggle, e);
          return;
        }
        this.closeAll(e.target);
      });
    }
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
    }
    /**
     * Initialize dropdown states.
     */
    initStates(root = document) {
      root.querySelectorAll("[data-dropdown-menu]").forEach((menu) => {
        if (menu.dataset.open === "true") {
          menu.classList.remove("hidden");
          this.syncToggle(menu, true);
        } else {
          menu.classList.add("hidden");
          this.syncToggle(menu, false);
        }
      });
    }
    /**
     * Toggle dropdown visibility.
     */
    toggle(toggle, e) {
      e.preventDefault();
      e.stopPropagation();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const dropdown = targetSelector && targetSelector !== "#" ? document.querySelector(targetSelector) : toggle.nextElementSibling;
      if (!dropdown) return;
      const isOpen = !dropdown.classList.contains("hidden");
      this.closeAll();
      if (!isOpen) {
        dropdown.classList.remove("hidden");
        this.syncToggle(dropdown, true);
      }
    }
    /**
     * Close all dropdowns except the one containing the given element.
     */
    closeAll(exceptElement = null) {
      document.querySelectorAll("[data-dropdown-menu]").forEach((menu) => {
        if (!exceptElement || !menu.contains(exceptElement)) {
          menu.classList.add("hidden");
          this.syncToggle(menu, false);
        }
      });
    }
    /**
     * Synchronize toggle accessibility and visual state.
     */
    syncToggle(menu, isOpen) {
      const wrapper = menu.closest("[data-dropdown-wrapper]") || menu.parentElement;
      const toggle = wrapper?.querySelector('[data-toggle="dropdown"]');
      if (!toggle) return;
      toggle.setAttribute("aria-expanded", String(isOpen));
      const chevron = toggle.querySelector("[data-chevron]");
      if (chevron) {
        chevron.classList.toggle("rotate-180", isOpen);
      }
    }
    /**
     * Remove event listeners.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/tabs.js
  var Tabs = class {
    constructor() {
      /**
       * Handle tab clicks.
       */
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="tab"]');
        if (!toggle) return;
        this.activate(toggle, e);
      });
      /**
       * Handle browser hash changes.
       */
      __publicField(this, "handleHashChange", () => {
        this.initFromHash();
      });
    }
    /**
     * Initialize tabs component.
     */
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
      window.addEventListener("hashchange", this.handleHashChange);
      this.initFromHash();
    }
    /**
     * Initialize tab states.
     */
    initStates(root = document) {
      const tabLists = [];
      if (root.matches?.('[role="tablist"], [data-tabs]')) {
        tabLists.push(root);
      }
      tabLists.push(
        ...root.querySelectorAll('[role="tablist"], [data-tabs]')
      );
      tabLists.forEach((tabList) => {
        const tabs = tabList.querySelectorAll('[data-toggle="tab"]');
        if (!tabs.length) return;
        const activeTab = Array.from(tabs).find(
          (tab) => tab.dataset.state === "active" || tab.getAttribute("aria-selected") === "true"
        );
        if (activeTab) {
          this.activate(activeTab, null, false);
        }
      });
    }
    /**
     * Activate a tab.
     */
    activate(toggle, e = null, syncHash = true) {
      if (e) e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      if (!targetSelector || targetSelector === "#") return;
      let targetPane;
      try {
        targetPane = document.querySelector(targetSelector);
      } catch {
        return;
      }
      if (!targetPane) return;
      const tabList = toggle.closest('[role="tablist"], [data-tabs]');
      const paneContainer = targetPane.parentElement;
      if (tabList) {
        tabList.querySelectorAll('[data-toggle="tab"]').forEach((tab) => {
          tab.setAttribute("aria-selected", "false");
          tab.dataset.state = "inactive";
        });
      }
      if (paneContainer) {
        Array.from(paneContainer.children).forEach((pane) => {
          if (pane.hasAttribute("data-tab-pane")) {
            pane.classList.add("hidden");
            pane.dataset.state = "inactive";
          }
        });
      }
      toggle.setAttribute("aria-selected", "true");
      toggle.dataset.state = "active";
      targetPane.classList.remove("hidden");
      targetPane.dataset.state = "active";
      if (syncHash && tabList?.dataset.syncHash === "true" && targetSelector.startsWith("#")) {
        history.replaceState(null, "", targetSelector);
      }
      toggle.dispatchEvent(
        new CustomEvent("spice:tab:shown", {
          bubbles: true,
          detail: {
            tab: toggle,
            pane: targetPane
          }
        })
      );
    }
    /**
     * Activate tab matching the current URL hash.
     */
    initFromHash() {
      const hash = window.location.hash;
      if (!hash) return;
      const tabs = document.querySelectorAll('[data-toggle="tab"]');
      const matchingTab = Array.from(tabs).find((tab) => {
        return tab.dataset.target === hash || tab.getAttribute("href") === hash;
      });
      if (matchingTab) {
        this.activate(matchingTab, null, false);
      }
    }
    /**
     * Destroy component listeners.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
      window.removeEventListener("hashchange", this.handleHashChange);
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/collapse.js
  var Collapse = class {
    constructor() {
      /**
       * Handle collapse interactions.
       */
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="collapse"]');
        if (!toggle) return;
        e.preventDefault();
        this.toggle(toggle);
      });
    }
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
    }
    /**
     * Initialize collapse elements.
     */
    initStates(root = document) {
      root.querySelectorAll("[data-collapse-content]").forEach((el) => {
        if (el.dataset.open === "true") {
          el.classList.remove("hidden");
          this.syncToggle(el, true);
        } else {
          el.classList.add("hidden");
          this.syncToggle(el, false);
        }
      });
    }
    /**
     * Toggle collapse content.
     */
    toggle(toggle) {
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      if (!targetSelector) return;
      let target;
      try {
        target = document.querySelector(targetSelector);
      } catch {
        return;
      }
      if (!target) return;
      const accordionGroup = toggle.closest("[data-accordion]");
      const isExpanded = !target.classList.contains("hidden");
      if (accordionGroup && !isExpanded && accordionGroup.dataset.accordion === "single") {
        accordionGroup.querySelectorAll("[data-collapse-content]").forEach((content) => {
          content.classList.add("hidden");
          this.syncToggle(content, false);
        });
      }
      target.classList.toggle("hidden");
      this.syncToggle(target, !isExpanded);
    }
    /**
     * Synchronize toggle accessibility and visual state.
     */
    syncToggle(target, isExpanded) {
      const wrapper = target.closest("[data-collapse-wrapper]") || target.parentElement;
      const toggle = wrapper?.querySelector('[data-toggle="collapse"]');
      if (!toggle) return;
      toggle.setAttribute("aria-expanded", String(isExpanded));
      const chevron = toggle.querySelector("[data-chevron]");
      if (chevron) {
        chevron.classList.toggle("rotate-180", isExpanded);
      }
    }
    /**
     * Remove event listeners.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/tooltip.js
  var TooltipPopover = class {
    constructor() {
      // ---------------------------------------------------------
      // Tooltip
      // ---------------------------------------------------------
      __publicField(this, "handleMouseOver", (e) => {
        const target = e.target.closest("[data-tooltip]");
        if (!target || target.contains(e.relatedTarget)) return;
        this.showTooltip(target);
      });
      __publicField(this, "handleMouseOut", (e) => {
        const target = e.target.closest("[data-tooltip]");
        if (!target || target.contains(e.relatedTarget)) return;
        this.hideTooltip(target);
      });
      __publicField(this, "handleFocusIn", (e) => {
        const target = e.target.closest("[data-tooltip]");
        if (target) this.showTooltip(target);
      });
      __publicField(this, "handleFocusOut", (e) => {
        const target = e.target.closest("[data-tooltip]");
        if (!target || target.contains(e.relatedTarget)) return;
        this.hideTooltip(target);
      });
      // ---------------------------------------------------------
      // Popover
      // ---------------------------------------------------------
      __publicField(this, "handleClick", (e) => {
        const toggle = e.target.closest('[data-toggle="popover"]');
        if (toggle) {
          this.togglePopover(toggle, e);
          return;
        }
        if (this.activePopover && !this.activePopover.contains(e.target) && !this.activePopover.__trigger.contains(e.target)) {
          this.hidePopover();
        }
      });
      __publicField(this, "handleResize", () => {
        this.scheduleReposition();
      });
      __publicField(this, "handleScroll", () => {
        this.scheduleReposition();
      });
      // ---------------------------------------------------------
      // Keyboard
      // ---------------------------------------------------------
      __publicField(this, "handleKeydown", (e) => {
        if (e.key !== "Escape") return;
        this.hideTooltip();
        this.hidePopover();
      });
      this.activeTooltip = null;
      this.activePopover = null;
      this.resizeFrame = null;
    }
    init() {
      document.addEventListener("mouseover", this.handleMouseOver);
      document.addEventListener("mouseout", this.handleMouseOut);
      document.addEventListener("focusin", this.handleFocusIn);
      document.addEventListener("focusout", this.handleFocusOut);
      document.addEventListener("click", this.handleClick);
      document.addEventListener("keydown", this.handleKeydown);
      window.addEventListener("resize", this.handleResize);
      window.addEventListener("scroll", this.handleScroll, true);
    }
    initStates() {
    }
    showTooltip(target) {
      const content = target.dataset.tooltip;
      if (!content) return;
      const tooltip = this.getTooltipElement();
      tooltip.textContent = content;
      tooltip.classList.remove("opacity-0");
      this.activeTooltip = tooltip;
      tooltip.__trigger = target;
      this.position(tooltip, target, target.dataset.tooltipPlacement || "top");
    }
    getTooltipElement() {
      let tooltip = document.querySelector("#spice-global-tooltip");
      if (!tooltip) {
        tooltip = document.createElement("div");
        tooltip.id = "spice-global-tooltip";
        tooltip.setAttribute("role", "tooltip");
        tooltip.className = [
          "fixed z-50 px-2.5 py-1.5",
          "text-xs font-medium text-white",
          "bg-slate-900 rounded-lg shadow-lg",
          "pointer-events-none transition-opacity duration-150",
          "opacity-0"
        ].join(" ");
        document.body.appendChild(tooltip);
      }
      return tooltip;
    }
    hideTooltip(target = null) {
      if (!this.activeTooltip) return;
      if (target && this.activeTooltip.__trigger !== target) return;
      this.activeTooltip.classList.add("opacity-0");
      this.activeTooltip = null;
    }
    togglePopover(toggle, e) {
      e.preventDefault();
      e.stopPropagation();
      if (this.activePopover?.__trigger === toggle) {
        this.hidePopover();
        return;
      }
      this.hidePopover();
      const popover = this.createPopover(toggle);
      if (!popover) return;
      document.body.appendChild(popover);
      this.activePopover = popover;
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-controls", popover.id);
      this.position(
        popover,
        toggle,
        toggle.dataset.popoverPlacement || "bottom"
      );
      popover.dispatchEvent(new CustomEvent("spice:popover:shown", {
        bubbles: true,
        detail: { trigger: toggle, popover }
      }));
    }
    createPopover(toggle) {
      const popover = document.createElement("div");
      popover.id = `spice-popover-${crypto.randomUUID()}`;
      popover.setAttribute("role", "dialog");
      popover.setAttribute("aria-modal", "false");
      popover.className = [
        "fixed z-50 w-64 max-w-[calc(100vw-1rem)]",
        "rounded-xl border border-slate-200",
        "bg-white p-3.5 shadow-xl text-sm",
        "transition-opacity duration-150"
      ].join(" ");
      const templateSelector = toggle.dataset.popoverTemplate;
      if (templateSelector) {
        let template;
        try {
          template = document.querySelector(templateSelector);
        } catch {
          return null;
        }
        if (!template || !(template instanceof HTMLTemplateElement)) {
          console.warn(`Popover template not found: ${templateSelector}`);
          return null;
        }
        popover.appendChild(template.content.cloneNode(true));
      } else {
        this.createSimpleContent(popover, toggle);
      }
      if (!popover.hasChildNodes()) return null;
      popover.__trigger = toggle;
      return popover;
    }
    createSimpleContent(popover, toggle) {
      const title = toggle.dataset.popoverTitle || "";
      const content = toggle.dataset.popoverContent || toggle.dataset.popover || "";
      if (title) {
        const heading = document.createElement("div");
        heading.className = [
          "font-bold text-slate-900 mb-1",
          "pb-1.5 border-b border-slate-100"
        ].join(" ");
        heading.textContent = title;
        popover.appendChild(heading);
      }
      if (content) {
        const body = document.createElement("div");
        body.className = "text-xs text-slate-600 leading-relaxed";
        body.textContent = content;
        popover.appendChild(body);
      }
    }
    hidePopover() {
      if (!this.activePopover) return;
      const popover = this.activePopover;
      const trigger = popover.__trigger;
      if (trigger) {
        trigger.setAttribute("aria-expanded", "false");
        trigger.removeAttribute("aria-controls");
      }
      popover.dispatchEvent(new CustomEvent("spice:popover:hidden", {
        bubbles: true,
        detail: { trigger, popover }
      }));
      popover.remove();
      this.activePopover = null;
    }
    // ---------------------------------------------------------
    // Positioning
    // ---------------------------------------------------------
    position(element, trigger, placement = "bottom") {
      const rect = trigger.getBoundingClientRect();
      const elementRect = element.getBoundingClientRect();
      const gap = 8;
      const padding = 8;
      const placements = {
        top: {
          top: rect.top - elementRect.height - gap,
          left: rect.left + (rect.width - elementRect.width) / 2
        },
        bottom: {
          top: rect.bottom + gap,
          left: rect.left + (rect.width - elementRect.width) / 2
        },
        left: {
          top: rect.top + (rect.height - elementRect.height) / 2,
          left: rect.left - elementRect.width - gap
        },
        right: {
          top: rect.top + (rect.height - elementRect.height) / 2,
          left: rect.right + gap
        }
      };
      let position = placements[placement] || placements.bottom;
      if (position.top + elementRect.height > window.innerHeight - padding && placement === "bottom") {
        position = placements.top;
      } else if (position.top < padding && placement === "top") {
        position = placements.bottom;
      }
      if (position.left < padding && placement === "left") {
        position = placements.right;
      } else if (position.left + elementRect.width > window.innerWidth - padding && placement === "right") {
        position = placements.left;
      }
      const maxLeft = Math.max(
        padding,
        window.innerWidth - elementRect.width - padding
      );
      const maxTop = Math.max(
        padding,
        window.innerHeight - elementRect.height - padding
      );
      element.style.top = `${Math.max(padding, Math.min(position.top, maxTop))}px`;
      element.style.left = `${Math.max(padding, Math.min(position.left, maxLeft))}px`;
    }
    scheduleReposition() {
      if (this.resizeFrame) return;
      this.resizeFrame = requestAnimationFrame(() => {
        this.resizeFrame = null;
        if (this.activeTooltip?.__trigger?.isConnected) {
          this.position(
            this.activeTooltip,
            this.activeTooltip.__trigger,
            this.activeTooltip.__trigger.dataset.tooltipPlacement || "top"
          );
        }
        if (this.activePopover?.__trigger?.isConnected) {
          this.position(
            this.activePopover,
            this.activePopover.__trigger,
            this.activePopover.__trigger.dataset.popoverPlacement || "bottom"
          );
        }
      });
    }
    // ---------------------------------------------------------
    // Lifecycle
    // ---------------------------------------------------------
    destroy() {
      document.removeEventListener("mouseover", this.handleMouseOver);
      document.removeEventListener("mouseout", this.handleMouseOut);
      document.removeEventListener("focusin", this.handleFocusIn);
      document.removeEventListener("focusout", this.handleFocusOut);
      document.removeEventListener("click", this.handleClick);
      document.removeEventListener("keydown", this.handleKeydown);
      window.removeEventListener("resize", this.handleResize);
      window.removeEventListener("scroll", this.handleScroll, true);
      if (this.resizeFrame) {
        cancelAnimationFrame(this.resizeFrame);
        this.resizeFrame = null;
      }
      this.hideTooltip();
      this.hidePopover();
      document.querySelector("#spice-global-tooltip")?.remove();
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/components/toast.js
  var Toast = class {
    constructor() {
      /**
       * Handle toast and alert dismissal.
       */
      __publicField(this, "handleClick", (e) => {
        const dismiss = e.target.closest(
          '[data-dismiss="toast"], [data-dismiss="alert"]'
        );
        if (!dismiss) return;
        e.preventDefault();
        this.handleDismiss(dismiss);
      });
    }
    /**
     * Initialize toast component.
     */
    init() {
      this.initStates();
      document.addEventListener("click", this.handleClick);
    }
    /**
     * Show a programmatic toast.
     *
     * @param {Object} options
     * @param {string} options.message
     * @param {string} options.type
     * @param {number} options.duration
     */
    show({ message = "", type = "info", duration = 5e3 } = {}) {
      const container = document.querySelector("spice-toast");
      const template = container?.querySelector("template");
      if (!container || !template) {
        console.warn("Toast container or template is missing.");
        return null;
      }
      const fragment = template.content.cloneNode(true);
      const toast = fragment.querySelector("[data-toast]");
      if (!toast) {
        console.warn("Toast template must contain an element with [data-toast].");
        return null;
      }
      toast.dataset.type = type;
      const messageElement = toast.querySelector("[data-toast-message]");
      if (messageElement) {
        messageElement.textContent = message;
      }
      if (duration !== void 0 && duration !== null) {
        toast.dataset.duration = String(duration);
      }
      container.appendChild(fragment);
      this.initToasts(toast);
      return toast;
    }
    /**
     * Initialize toast states.
     */
    initStates(root = document) {
      this.initToasts(root);
    }
    /**
     * Initialize server-rendered and dynamically inserted toasts.
     */
    initToasts(root = document) {
      const toasts = [];
      if (root.matches?.("[data-toast]")) {
        toasts.push(root);
      }
      toasts.push(...root.querySelectorAll("[data-toast]"));
      toasts.forEach((toast) => {
        if (toast.dataset.initialized === "true") return;
        toast.dataset.initialized = "true";
        requestAnimationFrame(() => {
          toast.classList.remove(
            "translate-y-2",
            "translate-y-4",
            "opacity-0"
          );
        });
        const duration = toast.dataset.duration === void 0 ? 5e3 : Number.parseInt(toast.dataset.duration, 10);
        if (Number.isFinite(duration) && duration > 0) {
          toast.dataset.timer = setTimeout(() => {
            this.dismiss(toast);
          }, duration);
        }
      });
    }
    /**
     * Dismiss a toast or alert.
     */
    handleDismiss(target) {
      const toast = target.closest("[data-toast]");
      if (toast) {
        this.dismiss(toast);
        return true;
      }
      const alert = target.closest("[data-alert]");
      if (alert) {
        this.dismissAlert(alert);
        return true;
      }
      return false;
    }
    /**
     * Dismiss toast with animation.
     */
    dismiss(toast) {
      if (!toast || toast.dataset.dismissing === "true") return;
      toast.dataset.dismissing = "true";
      if (toast.dataset.timer) {
        clearTimeout(Number(toast.dataset.timer));
        delete toast.dataset.timer;
      }
      toast.classList.add("translate-y-2", "opacity-0");
      setTimeout(() => {
        toast.remove();
      }, 200);
    }
    /**
     * Dismiss alert with animation.
     */
    dismissAlert(alert) {
      if (!alert || alert.dataset.dismissing === "true") return;
      alert.dataset.dismissing = "true";
      alert.classList.add(
        "opacity-0",
        "scale-95",
        "transition-all",
        "duration-150"
      );
      setTimeout(() => {
        alert.remove();
      }, 150);
    }
    /**
     * Destroy component listeners and timers.
     */
    destroy() {
      document.removeEventListener("click", this.handleClick);
      document.querySelectorAll("[data-toast]").forEach((toast) => {
        if (toast.dataset.timer) {
          clearTimeout(Number(toast.dataset.timer));
          delete toast.dataset.timer;
        }
      });
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/ui.js
  var SpiceUI = class {
    constructor() {
      /**
       * Handle HTMX content updates.
       */
      __publicField(this, "handleAfterSwap", (e) => {
        const root = e.target;
        this.initStates(root);
        const modal = root.matches?.("[data-modal]") ? root : root.querySelector?.("[data-modal]");
        if (modal?.dataset.autoOpen === "true") {
          this.components.modal.show(modal);
        }
      });
      /**
       * Handle programmatic toast notifications.
       */
      __publicField(this, "handleShowAlert", (event) => {
        this.components.toast.show(event.detail);
      });
      this.components = {
        modal: new Modal(),
        offcanvas: new Offcanvas(),
        sidebar: new Sidebar(),
        dropdown: new Dropdown(),
        tabs: new Tabs(),
        collapse: new Collapse(),
        tooltipPopover: new TooltipPopover(),
        toast: new Toast()
      };
      this.init();
    }
    /**
     * Initialize all components.
     */
    init() {
      Object.values(this.components).forEach((component) => {
        component.init();
      });
      this.initListeners();
    }
    /**
     * Initialize dynamically inserted content.
     */
    initStates(root = document) {
      Object.values(this.components).forEach((component) => {
        component.initStates?.(root);
      });
    }
    /**
     * Register global integrations.
     */
    initListeners() {
      document.addEventListener("htmx:afterSwap", this.handleAfterSwap);
      document.body.addEventListener("show-alert", this.handleShowAlert);
    }
    /**
     * Destroy all components and global listeners.
     */
    destroy() {
      document.removeEventListener("htmx:afterSwap", this.handleAfterSwap);
      document.body.removeEventListener("show-alert", this.handleShowAlert);
      Object.values(this.components).forEach((component) => {
        component.destroy?.();
      });
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/socket.js
  var DEFAULT_OPTIONS = {
    path: "/ws/realtime/",
    host: null,
    port: null,
    protocol: null,
    reconnect: true,
    reconnectDelay: 1e3,
    maxReconnectDelay: 3e4,
    maxRetries: Infinity
  };
  var SpiceSocket = class {
    constructor(options = {}) {
      this.options = {
        ...DEFAULT_OPTIONS,
        ...options,
        maxRetries: options.maxRetries === null ? Infinity : options.maxRetries ?? DEFAULT_OPTIONS.maxRetries
      };
      this.listeners = /* @__PURE__ */ new Map();
      this.socket = null;
      this.status = "disconnected";
      this.retries = 0;
      this.reconnectTimer = null;
      this.connectionPromise = null;
      this.settleConnection = null;
      this.manualDisconnect = false;
      this.generation = 0;
    }
    // Configuration
    configure(options = {}) {
      this.options = {
        ...this.options,
        ...options,
        maxRetries: options.maxRetries === null ? Infinity : options.maxRetries ?? this.options.maxRetries
      };
      return this;
    }
    getUrl() {
      const {
        path,
        host,
        port,
        protocol
      } = this.options;
      const url = new URL(path, window.location.href);
      url.protocol = protocol || (window.location.protocol === "https:" ? "wss:" : "ws:");
      if (host) {
        url.hostname = host;
      }
      if (port !== null && port !== void 0) {
        url.port = String(port);
      }
      return url.toString();
    }
    // Connection
    connect() {
      const WebSocketClass = globalThis.WebSocket;
      if (!WebSocketClass) {
        return Promise.reject(
          new Error("SpiceSocket: WebSocket is not supported.")
        );
      }
      if (this.socket?.readyState === WebSocketClass.OPEN) {
        return Promise.resolve(this);
      }
      if (this.connectionPromise) {
        return this.connectionPromise;
      }
      if (this.socket?.readyState === WebSocketClass.CLOSING) {
        return Promise.reject(
          new Error("SpiceSocket: previous connection is closing.")
        );
      }
      this.manualDisconnect = false;
      this.clearReconnectTimer();
      const generation = ++this.generation;
      this.setStatus("connecting");
      let socket2;
      try {
        socket2 = new WebSocketClass(this.getUrl());
        this.socket = socket2;
      } catch (error) {
        this.socket = null;
        this.setStatus("disconnected", error);
        this.scheduleReconnect();
        return Promise.reject(error);
      }
      this.connectionPromise = new Promise((resolve, reject) => {
        let settled = false;
        const settle = (callback, value) => {
          if (settled) return;
          settled = true;
          if (this.generation === generation) {
            this.connectionPromise = null;
            this.settleConnection = null;
          }
          callback(value);
        };
        this.settleConnection = (error) => {
          settle(reject, error);
        };
        socket2.addEventListener("open", (event) => {
          if (generation !== this.generation) return;
          const wasReconnecting = this.retries > 0;
          this.retries = 0;
          this.setStatus("connected", event);
          this.emit("open", event);
          if (wasReconnecting) {
            this.emit("reconnected", event);
          }
          settle(resolve, this);
        });
        socket2.addEventListener("message", (event) => {
          if (generation !== this.generation) return;
          this.handleMessage(event);
        });
        socket2.addEventListener("error", (event) => {
          if (generation !== this.generation) return;
          this.emit("error", event);
        });
        socket2.addEventListener("close", (event) => {
          if (generation !== this.generation) return;
          this.socket = null;
          this.setStatus("disconnected", event);
          this.emit("close", event);
          settle(
            reject,
            new Error(
              `SpiceSocket: connection closed (${event.code}).`
            )
          );
          if (!this.manualDisconnect) {
            this.scheduleReconnect();
          }
        });
      });
      return this.connectionPromise;
    }
    disconnect(code = 1e3, reason = "Client disconnected") {
      this.manualDisconnect = true;
      this.clearReconnectTimer();
      this.generation++;
      this.settleConnection?.(
        new Error("SpiceSocket: connection cancelled.")
      );
      this.connectionPromise = null;
      this.settleConnection = null;
      const socket2 = this.socket;
      this.socket = null;
      if (socket2 && globalThis.WebSocket && socket2.readyState !== globalThis.WebSocket.CLOSED && socket2.readyState !== globalThis.WebSocket.CLOSING) {
        socket2.close(code, reason);
      }
      this.setStatus("disconnected");
      return this;
    }
    destroy() {
      this.disconnect();
      this.listeners.clear();
      this.retries = 0;
      return this;
    }
    // Messaging
    send(event, data = {}) {
      if (!this.socket || !globalThis.WebSocket || this.socket.readyState !== globalThis.WebSocket.OPEN) {
        return false;
      }
      this.socket.send(JSON.stringify({ event, data }));
      return true;
    }
    handleMessage(message) {
      let data;
      try {
        data = JSON.parse(message.data);
      } catch {
        this.emit("message", message.data);
        return;
      }
      this.emit("message", data);
      if (data && typeof data === "object" && typeof data.event === "string") {
        this.emit(data.event, data.data);
      }
    }
    // Events
    on(event, callback) {
      if (typeof callback !== "function") {
        throw new TypeError(
          "SpiceSocket: listener must be a function."
        );
      }
      if (!this.listeners.has(event)) {
        this.listeners.set(event, /* @__PURE__ */ new Set());
      }
      this.listeners.get(event).add(callback);
      return this;
    }
    once(event, callback) {
      const wrapper = (...args) => {
        this.off(event, wrapper);
        callback(...args);
      };
      return this.on(event, wrapper);
    }
    off(event, callback) {
      if (!this.listeners.has(event)) {
        return this;
      }
      if (callback) {
        const callbacks = this.listeners.get(event);
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.listeners.delete(event);
        }
      } else {
        this.listeners.delete(event);
      }
      return this;
    }
    emit(event, ...args) {
      const callbacks = this.listeners.get(event);
      if (!callbacks) {
        return this;
      }
      for (const callback of [...callbacks]) {
        try {
          callback(...args);
        } catch (error) {
          globalThis.setTimeout(() => {
            throw error;
          }, 0);
        }
      }
      return this;
    }
    // Reconnection
    scheduleReconnect() {
      const {
        reconnect,
        reconnectDelay,
        maxReconnectDelay,
        maxRetries
      } = this.options;
      if (this.manualDisconnect || !reconnect || this.reconnectTimer !== null) {
        return;
      }
      if (this.retries >= maxRetries) {
        this.emit("reconnect_failed", {
          attempts: this.retries
        });
        return;
      }
      const delay = Math.min(
        reconnectDelay * Math.pow(2, this.retries),
        maxReconnectDelay
      );
      this.retries++;
      this.setStatus("reconnecting", {
        attempt: this.retries,
        delay
      });
      this.reconnectTimer = globalThis.setTimeout(() => {
        this.reconnectTimer = null;
        this.connect().catch(() => {
        });
      }, delay);
    }
    clearReconnectTimer() {
      if (this.reconnectTimer !== null) {
        globalThis.clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    }
    // Status
    setStatus(status, details = null) {
      const previousStatus = this.status;
      this.status = status;
      const payload = {
        status,
        previousStatus,
        details
      };
      this.emit("status", payload);
      if (previousStatus !== status) {
        this.emit(status, payload);
      }
      return this;
    }
    // State
    get connected() {
      return !!this.socket && !!globalThis.WebSocket && this.socket.readyState === globalThis.WebSocket.OPEN;
    }
    get connecting() {
      return this.status === "connecting";
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/router.js
  var SpiceRouter = class {
    constructor(options = {}) {
      this.options = options;
      this.started = false;
      this.observer = null;
      this.boundHandlers = {
        beforeRequest: this.handleBeforeRequest.bind(this),
        beforeSwap: this.handleBeforeSwap.bind(this),
        afterSwap: this.handleAfterSwap.bind(this),
        afterRequest: this.handleAfterRequest.bind(this),
        pushedIntoHistory: this.handlePushedIntoHistory.bind(this),
        requestError: this.handleRequestError.bind(this),
        popstate: this.handlePopState.bind(this)
      };
    }
    start() {
      if (this.started) {
        this.processDocument();
        return this;
      }
      this.initListeners();
      this.observeDOM();
      this.started = true;
      this.processDocument();
      emit(document, ROUTER_EVENTS.READY, { router: this });
      return this;
    }
    stop() {
      if (!this.started) return this;
      document.removeEventListener("htmx:beforeRequest", this.boundHandlers.beforeRequest);
      document.removeEventListener("htmx:beforeSwap", this.boundHandlers.beforeSwap);
      document.removeEventListener("htmx:afterSwap", this.boundHandlers.afterSwap);
      document.removeEventListener("htmx:afterRequest", this.boundHandlers.afterRequest);
      document.removeEventListener("htmx:pushedIntoHistory", this.boundHandlers.pushedIntoHistory);
      document.removeEventListener("htmx:responseError", this.boundHandlers.requestError);
      document.removeEventListener("htmx:sendError", this.boundHandlers.requestError);
      document.removeEventListener("htmx:timeout", this.boundHandlers.requestError);
      document.removeEventListener("htmx:sendAbort", this.boundHandlers.requestError);
      window.removeEventListener("popstate", this.boundHandlers.popstate);
      this.observer?.disconnect();
      this.observer = null;
      this.started = false;
      return this;
    }
    updateOptions(options = {}) {
      this.options = { ...this.options, ...options };
      this.refreshActiveLinks();
      return this;
    }
    processDocument() {
      this.refreshActiveLinks();
    }
    refreshActiveLinks() {
      const currentURL = new URL(window.location.href);
      const currentPath = normalizePath(currentURL.pathname);
      document.querySelectorAll("a[data-spice-link]").forEach((anchor) => {
        let active = false;
        try {
          const linkURL = new URL(anchor.href, window.location.href);
          const linkPath = normalizePath(linkURL.pathname);
          const exact = anchor.dataset.spiceExact === "true";
          const matchQuery = anchor.dataset.spiceMatchQuery === "true";
          if (exact) {
            active = linkPath === currentPath;
          } else {
            active = linkPath === "/" || linkPath === currentPath || currentPath.startsWith(`${linkPath}/`);
          }
          if (active && matchQuery && linkURL.search !== currentURL.search) {
            active = false;
          }
        } catch {
          active = false;
        }
        const activeClass = anchor.dataset.spiceActiveClass || "active";
        anchor.classList.toggle(activeClass, active);
        if (active) {
          anchor.setAttribute("aria-current", "page");
        } else {
          anchor.removeAttribute("aria-current");
        }
      });
    }
    initListeners() {
      document.addEventListener("htmx:beforeRequest", this.boundHandlers.beforeRequest);
      document.addEventListener("htmx:beforeSwap", this.boundHandlers.beforeSwap);
      document.addEventListener("htmx:afterSwap", this.boundHandlers.afterSwap);
      document.addEventListener("htmx:afterRequest", this.boundHandlers.afterRequest);
      document.addEventListener("htmx:pushedIntoHistory", this.boundHandlers.pushedIntoHistory);
      document.addEventListener("htmx:responseError", this.boundHandlers.requestError);
      document.addEventListener("htmx:sendError", this.boundHandlers.requestError);
      document.addEventListener("htmx:timeout", this.boundHandlers.requestError);
      document.addEventListener("htmx:sendAbort", this.boundHandlers.requestError);
      window.addEventListener("popstate", this.boundHandlers.popstate);
    }
    getTriggerElement(detail) {
      return detail?.requestConfig?.elt || detail?.elt || null;
    }
    isRouterRequest(detail) {
      const element = this.getTriggerElement(detail);
      return Boolean(element?.matches?.("[data-spice-navigation]"));
    }
    handleBeforeRequest(event) {
      const detail = event.detail || {};
      if (!this.isRouterRequest(detail)) return;
      const element = this.getTriggerElement(detail);
      const beforeEvent = emit(
        element,
        ROUTER_EVENTS.BEFORE_NAVIGATE,
        { element, target: detail.target, xhr: detail.xhr, requestConfig: detail.requestConfig },
        { cancelable: true }
      );
      if (beforeEvent.defaultPrevented) {
        event.preventDefault();
      }
    }
    handleBeforeSwap(event) {
      const detail = event.detail || {};
      if (!this.isRouterRequest(detail)) return;
      const element = this.getTriggerElement(detail);
      const beforeEvent = emit(
        element,
        ROUTER_EVENTS.BEFORE_SWAP,
        { element, target: detail.target, xhr: detail.xhr, requestConfig: detail.requestConfig },
        { cancelable: true }
      );
      if (beforeEvent.defaultPrevented) {
        event.preventDefault();
      }
    }
    handleAfterSwap(event) {
      const detail = event.detail || {};
      if (!this.isRouterRequest(detail)) return;
      const element = this.getTriggerElement(detail);
      const target = detail.target || event.target;
      emit(target, ROUTER_EVENTS.AFTER_SWAP, { element, target, xhr: detail.xhr });
      emit(target, ROUTER_EVENTS.NAVIGATE, { element, target, url: window.location.href, xhr: detail.xhr });
      this.refreshActiveLinks();
    }
    handleAfterRequest(event) {
      const detail = event.detail || {};
      if (!this.isRouterRequest(detail)) return;
      if (detail.failed) {
        this.emitNavigationError(detail);
      }
    }
    handleRequestError(event) {
      const detail = event.detail || {};
      if (!this.isRouterRequest(detail)) return;
      this.emitNavigationError(detail);
    }
    emitNavigationError(detail) {
      const element = this.getTriggerElement(detail);
      emit(element, ROUTER_EVENTS.NAVIGATION_ERROR, {
        element,
        xhr: detail.xhr,
        status: detail.xhr?.status,
        error: detail.error,
        failed: detail.failed
      });
    }
    handlePushedIntoHistory(event) {
      this.refreshActiveLinks();
      emit(document, ROUTER_EVENTS.LOCATION_CHANGE, {
        url: window.location.href,
        source: "htmx",
        detail: event.detail
      });
    }
    handlePopState() {
      this.refreshActiveLinks();
      emit(document, ROUTER_EVENTS.LOCATION_CHANGE, {
        url: window.location.href,
        source: "popstate"
      });
    }
    observeDOM() {
      if (this.observer || !document.body) return;
      this.observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
          if (mutation.addedNodes.length > 0) {
            for (const node of mutation.addedNodes) {
              if (node.nodeType === Node.ELEMENT_NODE) {
                if (window.htmx) {
                  window.htmx.process(node);
                }
              }
            }
          }
        }
      });
      this.observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/table.js
  var SpiceTable = class {
    constructor(element) {
      this.el = element;
      this.selected = /* @__PURE__ */ new Set();
      this.contextMenu = {
        x: 0,
        y: 0,
        recordId: null
      };
      this.init();
    }
    init() {
      this.el.addEventListener("click", (e) => {
        if (!e.target.closest("[data-context-menu]")) {
          this.closeContextMenu();
        }
        const actionEl = e.target.closest("[data-action]");
        if (actionEl) {
          const action = actionEl.dataset.action;
          if (action === "clear-selection") {
            this.clearSelection();
          }
        }
        const row = e.target.closest("[data-table-row]");
        if (!row || !this.el.contains(row)) return;
        if (e.target.closest('a, button, input, select, textarea, label, [data-no-row-select], [contenteditable="true"], [role="button"], [role="menuitem"]')) {
          return;
        }
        const isNavigation = row.dataset.navigation === "true";
        if (isNavigation) {
          return;
        }
        const checkbox = row.querySelector("[data-row-checkbox]");
        if (!checkbox || checkbox.disabled) return;
        checkbox.checked = !checkbox.checked;
        checkbox.dispatchEvent(
          new Event("change", { bubbles: true })
        );
      });
      this.el.addEventListener("contextmenu", (e) => {
        const row = e.target.closest("[data-table-row]");
        if (row && this.el.contains(row)) {
          e.preventDefault();
          const recordId = row.dataset.objectId;
          this.openContextMenu(e, recordId);
        }
      });
      this.el.addEventListener("change", (e) => {
        const actionEl = e.target.closest("[data-action]");
        if (!actionEl) return;
        const action = actionEl.dataset.action;
        if (action === "toggle-all") {
          this.toggleAll(actionEl.checked);
        } else if (action === "toggle-row") {
          this.toggleRow(actionEl.value, actionEl.checked);
        }
      });
      window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          this.closeContextMenu();
        }
      });
      window.addEventListener("scroll", () => {
        this.closeContextMenu();
      }, { passive: true });
      this.syncState();
    }
    // =========================================================================
    // CONTEXT MENU & [id] PLACEHOLDER RESOLUTION
    // =========================================================================
    openContextMenu(event, id) {
      const width = 224;
      const height = 260;
      this.contextMenu.recordId = id;
      this.contextMenu.x = Math.max(
        8,
        Math.min(event.clientX, window.innerWidth - width - 8)
      );
      this.contextMenu.y = Math.max(
        8,
        Math.min(event.clientY, window.innerHeight - height - 8)
      );
      const menuEl = this.el.querySelector("[data-context-menu]");
      if (menuEl) {
        menuEl.dataset.activeRecordId = id;
        menuEl.style.left = `${this.contextMenu.x}px`;
        menuEl.style.top = `${this.contextMenu.y}px`;
        menuEl.classList.remove("hidden");
        menuEl.querySelectorAll("a, button").forEach((el) => {
          const targetAttrs = [
            "hx-get",
            "hx-post",
            "hx-delete",
            "hx-patch",
            "hx-put",
            "href"
          ];
          targetAttrs.forEach((attr) => {
            if (el.hasAttribute(attr)) {
              const originalAttrKey = `data-original-${attr.replace("-", "")}`;
              if (!el.hasAttribute(originalAttrKey)) {
                el.setAttribute(
                  originalAttrKey,
                  el.getAttribute(attr)
                );
              }
              const template = el.getAttribute(originalAttrKey);
              const resolvedUrl = template.replaceAll("[id]", id);
              el.setAttribute(attr, resolvedUrl);
            }
          });
          if (window.htmx) {
            htmx.process(el);
          }
        });
      }
    }
    closeContextMenu() {
      const menuEl = this.el.querySelector("[data-context-menu]");
      if (menuEl) {
        menuEl.classList.add("hidden");
      }
    }
    // =========================================================================
    // SELECTION & STATE SYNCHRONIZATION
    // =========================================================================
    toggleAll(checked) {
      const checkboxes = this.el.querySelectorAll(
        "[data-row-checkbox]:not(:disabled)"
      );
      checkboxes.forEach((cb) => {
        cb.checked = checked;
        if (checked) {
          this.selected.add(cb.value);
        } else {
          this.selected.delete(cb.value);
        }
        this.syncRow(cb);
      });
      this.syncHeaderCheckbox();
      this.syncState();
    }
    toggleRow(id, checked) {
      if (checked) {
        this.selected.add(id);
      } else {
        this.selected.delete(id);
      }
      const checkbox = Array.from(
        this.el.querySelectorAll("[data-row-checkbox]")
      ).find((cb) => cb.value === id);
      if (checkbox) {
        this.syncRow(checkbox);
      }
      this.syncHeaderCheckbox();
      this.syncState();
    }
    /**
     * Synchronize checkbox state with row highlighting.
     */
    syncRow(checkbox) {
      const row = checkbox.closest("[data-table-row]");
      if (!row) return;
      row.classList.toggle("is-selected", checkbox.checked);
    }
    /**
     * Synchronize header checkbox checked and indeterminate states.
     */
    syncHeaderCheckbox() {
      const selectAll = this.el.querySelector(
        '[data-action="toggle-all"]'
      );
      if (!selectAll) return;
      const checkboxes = Array.from(
        this.el.querySelectorAll(
          "[data-row-checkbox]:not(:disabled)"
        )
      );
      const selectedCount = checkboxes.filter(
        (cb) => cb.checked
      ).length;
      selectAll.checked = checkboxes.length > 0 && selectedCount === checkboxes.length;
      selectAll.indeterminate = selectedCount > 0 && selectedCount < checkboxes.length;
    }
    clearSelection() {
      this.selected.clear();
      this.el.querySelectorAll("[data-row-checkbox]").forEach((cb) => {
        cb.checked = false;
        this.syncRow(cb);
      });
      const selectAll = this.el.querySelector(
        '[data-action="toggle-all"]'
      );
      if (selectAll) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
      }
      this.syncState();
    }
    // =========================================================================
    // BULK ACTION STATE & HIDDEN INPUT SYNCHRONIZATION
    // =========================================================================
    syncState() {
      const count = this.selected.size;
      const countEl = this.el.querySelector("[data-selected-count]");
      if (countEl) {
        countEl.textContent = count;
      }
      const bulkBar = this.el.querySelector("[data-bulk-actions]");
      if (bulkBar) {
        bulkBar.classList.toggle("hidden", count === 0);
        if (count === 0) {
          const bulkDropdown = bulkBar.querySelector(
            "[data-dropdown-menu]"
          );
          if (bulkDropdown && !bulkDropdown.classList.contains("hidden")) {
            bulkDropdown.classList.add("hidden");
          }
        }
      }
      const container = this.el.querySelector("[data-hidden-inputs]");
      if (container) {
        container.innerHTML = "";
        this.selected.forEach((id) => {
          const input = document.createElement("input");
          input.type = "hidden";
          input.name = container.dataset.paramName || "selected_objects";
          input.value = id;
          container.appendChild(input);
        });
      }
      this.syncHeaderCheckbox();
    }
  };

  // ../djangospice/src/djangospice/spice/static/spice/js/lookup.js
  var SELECTOR = "select[data-spice-lookup]";
  var EVENT_PREFIX = "spice:lookup";
  var DEFAULTS2 = Object.freeze({
    delay: 250,
    pageSize: 20,
    minimumInputLength: 0,
    searchParam: "q",
    pageParam: "page",
    pageSizeParam: "page_size",
    placeholder: "Select...",
    searchPlaceholder: "Search...",
    allowClear: true,
    tokenHeader: "X-Lookup-Token"
  });
  var instances = /* @__PURE__ */ new WeakMap();
  function parseBoolean2(value, fallback) {
    if (value === void 0 || value === null || value === "") {
      return fallback;
    }
    return String(value).toLowerCase() === "true";
  }
  function parseInteger(value, fallback) {
    const parsed = Number.parseInt(value, 10);
    return Number.isFinite(parsed) ? parsed : fallback;
  }
  function parseDependencies(value) {
    if (!value) return [];
    return String(value).split(",").map((item) => item.trim()).filter(Boolean);
  }
  function debounce(callback, delay) {
    let timer = null;
    const debounced = function(...args) {
      window.clearTimeout(timer);
      timer = window.setTimeout(
        () => callback.apply(this, args),
        delay
      );
    };
    debounced.cancel = function() {
      window.clearTimeout(timer);
      timer = null;
    };
    return debounced;
  }
  function createElement(tag, className, attributes = {}) {
    const element = document.createElement(tag);
    if (className) {
      element.className = className;
    }
    for (const [name, value] of Object.entries(attributes)) {
      if (value === null || value === void 0) continue;
      if (value === true) {
        element.setAttribute(name, "");
      } else if (value !== false) {
        element.setAttribute(name, String(value));
      }
    }
    return element;
  }
  var SpiceLookup = class {
    constructor(select) {
      this.select = select;
      this.destroyed = false;
      this.loading = false;
      this.abortController = null;
      this.requestSequence = 0;
      this.page = 1;
      this.hasNext = false;
      this.highlightedIndex = -1;
      this.dependencies = [];
      this.dependencyListeners = [];
      this.config = this.readConfig();
      this.initialOptions = this.captureOptions();
      this.selectedValues = this.getSelectedValues();
      this.initialize();
    }
    readConfig() {
      const data = this.select.dataset;
      return {
        url: data.lookupUrl || "",
        name: data.lookupName || this.select.name || "",
        delay: parseInteger(data.lookupDelay, DEFAULTS2.delay),
        pageSize: parseInteger(
          data.lookupPageSize,
          DEFAULTS2.pageSize
        ),
        minimumInputLength: parseInteger(
          data.lookupMinSearchLength,
          DEFAULTS2.minimumInputLength
        ),
        searchParam: data.lookupSearchParam || DEFAULTS2.searchParam,
        pageParam: data.lookupPageParam || DEFAULTS2.pageParam,
        pageSizeParam: data.lookupPageSizeParam || DEFAULTS2.pageSizeParam,
        placeholder: data.lookupPlaceholder || DEFAULTS2.placeholder,
        searchPlaceholder: data.lookupSearchPlaceholder || DEFAULTS2.searchPlaceholder,
        allowClear: parseBoolean2(
          data.lookupAllowClear,
          DEFAULTS2.allowClear
        ),
        token: data.lookupToken || null,
        tokenHeader: data.lookupTokenHeader || DEFAULTS2.tokenHeader
      };
    }
    initialize() {
      this.dependencies = this.readDependencies();
      this.createInterface();
      if (!this.wrapper) return;
      this.bindEvents();
      this.bindDependencies();
      this.syncDisabledState();
      this.syncFromSelect();
      this.renderInitialResults();
    }
    readDependencies() {
      return parseDependencies(
        this.select.dataset.lookupDependencies
      );
    }
    captureOptions() {
      return Array.from(this.select.options).map((option) => ({
        value: option.value,
        label: option.textContent,
        selected: option.selected,
        disabled: option.disabled
      }));
    }
    hasDependencies() {
      return this.dependencies.length > 0;
    }
    /* --------------------------------------------------------
     * Interface
     * -------------------------------------------------------- */
    createInterface() {
      const parent = this.select.parentNode;
      if (!parent) return;
      this.wrapper = createElement("div", "spice-lookup");
      this.wrapper.dataset.djangospiceLookupWrapper = "";
      this.control = createElement(
        "div",
        "spice-lookup__control"
      );
      this.selection = this.select.multiple ? createElement("div", "spice-lookup__selection") : null;
      this.search = createElement(
        "input",
        "spice-lookup__input",
        {
          type: "search",
          autocomplete: "off",
          role: "combobox",
          "aria-autocomplete": "list",
          "aria-expanded": "false",
          "aria-haspopup": "listbox",
          placeholder: this.config.searchPlaceholder
        }
      );
      this.clearButton = this.config.allowClear ? createElement("button", "spice-lookup__clear", {
        type: "button",
        "aria-label": "Clear selection"
      }) : null;
      if (this.clearButton) {
        this.clearButton.textContent = "\xD7";
      }
      this.listbox = createElement(
        "div",
        "spice-lookup__dropdown",
        {
          role: "listbox",
          tabindex: "-1"
        }
      );
      this.status = createElement(
        "div",
        "spice-lookup__status",
        {
          role: "status",
          "aria-live": "polite"
        }
      );
      this.status.hidden = true;
      if (this.selection) {
        this.control.appendChild(this.selection);
      }
      this.control.appendChild(this.search);
      if (this.clearButton) {
        this.control.appendChild(this.clearButton);
      }
      parent.insertBefore(this.wrapper, this.select);
      this.wrapper.appendChild(this.control);
      this.wrapper.appendChild(this.listbox);
      this.wrapper.appendChild(this.status);
      this.wrapper.appendChild(this.select);
      this.select.classList.add("spice-lookup__native");
      this.listbox.id = this.getListboxId();
      this.search.setAttribute("aria-controls", this.listbox.id);
      this.wrapper.classList.add("is-enhanced");
    }
    getListboxId() {
      if (this.select.id) {
        return `${this.select.id}-lookup-listbox`;
      }
      return `spice-lookup-${Math.random().toString(36).slice(2)}`;
    }
    syncDisabledState() {
      if (!this.wrapper) return;
      const disabled = this.select.disabled || this.hasDependencies() && !this.isDependencySatisfied();
      this.search.disabled = disabled;
      if (this.clearButton) {
        this.clearButton.disabled = disabled;
      }
      this.wrapper.classList.toggle("is-disabled", disabled);
      this.wrapper.setAttribute("aria-disabled", String(disabled));
    }
    renderInitialResults() {
      if (this.hasDependencies()) {
        const initialSelected = this.initialOptions.filter(
          (option) => option.selected && option.value !== ""
        );
        this.clearLookupResults();
        if (this.isDependencySatisfied() && initialSelected.length) {
          this.syncFromSelect();
        } else {
          this.clearDependentOptions();
        }
        this.syncDisabledState();
        this.close();
        return;
      }
      this.renderResults(
        this.initialOptions.filter((option) => option.value !== "").map((option) => ({
          value: option.value,
          label: option.label
        }))
      );
      this.syncFromSelect();
    }
    /* --------------------------------------------------------
     * Events
     * -------------------------------------------------------- */
    bindEvents() {
      this.handleSearch = debounce(
        () => this.searchLookup(),
        this.config.delay
      );
      this.search.addEventListener("input", this.handleSearch);
      this.search.addEventListener("click", () => {
        if (this.select.disabled) return;
        if (this.hasDependencies()) {
          if (!this.isDependencySatisfied()) {
            this.clearLookupResults();
            this.close();
            this.syncDisabledState();
            return;
          }
          this.page = 1;
          this.hasNext = false;
          this.clearLookupResults();
          this.load({
            term: "",
            page: 1,
            replace: true
          });
        }
        this.open();
      });
      this.search.addEventListener("keydown", (event) => {
        this.handleKeydown(event);
      });
      this.listbox.addEventListener("scroll", () => {
        this.checkLoadMore();
      });
      this.listbox.addEventListener("mousedown", (event) => {
        const option = event.target.closest("[data-lookup-option]");
        if (option) event.preventDefault();
      });
      this.listbox.addEventListener("click", (event) => {
        const option = event.target.closest("[data-lookup-option]");
        if (!option) return;
        this.selectResult(
          option.dataset.lookupValue,
          option.textContent
        );
      });
      if (this.selection) {
        this.selection.addEventListener("click", (event) => {
          const removeButton = event.target.closest(
            "[data-lookup-remove]"
          );
          if (!removeButton) return;
          event.stopPropagation();
          this.toggleMultipleValue(
            removeButton.dataset.lookupRemove
          );
        });
      }
      this.select.addEventListener("change", () => {
        this.syncFromSelect();
      });
      this.control.addEventListener("click", (event) => {
        if (event.target.closest("[data-lookup-remove]")) return;
        this.search.focus();
      });
      if (this.clearButton) {
        this.clearButton.addEventListener("click", () => {
          this.clearSelection();
        });
      }
      this.handleDocumentClick = (event) => {
        if (!this.wrapper.contains(event.target)) {
          this.close();
        }
      };
      document.addEventListener(
        "mousedown",
        this.handleDocumentClick
      );
    }
    /* --------------------------------------------------------
     * Dependencies
     * -------------------------------------------------------- */
    bindDependencies() {
      this.unbindDependencies();
      for (const dependency of this.dependencies) {
        const source = this.findDependency(dependency);
        if (!source) continue;
        const handler = () => this.handleDependencyChange();
        source.addEventListener("change", handler);
        this.dependencyListeners.push({
          element: source,
          handler
        });
      }
    }
    unbindDependencies() {
      for (const { element, handler } of this.dependencyListeners) {
        element.removeEventListener("change", handler);
      }
      this.dependencyListeners = [];
    }
    findDependency(name) {
      if (!name) return null;
      const candidates = document.querySelectorAll(
        "[data-lookup-name], [name]"
      );
      for (const element of candidates) {
        if (element.dataset.lookupName === name || element.name === name) {
          return element;
        }
      }
      return null;
    }
    isDependencySatisfied() {
      if (!this.hasDependencies()) return true;
      return this.dependencies.every((dependency) => {
        const value = this.getDependencyValue(dependency);
        if (Array.isArray(value)) {
          return value.length > 0;
        }
        return value !== null && value !== void 0 && value !== "";
      });
    }
    handleDependencyChange() {
      if (!this.hasDependencies() || this.destroyed) return;
      this.requestSequence++;
      this.abortRequest();
      this.handleSearch.cancel();
      this.setLoading(false);
      this.close();
      this.clearSelection(false, {
        restoreInitial: false
      });
      this.clearDependentOptions();
      this.clearLookupResults();
      this.page = 1;
      this.hasNext = false;
      this.syncDisabledState();
    }
    clearDependentOptions() {
      for (const option of Array.from(this.select.options)) {
        if (option.value !== "") {
          option.remove();
        } else {
          option.selected = true;
        }
      }
      if (!this.select.multiple && !Array.from(this.select.options).some(
        (option) => option.value === ""
      )) {
        this.select.add(new Option(this.config.placeholder, ""));
      }
      this.selectedValues = [];
      this.search.value = "";
      if (this.selection) {
        this.selection.innerHTML = "";
      }
      this.clearLookupResults();
    }
    getDependencyValue(name) {
      const element = this.findDependency(name);
      if (!element) return null;
      if (element.multiple) {
        return Array.from(element.selectedOptions).map((option) => option.value).filter(Boolean);
      }
      return element.value || null;
    }
    /* --------------------------------------------------------
     * Search and Loading
     * -------------------------------------------------------- */
    searchLookup() {
      if (this.destroyed) return;
      const term = this.search.value.trim();
      if (this.hasDependencies() && !this.isDependencySatisfied()) {
        this.clearLookupResults();
        this.close();
        return;
      }
      if (term.length < this.config.minimumInputLength) {
        if (this.hasDependencies()) return;
        this.clearRemoteResults({
          restoreInitial: true
        });
        if (this.config.minimumInputLength) {
          const count = this.config.minimumInputLength;
          this.setStatus(
            `Enter at least ${count} character${count === 1 ? "" : "s"}.`
          );
        }
        return;
      }
      this.page = 1;
      this.hasNext = false;
      this.load({
        term,
        page: 1,
        replace: true
      });
    }
    async load({ term = "", page = 1, replace = true }) {
      if (this.destroyed || !this.config.url || !this.isDependencySatisfied()) {
        return;
      }
      const requestId = ++this.requestSequence;
      this.abortRequest();
      const controller = new AbortController();
      this.abortController = controller;
      const url = new URL(
        this.config.url,
        window.location.origin
      );
      if (term) {
        url.searchParams.set(this.config.searchParam, term);
      }
      url.searchParams.set(this.config.pageParam, String(page));
      url.searchParams.set(
        this.config.pageSizeParam,
        String(this.config.pageSize)
      );
      this.appendDependencies(url);
      const headers = {
        Accept: "application/json"
      };
      if (this.config.token) {
        headers[this.config.tokenHeader] = this.config.token;
      }
      this.setLoading(true);
      try {
        const response = await fetch(url.toString(), {
          method: "GET",
          headers,
          credentials: "same-origin",
          signal: controller.signal
        });
        if (this.destroyed || requestId !== this.requestSequence) {
          return;
        }
        if (!response.ok) {
          throw new Error(
            `Lookup request failed: ${response.status}`
          );
        }
        const data = await response.json();
        if (this.destroyed || requestId !== this.requestSequence) {
          return;
        }
        this.handleResponse(data, {
          page,
          replace
        });
      } catch (error) {
        if (error.name === "AbortError") return;
        if (this.destroyed || requestId !== this.requestSequence) {
          return;
        }
        this.setError("Unable to load results.");
        this.dispatch("error", {
          error
        });
      } finally {
        if (requestId === this.requestSequence) {
          this.setLoading(false);
        }
      }
    }
    appendDependencies(url) {
      for (const dependency of this.dependencies) {
        const value = this.getDependencyValue(dependency);
        if (value === null || value === void 0 || value === "") {
          continue;
        }
        if (Array.isArray(value)) {
          for (const item of value) {
            url.searchParams.append(dependency, item);
          }
        } else {
          url.searchParams.set(dependency, value);
        }
      }
    }
    abortRequest() {
      if (!this.abortController) return;
      this.abortController.abort();
      this.abortController = null;
    }
    /* --------------------------------------------------------
     * Response and Rendering
     * -------------------------------------------------------- */
    handleResponse(data, { page, replace }) {
      const results = Array.isArray(data?.results) ? data.results : [];
      if (replace) {
        this.clearRemoteResults({
          restoreInitial: false
        });
      }
      this.renderResults(results);
      const pagination = data?.pagination || {};
      this.hasNext = Boolean(
        pagination.has_next ?? pagination.more ?? false
      );
      this.page = page;
      if (!results.length && replace) {
        this.setEmpty();
      } else {
        this.clearStatus();
      }
    }
    renderResults(results) {
      const selected = new Set(this.getSelectedValues());
      const existing = new Set(
        Array.from(
          this.listbox.querySelectorAll("[data-lookup-option]")
        ).map((option) => option.dataset.lookupValue)
      );
      for (const result of results) {
        const value = result?.value ?? result?.id ?? "";
        const label = result?.label ?? result?.text ?? "";
        if (value === null || value === void 0 || value === "") {
          continue;
        }
        const stringValue = String(value);
        if (existing.has(stringValue)) continue;
        const option = createElement(
          "div",
          "spice-lookup__option",
          {
            role: "option",
            "data-lookup-option": "",
            "data-lookup-value": stringValue
          }
        );
        option.textContent = String(label);
        const isSelected = selected.has(stringValue);
        option.classList.toggle("is-selected", isSelected);
        option.setAttribute("aria-selected", String(isSelected));
        this.listbox.appendChild(option);
        existing.add(stringValue);
      }
      this.updateHighlight();
    }
    checkLoadMore() {
      if (this.loading || !this.hasNext || this.destroyed) return;
      const threshold = 50;
      const position = this.listbox.scrollTop + this.listbox.clientHeight;
      const height = this.listbox.scrollHeight;
      if (height - position <= threshold) {
        this.load({
          term: this.search.value.trim(),
          page: this.page + 1,
          replace: false
        });
      }
    }
    clearRemoteResults({ restoreInitial = true } = {}) {
      this.listbox.innerHTML = "";
      this.highlightedIndex = -1;
      if (restoreInitial && !this.hasDependencies()) {
        this.renderResults(
          this.initialOptions.filter((option) => option.value !== "").map((option) => ({
            value: option.value,
            label: option.label
          }))
        );
      }
      this.hasNext = false;
      this.page = 1;
      this.clearStatus();
    }
    clearLookupResults() {
      this.listbox.innerHTML = "";
      this.highlightedIndex = -1;
      this.hasNext = false;
      this.page = 1;
      this.clearStatus();
    }
    setLoading(value) {
      if (this.destroyed) return;
      this.loading = value;
      this.wrapper.classList.toggle("is-loading", value);
      if (value) {
        this.setStatus("Loading...");
      } else if (this.status.textContent === "Loading...") {
        this.clearStatus();
      }
    }
    setEmpty() {
      this.setStatus("No results found.");
    }
    setError(message) {
      this.setStatus(message);
      this.wrapper.classList.add("has-error");
    }
    setStatus(message) {
      this.status.textContent = message;
      this.status.hidden = !message;
    }
    clearStatus() {
      this.status.textContent = "";
      this.status.hidden = true;
      this.wrapper.classList.remove("has-error");
    }
    /* --------------------------------------------------------
     * Selection
     * -------------------------------------------------------- */
    getSelectedValues() {
      return Array.from(this.select.selectedOptions).map((option) => option.value);
    }
    selectResult(value, label = null) {
      if (value === null || value === void 0 || value === "") {
        return;
      }
      if (this.select.multiple) {
        this.toggleMultipleValue(value, label);
      } else {
        this.setSingleValue(value, label);
      }
    }
    setSingleValue(value, label = null) {
      const stringValue = String(value);
      let option = Array.from(this.select.options).find(
        (existing) => existing.value === stringValue
      );
      if (!option) {
        option = new Option(
          label !== null ? String(label) : stringValue,
          stringValue,
          false,
          false
        );
        this.select.appendChild(option);
      } else if (label !== null) {
        option.textContent = String(label);
      }
      for (const existing of this.select.options) {
        existing.selected = existing === option;
      }
      this.selectedValues = this.getSelectedValues();
      this.syncFromSelect();
      this.dispatchChange();
      this.close();
      this.search.value = option.textContent;
      this.dispatch("select", {
        value: stringValue,
        label: option.textContent
      });
    }
    toggleMultipleValue(value, label = null) {
      const stringValue = String(value);
      let found = false;
      for (const option of this.select.options) {
        if (option.value !== stringValue) continue;
        option.selected = !option.selected;
        found = true;
        break;
      }
      if (!found) {
        const option = new Option(
          label !== null ? String(label) : stringValue,
          stringValue,
          false,
          true
        );
        this.select.appendChild(option);
      }
      this.dispatchChange();
      this.syncFromSelect();
      this.search.value = "";
      this.search.focus();
      this.open();
      this.dispatch("select", {
        value: stringValue,
        label: this.getOptionLabel(stringValue)
      });
    }
    clearSelection(triggerChange = true, { restoreInitial = true } = {}) {
      for (const option of this.select.options) {
        option.selected = false;
      }
      if (triggerChange) {
        this.dispatchChange();
      }
      this.syncFromSelect();
      this.clearRemoteResults({
        restoreInitial
      });
    }
    syncFromSelect() {
      if (this.destroyed) return;
      const selectedValues = new Set(this.getSelectedValues());
      if (!this.select.multiple) {
        const selectedValue = this.getSelectedValues()[0];
        this.search.value = selectedValue ? this.getOptionLabel(selectedValue) : "";
      }
      const optionElements = this.listbox.querySelectorAll(
        "[data-lookup-option]"
      );
      optionElements.forEach((element) => {
        const isSelected = selectedValues.has(
          element.dataset.lookupValue
        );
        element.classList.toggle("is-selected", isSelected);
        element.setAttribute(
          "aria-selected",
          String(isSelected)
        );
      });
      if (this.selection) {
        this.selection.innerHTML = "";
        for (const value of selectedValues) {
          const label = this.getOptionLabel(value);
          const tag = createElement(
            "span",
            "spice-lookup__tag",
            {
              "data-lookup-tag": value
            }
          );
          tag.textContent = label;
          const removeButton = createElement(
            "button",
            "spice-lookup__tag-remove",
            {
              type: "button",
              "aria-label": `Remove ${label}`,
              "data-lookup-remove": value
            }
          );
          removeButton.textContent = "\xD7";
          tag.appendChild(removeButton);
          this.selection.appendChild(tag);
        }
      }
    }
    getOptionLabel(value) {
      const option = Array.from(this.select.options).find(
        (item) => item.value === String(value)
      );
      if (option) return option.textContent;
      const optionElement = Array.from(
        this.listbox.querySelectorAll("[data-lookup-option]")
      ).find(
        (item) => item.dataset.lookupValue === String(value)
      );
      return optionElement ? optionElement.textContent : String(value);
    }
    dispatchChange() {
      this.select.dispatchEvent(
        new Event("change", {
          bubbles: true
        })
      );
    }
    dispatch(eventName, detail = {}) {
      if (!this.wrapper) return;
      this.wrapper.dispatchEvent(
        new CustomEvent(`${EVENT_PREFIX}:${eventName}`, {
          detail,
          bubbles: true,
          cancelable: true
        })
      );
    }
    /* --------------------------------------------------------
     * Dropdown
     * -------------------------------------------------------- */
    open() {
      if (this.destroyed || this.select.disabled || this.hasDependencies() && !this.isDependencySatisfied()) {
        return;
      }
      this.wrapper.classList.add("is-open");
      this.search.setAttribute("aria-expanded", "true");
    }
    close() {
      if (!this.wrapper) return;
      this.wrapper.classList.remove("is-open");
      this.search.setAttribute("aria-expanded", "false");
      this.highlightedIndex = -1;
      this.updateHighlight();
    }
    handleKeydown(event) {
      const options = Array.from(
        this.listbox.querySelectorAll("[data-lookup-option]")
      );
      switch (event.key) {
        case "ArrowDown":
          event.preventDefault();
          if (!this.wrapper.classList.contains("is-open")) {
            this.open();
          } else if (options.length) {
            this.highlightedIndex = (this.highlightedIndex + 1) % options.length;
            this.updateHighlight();
            this.scrollHighlightedIntoView(
              options[this.highlightedIndex]
            );
          }
          break;
        case "ArrowUp":
          event.preventDefault();
          if (options.length) {
            this.highlightedIndex = (this.highlightedIndex - 1 + options.length) % options.length;
            this.updateHighlight();
            this.scrollHighlightedIntoView(
              options[this.highlightedIndex]
            );
          }
          break;
        case "Enter":
          if (this.wrapper.classList.contains("is-open") && this.highlightedIndex >= 0 && options[this.highlightedIndex]) {
            event.preventDefault();
            const option = options[this.highlightedIndex];
            this.selectResult(
              option.dataset.lookupValue,
              option.textContent
            );
          }
          break;
        case "Escape":
          if (this.wrapper.classList.contains("is-open")) {
            event.preventDefault();
            this.close();
          }
          break;
      }
    }
    updateHighlight() {
      if (!this.listbox) return;
      const options = Array.from(
        this.listbox.querySelectorAll("[data-lookup-option]")
      );
      options.forEach((element, index) => {
        element.classList.toggle(
          "is-highlighted",
          index === this.highlightedIndex
        );
      });
    }
    scrollHighlightedIntoView(optionElement) {
      if (!optionElement) return;
      const parentRect = this.listbox.getBoundingClientRect();
      const optionRect = optionElement.getBoundingClientRect();
      if (optionRect.bottom > parentRect.bottom) {
        this.listbox.scrollTop += optionRect.bottom - parentRect.bottom;
      } else if (optionRect.top < parentRect.top) {
        this.listbox.scrollTop -= parentRect.top - optionRect.top;
      }
    }
    /* --------------------------------------------------------
     * Cleanup
     * -------------------------------------------------------- */
    destroy() {
      if (this.destroyed) return;
      this.destroyed = true;
      this.requestSequence++;
      this.abortRequest();
      if (this.handleSearch) {
        this.handleSearch.cancel();
      }
      document.removeEventListener(
        "mousedown",
        this.handleDocumentClick
      );
      this.unbindDependencies();
      if (this.wrapper?.parentNode) {
        this.wrapper.parentNode.insertBefore(
          this.select,
          this.wrapper
        );
        this.wrapper.remove();
      }
      this.select.classList.remove("spice-lookup__native");
    }
  };
  function initializeLookup(root = document) {
    if (!root) return;
    const selects = [];
    if (root.nodeType === Node.ELEMENT_NODE && root.matches(SELECTOR)) {
      selects.push(root);
    }
    if (typeof root.querySelectorAll === "function") {
      selects.push(...root.querySelectorAll(SELECTOR));
    }
    for (const select of selects) {
      if (instances.has(select)) continue;
      const instance = new SpiceLookup(select);
      instances.set(select, instance);
    }
  }
  function destroyLookup(root) {
    if (!root) return;
    const selects = [];
    if (root.nodeType === Node.ELEMENT_NODE && root.matches(SELECTOR)) {
      selects.push(root);
    }
    if (typeof root.querySelectorAll === "function") {
      selects.push(...root.querySelectorAll(SELECTOR));
    }
    for (const select of selects) {
      const instance = instances.get(select);
      if (!instance) continue;
      instance.destroy();
      instances.delete(select);
    }
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/index.js
  var isBrowser = typeof window !== "undefined" && typeof document !== "undefined";
  var socket = isBrowser ? new SpiceSocket() : null;
  var router = isBrowser ? new SpiceRouter() : null;
  var ui = isBrowser ? new SpiceUI() : null;
  if (isBrowser) {
    window.SpiceUI = SpiceUI;
    window.SpiceSocket = SpiceSocket;
    window.SpiceRouter = SpiceRouter;
    window.SpiceTable = SpiceTable;
    window.spice ?? (window.spice = {});
    Object.assign(window.spice, {
      ui,
      socket,
      router
    });
  }
  var initialized = false;
  var tableInstances = /* @__PURE__ */ new WeakMap();
  function onReady(callback) {
    if (!isBrowser) return;
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, {
        once: true
      });
    } else {
      callback();
    }
  }
  function getElements(root, selector) {
    if (!root) return [];
    const elements = [];
    if (root.matches?.(selector)) {
      elements.push(root);
    }
    elements.push(...root.querySelectorAll?.(selector) || []);
    return elements;
  }
  function initTables(root) {
    getElements(root, "[data-table]").forEach((element) => {
      if (tableInstances.has(element)) return;
      const instance = new SpiceTable(element);
      tableInstances.set(element, instance);
    });
  }
  function destroyTables(root) {
    getElements(root, "[data-table]").forEach((element) => {
      const instance = tableInstances.get(element);
      if (!instance) return;
      instance.destroy?.();
      tableInstances.delete(element);
    });
  }
  function initLookups(root) {
    if (!root) return;
    initializeLookup(root);
  }
  function destroyLookups(root) {
    if (!root) return;
    destroyLookup(root);
  }
  function init(root = document) {
    if (!isBrowser || !root) return;
    if (!initialized) {
      initialized = true;
      router.start();
      router.processDocument();
    }
    initTables(root);
    initLookups(root);
    ui.initStates(root);
  }
  function handleHTMXLoad(event) {
    init(event.detail?.elt || document);
  }
  function handleHTMXCleanup(event) {
    const root = event.detail?.elt;
    if (!root) return;
    destroyTables(root);
    destroyLookups(root);
  }
  if (isBrowser) {
    document.addEventListener("htmx:load", handleHTMXLoad);
    document.addEventListener(
      "htmx:beforeCleanupElement",
      handleHTMXCleanup
    );
    onReady(() => init());
  }
  document.body.addEventListener("htmx:beforeRequest", function(event) {
    if (event.detail.elt.matches("[data-table-export]")) {
      document.getElementById("table-export-loading")?.classList.remove("hidden");
      document.getElementById("table-export-loading")?.classList.add("flex");
    }
  });
  document.body.addEventListener("htmx:afterRequest", function(event) {
    if (event.detail.elt.matches("[data-table-export]")) {
      document.getElementById("table-export-loading")?.classList.add("hidden");
      document.getElementById("table-export-loading")?.classList.remove("flex");
    }
  });
})();
//# sourceMappingURL=javascript.js.map
