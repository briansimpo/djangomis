var Djangospice = (() => {
  // ../djangospice/src/djangospice/spice/static/spice/js/spice-ui.js
  var SpiceUI = class {
    constructor() {
      this.activeModals = [];
      this.activeOffcanvas = null;
      this.activeSidebar = null;
      this.activeTooltip = null;
      this.activePopover = null;
      this.initStates();
      this.initListeners();
      this.initTabsFromHash();
    }
    /**
     * Enforces initial hidden/closed states across components unless explicitly 
     * overridden via `data-open="true"`. If `data-open="false"` or omitted, they stay closed.
     */
    initStates() {
      const shouldBeOpen = (el) => el.dataset.open === "true";
      const collapsibleSelectors = "[data-dropdown-menu], [data-collapse-content]";
      document.querySelectorAll(collapsibleSelectors).forEach((el) => {
        if (shouldBeOpen(el)) {
          el.classList.remove("hidden");
          const wrapper = el.closest("[data-dropdown-wrapper]") || el.parentElement;
          const toggle = wrapper?.querySelector('[data-toggle="dropdown"], [data-toggle="collapse"]');
          if (toggle) {
            toggle.setAttribute("aria-expanded", "true");
            const chevron = toggle.querySelector("[data-chevron]");
            if (chevron) chevron.classList.add("rotate-180");
          }
        } else {
          el.classList.add("hidden");
        }
      });
      document.querySelectorAll("[data-modal]").forEach((modal) => {
        if (shouldBeOpen(modal)) {
          this.showModalElement(modal);
        } else {
          modal.classList.add("hidden");
          modal.setAttribute("aria-hidden", "true");
        }
      });
      document.querySelectorAll("[data-offcanvas]").forEach((offcanvas) => {
        if (shouldBeOpen(offcanvas)) {
          const panel = offcanvas.querySelector("[data-offcanvas-panel]");
          const backdrop = offcanvas.querySelector("[data-offcanvas-backdrop]");
          offcanvas.classList.remove("pointer-events-none");
          offcanvas.setAttribute("aria-hidden", "false");
          if (panel) panel.classList.remove("translate-x-full", "-translate-x-full", "translate-y-full", "-translate-y-full");
          if (backdrop) backdrop.classList.remove("opacity-0");
          document.body.classList.add("overflow-hidden");
          this.activeOffcanvas = offcanvas;
        } else {
          offcanvas.classList.add("pointer-events-none");
          offcanvas.setAttribute("aria-hidden", "true");
          const panel = offcanvas.querySelector("[data-offcanvas-panel]");
          const backdrop = offcanvas.querySelector("[data-offcanvas-backdrop]");
          const placement = offcanvas.dataset.placement || "right";
          const translateMap = {
            right: "translate-x-full",
            left: "-translate-x-full",
            top: "-translate-y-full",
            bottom: "translate-y-full"
          };
          if (panel) panel.classList.add(translateMap[placement] || "translate-x-full");
          if (backdrop) backdrop.classList.add("opacity-0");
        }
      });
      document.querySelectorAll("[data-sidebar], aside[id]").forEach((sidebar) => {
        if (shouldBeOpen(sidebar)) {
          sidebar.classList.remove("-translate-x-full");
          sidebar.classList.add("translate-x-0");
          this.activeSidebar = sidebar;
        } else {
          sidebar.classList.remove("translate-x-0");
          sidebar.classList.add("-translate-x-full");
        }
      });
      document.querySelectorAll("[data-toast]").forEach((toast) => {
        requestAnimationFrame(() => {
          toast.classList.remove("translate-y-2", "translate-y-4", "opacity-0");
        });
        const duration = parseInt(toast.dataset.duration, 10) || 5e3;
        if (duration > 0 && !toast.dataset.timer) {
          toast.dataset.timer = setTimeout(() => this.removeToast(toast), duration);
        }
      });
    }
    initListeners() {
      document.addEventListener("click", (e) => {
        const dropdownToggle = e.target.closest('[data-toggle="dropdown"]');
        if (!dropdownToggle) {
          this.closeAllDropdowns(e.target);
        }
        const popoverToggle = e.target.closest('[data-toggle="popover"]');
        if (!popoverToggle && this.activePopover && !this.activePopover.contains(e.target)) {
          this.hidePopover();
        }
        if (e.target.matches("[data-sidebar-backdrop]") && this.activeSidebar) {
          this.closeSidebar(this.activeSidebar);
          return;
        }
        const dismissModalBtn = e.target.closest('[data-dismiss="modal"]');
        if (dismissModalBtn) {
          e.preventDefault();
          const modal = dismissModalBtn.closest("[data-modal]");
          if (modal) this.closeModal(modal);
          return;
        }
        if (e.target.matches('[data-modal]:not([data-backdrop="static"])')) {
          if (!e.target.closest("[data-modal-dialog]") || e.target.hasAttribute("data-modal")) {
            this.closeModal(e.target);
            return;
          }
        }
        const dismissOffcanvasBtn = e.target.closest('[data-dismiss="offcanvas"]');
        if (dismissOffcanvasBtn) {
          e.preventDefault();
          const offcanvas = dismissOffcanvasBtn.closest("[data-offcanvas]");
          if (offcanvas) this.closeOffcanvas(offcanvas);
          return;
        }
        if (e.target.matches("[data-offcanvas-backdrop]") && this.activeOffcanvas) {
          if (this.activeOffcanvas.dataset.backdrop !== "static") {
            this.closeOffcanvas(this.activeOffcanvas);
          }
          return;
        }
        const dismissToastBtn = e.target.closest('[data-dismiss="toast"]');
        if (dismissToastBtn) {
          e.preventDefault();
          const toast = dismissToastBtn.closest("[data-toast]");
          if (toast) this.removeToast(toast);
          return;
        }
        const dismissAlertBtn = e.target.closest('[data-dismiss="alert"]');
        if (dismissAlertBtn) {
          e.preventDefault();
          const alert = dismissAlertBtn.closest("[data-alert]");
          if (alert) {
            alert.classList.add("opacity-0", "scale-95", "transition-all", "duration-150");
            setTimeout(() => alert.remove(), 150);
          }
          return;
        }
        const toggle = e.target.closest("[data-toggle]");
        if (!toggle) return;
        const type = toggle.dataset.toggle;
        if (type === "sidebar") this.handleSidebar(toggle, e);
        if (type === "dropdown") this.handleDropdown(toggle, e);
        if (type === "modal") this.openModal(toggle, e);
        if (type === "offcanvas") this.openOffcanvas(toggle, e);
        if (type === "tab") this.activateTab(toggle, e);
        if (type === "collapse") this.handleCollapse(toggle, e);
        if (type === "popover") this.togglePopover(toggle, e);
      });
      document.addEventListener("mouseover", (e) => this.handleTooltipShow(e));
      document.addEventListener("mouseout", (e) => this.handleTooltipHide(e));
      document.addEventListener("focusin", (e) => this.handleTooltipShow(e));
      document.addEventListener("focusout", (e) => this.handleTooltipHide(e));
      window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          this.closeAllDropdowns();
          this.hidePopover();
          if (this.activeSidebar) {
            this.closeSidebar(this.activeSidebar);
            return;
          }
          if (this.activeOffcanvas && this.activeOffcanvas.dataset.keyboard !== "false") {
            this.closeOffcanvas(this.activeOffcanvas);
            return;
          }
          if (this.activeModals.length > 0) {
            const topModal = this.activeModals[this.activeModals.length - 1];
            if (topModal.dataset.keyboard !== "false") {
              this.closeModal(topModal);
            }
          }
        }
        if (e.key === "Tab" && this.activeModals.length > 0) {
          const topModal = this.activeModals[this.activeModals.length - 1];
          this.trapFocus(topModal, e);
        }
      });
      document.addEventListener("htmx:afterSwap", (e) => {
        const modal = e.target.closest("[data-modal]") || e.target.querySelector("[data-modal]");
        if (modal && modal.dataset.autoOpen === "true") {
          this.showModalElement(modal);
        }
        this.initStates();
      });
    }
    // =========================================================================
    // SIDEBAR MANAGEMENT
    // =========================================================================
    handleSidebar(toggle, e) {
      if (e) e.preventDefault();
      e.stopPropagation();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const sidebar = document.querySelector(targetSelector);
      if (!sidebar) return;
      const isOpen = sidebar.classList.contains("translate-x-0");
      if (isOpen) {
        this.closeSidebar(sidebar);
      } else {
        this.openSidebar(sidebar, toggle);
      }
    }
    openSidebar(sidebar, toggle = null) {
      sidebar.__triggerElement = toggle;
      sidebar.classList.remove("-translate-x-full");
      sidebar.classList.add("translate-x-0");
      let backdrop = document.querySelector("#spice-sidebar-backdrop");
      if (!backdrop) {
        backdrop = document.createElement("div");
        backdrop.id = "spice-sidebar-backdrop";
        backdrop.className = "fixed inset-0 z-30 bg-black/30 lg:hidden pt-16 transition-opacity opacity-0";
        backdrop.setAttribute("data-sidebar-backdrop", "");
        document.body.appendChild(backdrop);
        requestAnimationFrame(() => backdrop.classList.remove("opacity-0"));
      } else {
        backdrop.classList.remove("hidden");
        requestAnimationFrame(() => backdrop.classList.remove("opacity-0"));
      }
      this.activeSidebar = sidebar;
      sidebar.dispatchEvent(new CustomEvent("spice:sidebar:shown", { bubbles: true }));
    }
    closeSidebar(sidebar = null) {
      const targetSidebar = sidebar || this.activeSidebar;
      if (!targetSidebar) return;
      targetSidebar.classList.remove("translate-x-0");
      targetSidebar.classList.add("-translate-x-full");
      const backdrop = document.querySelector("#spice-sidebar-backdrop");
      if (backdrop) {
        backdrop.classList.add("opacity-0");
        setTimeout(() => backdrop.classList.add("hidden"), 200);
      }
      if (targetSidebar.__triggerElement && document.body.contains(targetSidebar.__triggerElement)) {
        targetSidebar.__triggerElement.focus();
      }
      this.activeSidebar = null;
      targetSidebar.dispatchEvent(new CustomEvent("spice:sidebar:hidden", { bubbles: true }));
    }
    // =========================================================================
    // TOAST NOTIFICATIONS (spice.showToast)
    // =========================================================================
    showToast({ title = "", message = "", type = "info", duration = 4e3 } = {}) {
      let container = document.querySelector("#spice-toast-container");
      if (!container) {
        container = document.createElement("div");
        container.id = "spice-toast-container";
        container.className = "fixed bottom-5 right-5 z-50 flex flex-col gap-3 pointer-events-none max-w-sm w-full px-4";
        document.body.appendChild(container);
      }
      const toast = document.createElement("div");
      toast.setAttribute("data-toast", "");
      toast.setAttribute("role", "status");
      const variants = {
        success: "border-emerald-200 bg-emerald-50/95 text-emerald-900",
        error: "border-rose-200 bg-rose-50/95 text-rose-900",
        warning: "border-amber-200 bg-amber-50/95 text-amber-900",
        info: "border-slate-200 bg-white/95 text-slate-800"
      };
      const icons = {
        success: '<i class="fa-solid fa-circle-check text-emerald-600 mt-0.5"></i>',
        error: '<i class="fa-solid fa-circle-exclamation text-rose-600 mt-0.5"></i>',
        warning: '<i class="fa-solid fa-triangle-exclamation text-amber-600 mt-0.5"></i>',
        info: '<i class="fa-solid fa-circle-info text-blue-600 mt-0.5"></i>'
      };
      toast.className = `pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-xl border backdrop-blur-sm transition-all transform translate-y-2 opacity-0 duration-200 ${variants[type] || variants.info}`;
      toast.innerHTML = `
            ${icons[type] || icons.info}
            <div class="flex-1">
                ${title ? `<h4 class="text-sm font-bold mb-0.5">${title}</h4>` : ""}
                <p class="text-xs leading-relaxed">${message}</p>
            </div>
            <button type="button" data-dismiss="toast" aria-label="Close" class="text-slate-400 hover:text-slate-600 transition-colors">
                <i class="fa-solid fa-xmark text-xs"></i>
            </button>
        `;
      container.appendChild(toast);
      requestAnimationFrame(() => toast.classList.remove("translate-y-2", "opacity-0"));
      if (duration > 0) {
        toast.dataset.timer = setTimeout(() => this.removeToast(toast), duration);
      }
      return toast;
    }
    removeToast(toast) {
      if (!toast) return;
      if (toast.dataset.timer) clearTimeout(parseInt(toast.dataset.timer, 10));
      toast.classList.add("translate-y-2", "opacity-0");
      setTimeout(() => toast.remove(), 200);
    }
    // =========================================================================
    // DROPDOWNS
    // =========================================================================
    handleDropdown(toggle, e) {
      e.preventDefault();
      e.stopPropagation();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const dropdown = targetSelector && targetSelector !== "#" ? document.querySelector(targetSelector) : toggle.nextElementSibling;
      if (!dropdown) return;
      const isOpen = !dropdown.classList.contains("hidden");
      this.closeAllDropdowns();
      if (!isOpen) {
        dropdown.classList.remove("hidden");
        toggle.setAttribute("aria-expanded", "true");
        const chevron = toggle.querySelector("[data-chevron]");
        if (chevron) chevron.classList.add("rotate-180");
      }
    }
    closeAllDropdowns(exceptElement = null) {
      document.querySelectorAll("[data-dropdown-menu]").forEach((menu) => {
        if (!exceptElement || !menu.contains(exceptElement)) {
          menu.classList.add("hidden");
          const wrapper = menu.closest("[data-dropdown-wrapper]") || menu.parentElement;
          const toggle = wrapper?.querySelector('[data-toggle="dropdown"]');
          if (toggle) {
            toggle.setAttribute("aria-expanded", "false");
            const chevron = toggle.querySelector("[data-chevron]");
            if (chevron) chevron.classList.remove("rotate-180");
          }
        }
      });
    }
    // =========================================================================
    // MODALS
    // =========================================================================
    openModal(toggle, e) {
      if (e) e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const modal = document.querySelector(targetSelector);
      if (!modal) return;
      modal.__triggerElement = toggle;
      this.showModalElement(modal);
    }
    showModalElement(modal) {
      if (this.activeModals.includes(modal)) return;
      modal.classList.remove("hidden");
      modal.setAttribute("aria-hidden", "false");
      document.body.classList.add("overflow-hidden");
      this.activeModals.push(modal);
      const focusable = this.getFocusableElements(modal);
      if (focusable.length > 0) {
        const autoFocusEl = modal.querySelector("[autofocus]") || focusable[0];
        requestAnimationFrame(() => autoFocusEl.focus());
      }
      modal.dispatchEvent(new CustomEvent("spice:modal:shown", { bubbles: true }));
    }
    closeModal(modal) {
      if (!modal) return;
      modal.classList.add("hidden");
      modal.setAttribute("aria-hidden", "true");
      this.activeModals = this.activeModals.filter((m) => m !== modal);
      if (this.activeModals.length === 0 && !this.activeOffcanvas) {
        document.body.classList.remove("overflow-hidden");
      }
      if (modal.__triggerElement && document.body.contains(modal.__triggerElement)) {
        modal.__triggerElement.focus();
      }
      modal.dispatchEvent(new CustomEvent("spice:modal:hidden", { bubbles: true }));
    }
    getFocusableElements(container) {
      return Array.from(
        container.querySelectorAll(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      ).filter((el) => el.offsetParent !== null);
    }
    trapFocus(modal, e) {
      const focusable = this.getFocusableElements(modal);
      if (focusable.length === 0) return;
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
    // =========================================================================
    // OFFCANVAS / DRAWERS
    // =========================================================================
    openOffcanvas(toggle, e) {
      if (e) e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const offcanvas = document.querySelector(targetSelector);
      if (!offcanvas) return;
      if (this.activeOffcanvas && this.activeOffcanvas !== offcanvas) {
        this.closeOffcanvas(this.activeOffcanvas);
      }
      offcanvas.__triggerElement = toggle;
      offcanvas.classList.remove("pointer-events-none");
      offcanvas.setAttribute("aria-hidden", "false");
      const panel = offcanvas.querySelector("[data-offcanvas-panel]");
      const backdrop = offcanvas.querySelector("[data-offcanvas-backdrop]");
      requestAnimationFrame(() => {
        if (panel) {
          panel.classList.remove(
            "translate-x-full",
            "-translate-x-full",
            "translate-x-[-100%]",
            "translate-y-full",
            "-translate-y-full",
            "translate-y-[-100%]"
          );
        }
        if (backdrop) backdrop.classList.remove("opacity-0");
      });
      document.body.classList.add("overflow-hidden");
      this.activeOffcanvas = offcanvas;
      offcanvas.dispatchEvent(new CustomEvent("spice:offcanvas:shown", { bubbles: true }));
    }
    closeOffcanvas(offcanvas) {
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
      if (panel) panel.classList.add(translateMap[placement] || "translate-x-full");
      if (backdrop) backdrop.classList.add("opacity-0");
      offcanvas.setAttribute("aria-hidden", "true");
      setTimeout(() => {
        offcanvas.classList.add("pointer-events-none");
        if (this.activeModals.length === 0) {
          document.body.classList.remove("overflow-hidden");
        }
      }, 300);
      if (offcanvas.__triggerElement && document.body.contains(offcanvas.__triggerElement)) {
        offcanvas.__triggerElement.focus();
      }
      this.activeOffcanvas = null;
      offcanvas.dispatchEvent(new CustomEvent("spice:offcanvas:hidden", { bubbles: true }));
    }
    // =========================================================================
    // DYNAMIC TABS
    // =========================================================================
    activateTab(toggle, e) {
      if (e) e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const targetPane = document.querySelector(targetSelector);
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
      if (tabList && tabList.dataset.syncHash === "true" && targetSelector.startsWith("#")) {
        history.replaceState(null, "", targetSelector);
      }
      toggle.dispatchEvent(new CustomEvent("spice:tab:shown", {
        bubbles: true,
        detail: { tab: toggle, pane: targetPane }
      }));
    }
    initTabsFromHash() {
      const hash = window.location.hash;
      if (!hash) return;
      const matchingTab = document.querySelector(
        `[data-toggle="tab"][data-target="${hash}"], [data-toggle="tab"][href="${hash}"]`
      );
      if (matchingTab) {
        this.activateTab(matchingTab);
      }
    }
    // =========================================================================
    // ACCORDIONS & COLLAPSES
    // =========================================================================
    handleCollapse(toggle, e) {
      e.preventDefault();
      const targetSelector = toggle.dataset.target || toggle.getAttribute("href");
      const target = document.querySelector(targetSelector);
      if (!target) return;
      const accordionGroup = toggle.closest("[data-accordion]");
      const isExpanded = !target.classList.contains("hidden");
      if (accordionGroup && !isExpanded && accordionGroup.dataset.accordion === "single") {
        accordionGroup.querySelectorAll("[data-collapse-content]").forEach((content) => {
          content.classList.add("hidden");
        });
        accordionGroup.querySelectorAll('[data-toggle="collapse"]').forEach((btn) => {
          btn.setAttribute("aria-expanded", "false");
          const chevron2 = btn.querySelector("[data-chevron]");
          if (chevron2) chevron2.classList.remove("rotate-180");
        });
      }
      target.classList.toggle("hidden");
      toggle.setAttribute("aria-expanded", String(!isExpanded));
      const chevron = toggle.querySelector("[data-chevron]");
      if (chevron) chevron.classList.toggle("rotate-180", !isExpanded);
    }
    // =========================================================================
    // TOOLTIPS & POPOVERS
    // =========================================================================
    handleTooltipShow(e) {
      const target = e.target.closest("[data-tooltip]");
      if (!target) return;
      const content = target.dataset.tooltip;
      if (!content) return;
      let tooltipEl = document.querySelector("#spice-global-tooltip");
      if (!tooltipEl) {
        tooltipEl = document.createElement("div");
        tooltipEl.id = "spice-global-tooltip";
        tooltipEl.role = "tooltip";
        tooltipEl.className = "fixed z-50 px-2.5 py-1.5 text-xs font-medium text-white bg-slate-900 rounded-lg shadow-lg pointer-events-none transition-opacity duration-150 opacity-0";
        document.body.appendChild(tooltipEl);
      }
      tooltipEl.textContent = content;
      tooltipEl.classList.remove("opacity-0");
      const rect = target.getBoundingClientRect();
      const tRect = tooltipEl.getBoundingClientRect();
      const placement = target.dataset.tooltipPlacement || "top";
      let top = rect.top - tRect.height - 8;
      let left = rect.left + rect.width / 2 - tRect.width / 2;
      if (placement === "bottom" || top < 8) {
        top = rect.bottom + 8;
      }
      left = Math.max(8, Math.min(left, window.innerWidth - tRect.width - 8));
      tooltipEl.style.top = `${top}px`;
      tooltipEl.style.left = `${left}px`;
      this.activeTooltip = tooltipEl;
    }
    handleTooltipHide(e) {
      const target = e.target.closest("[data-tooltip]");
      if (!target) return;
      const tooltipEl = document.querySelector("#spice-global-tooltip");
      if (tooltipEl) {
        tooltipEl.classList.add("opacity-0");
      }
    }
    togglePopover(toggle, e) {
      e.preventDefault();
      e.stopPropagation();
      if (this.activePopover && this.activePopover.__trigger === toggle) {
        this.hidePopover();
        return;
      }
      this.hidePopover();
      const title = toggle.dataset.popoverTitle || "";
      const content = toggle.dataset.popoverContent || toggle.dataset.popover || "";
      if (!title && !content) return;
      const popover = document.createElement("div");
      popover.id = "spice-global-popover";
      popover.__trigger = toggle;
      popover.className = "fixed z-50 w-64 rounded-xl border border-slate-200 bg-white p-3.5 shadow-xl text-sm transition-opacity duration-150";
      popover.innerHTML = `
            ${title ? `<div class="font-bold text-slate-900 mb-1 pb-1.5 border-b border-slate-100">${title}</div>` : ""}
            <div class="text-xs text-slate-600 leading-relaxed">${content}</div>
        `;
      document.body.appendChild(popover);
      const rect = toggle.getBoundingClientRect();
      const pRect = popover.getBoundingClientRect();
      let top = rect.bottom + 8;
      let left = rect.left + rect.width / 2 - pRect.width / 2;
      if (top + pRect.height > window.innerHeight - 8) {
        top = rect.top - pRect.height - 8;
      }
      left = Math.max(8, Math.min(left, window.innerWidth - pRect.width - 8));
      popover.style.top = `${top}px`;
      popover.style.left = `${left}px`;
      this.activePopover = popover;
    }
    hidePopover() {
      if (this.activePopover) {
        this.activePopover.remove();
        this.activePopover = null;
      }
    }
  };
  if (typeof window !== "undefined") {
    window.SpiceUI = SpiceUI;
    if (typeof document !== "undefined") {
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
          window.spice = new SpiceUI();
        });
      } else {
        window.spice = new SpiceUI();
      }
    }
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/spice-router.js
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
  var RESERVED_ATTRIBUTES = /* @__PURE__ */ new Set([
    "to",
    "method",
    "exact",
    "active-class",
    "match-query",
    "transition",
    "preload",
    "push-url",
    "select",
    "swap",
    "target",
    "data-initialized"
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
    return !["false", "0", "off", "no"].includes(
      String(value).toLowerCase()
    );
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
  function copyAttributes(source, destination, excluded = /* @__PURE__ */ new Set()) {
    for (const attribute of source.attributes) {
      const name = attribute.name;
      if (RESERVED_ATTRIBUTES.has(name) || excluded.has(name) || name.startsWith("data-spice-internal-")) {
        continue;
      }
      destination.setAttribute(name, attribute.value);
    }
  }
  var SpiceRouter = class {
    constructor(options = {}) {
      this.options = {
        ...DEFAULTS,
        ...options
      };
      this.started = false;
      this.apps = /* @__PURE__ */ new Set();
      this.observer = null;
      this.boundHandlers = {
        beforeRequest: this.handleBeforeRequest.bind(this),
        beforeSwap: this.handleBeforeSwap.bind(this),
        afterSwap: this.handleAfterSwap.bind(this),
        afterRequest: this.handleAfterRequest.bind(this),
        pushedIntoHistory: this.handlePushedIntoHistory.bind(this),
        responseError: this.handleRequestError.bind(this),
        sendError: this.handleRequestError.bind(this),
        timeout: this.handleRequestError.bind(this),
        sendAbort: this.handleRequestError.bind(this),
        popstate: this.handlePopState.bind(this)
      };
    }
    /* ---------------------------------------------------------------------- */
    /* Lifecycle                                                              */
    /* ---------------------------------------------------------------------- */
    start() {
      if (this.started) {
        this.processDocument();
        return this;
      }
      this.registerElements();
      this.initListeners();
      this.observeDOM();
      this.started = true;
      this.processDocument();
      emit(document, ROUTER_EVENTS.READY, {
        router: this
      });
      return this;
    }
    stop() {
      if (!this.started) return this;
      const events = {
        "htmx:beforeRequest": "beforeRequest",
        "htmx:beforeSwap": "beforeSwap",
        "htmx:afterSwap": "afterSwap",
        "htmx:afterRequest": "afterRequest",
        "htmx:pushedIntoHistory": "pushedIntoHistory",
        "htmx:responseError": "responseError",
        "htmx:sendError": "sendError",
        "htmx:timeout": "timeout",
        "htmx:sendAbort": "sendAbort"
      };
      for (const [event, handler] of Object.entries(events)) {
        document.removeEventListener(
          event,
          this.boundHandlers[handler]
        );
      }
      window.removeEventListener(
        "popstate",
        this.boundHandlers.popstate
      );
      this.observer?.disconnect();
      this.observer = null;
      this.started = false;
      return this;
    }
    updateOptions(options = {}) {
      this.options = {
        ...this.options,
        ...options
      };
      this.processExistingContainers();
      this.refreshActiveLinks();
      return this;
    }
    /* ---------------------------------------------------------------------- */
    /* Custom elements                                                        */
    /* ---------------------------------------------------------------------- */
    registerElements() {
      const router = this;
      if (!customElements.get("spice-app")) {
        customElements.define(
          "spice-app",
          class extends HTMLElement {
            connectedCallback() {
              router.apps.add(this);
            }
            disconnectedCallback() {
              router.apps.delete(this);
            }
          }
        );
      }
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
                /* @__PURE__ */ new Set(["id"])
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
              router.initializeRequest(anchor, {
                to,
                method: "get"
              });
              router.refreshActiveLinks();
            }
          }
        );
      }
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
                console.error(
                  "SpiceRouter: Invalid spice-button configuration.",
                  this
                );
                return;
              }
              const button = document.createElement("button");
              button.type = this.getAttribute("type") || "button";
              copyAttributes(
                this,
                button,
                /* @__PURE__ */ new Set(["id"])
              );
              button.dataset.spiceNavigation = "true";
              while (this.firstChild) {
                button.appendChild(this.firstChild);
              }
              this.appendChild(button);
              router.initializeRequest(button, {
                to,
                method,
                pushUrl: parseBoolean(
                  this.getAttribute("push-url"),
                  method === "get"
                )
              });
            }
          }
        );
      }
      if (!customElements.get("spice-nav")) {
        customElements.define(
          "spice-nav",
          class extends HTMLElement {
            connectedCallback() {
              router.processBoostContainer(this);
            }
          }
        );
      }
      if (!customElements.get("spice-boost")) {
        customElements.define(
          "spice-boost",
          class extends HTMLElement {
            connectedCallback() {
              router.processBoostContainer(this);
            }
          }
        );
      }
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
              document.addEventListener(
                "htmx:beforeRequest",
                this.onBeforeRequest
              );
              document.addEventListener(
                "htmx:afterRequest",
                this.onAfterRequest
              );
              [
                "htmx:sendError",
                "htmx:timeout",
                "htmx:sendAbort",
                "htmx:responseError"
              ].forEach((event) => {
                document.addEventListener(
                  event,
                  this.onRequestError
                );
              });
            }
            disconnectedCallback() {
              document.removeEventListener(
                "htmx:beforeRequest",
                this.onBeforeRequest
              );
              document.removeEventListener(
                "htmx:afterRequest",
                this.onAfterRequest
              );
              [
                "htmx:sendError",
                "htmx:timeout",
                "htmx:sendAbort",
                "htmx:responseError"
              ].forEach((event) => {
                document.removeEventListener(
                  event,
                  this.onRequestError
                );
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
              emit(this, ROUTER_EVENTS.LOADING, {
                element: this
              });
            }
            hide() {
              this.style.display = "none";
              this.classList.remove("loading", "active");
              emit(this, ROUTER_EVENTS.LOADED, {
                element: this
              });
            }
          }
        );
      }
    }
    /* ---------------------------------------------------------------------- */
    /* Configuration                                                          */
    /* ---------------------------------------------------------------------- */
    resolveConfig(element) {
      const config = {
        ...this.options
      };
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
        const target = source.getAttribute(
          isRequestElement ? "hx-target" : "target"
        );
        const select = source.getAttribute("select");
        const swap = source.getAttribute("swap");
        const transition = source.getAttribute("transition");
        const preload = source.getAttribute("preload");
        const pushUrl = source.getAttribute("push-url");
        if (target !== null) config.target = target;
        if (select !== null) config.select = select;
        if (swap !== null) config.swap = swap;
        if (transition !== null) {
          config.transition = parseBoolean(
            transition,
            config.transition
          );
        }
        if (preload !== null) {
          config.preload = parseBoolean(
            preload,
            config.preload
          );
        }
        if (pushUrl !== null) {
          config.pushUrl = parseBoolean(
            pushUrl,
            config.pushUrl
          );
        }
      };
      containers.forEach((container) => apply(container));
      apply(element, true);
      config.target || (config.target = "spice-app");
      config.select || (config.select = config.target);
      config.swap || (config.swap = DEFAULTS.swap);
      return config;
    }
    /* ---------------------------------------------------------------------- */
    /* Request initialization                                                 */
    /* ---------------------------------------------------------------------- */
    initializeRequest(element, {
      to,
      method = "get",
      pushUrl
    } = {}) {
      if (!element || !to) return false;
      method = method.toLowerCase();
      if (!HTTP_METHODS.has(method)) {
        console.error(`SpiceRouter: Unsupported method "${method}".`);
        return false;
      }
      if (!isInternalURL(to)) return false;
      const config = this.resolveConfig(element);
      const effectivePushUrl = pushUrl ?? (method === "get" && config.pushUrl);
      element.setAttribute(`hx-${method}`, to);
      element.setAttribute("hx-target", config.target);
      element.setAttribute("hx-select", config.select);
      const swap = config.transition ? `${config.swap} transition:true` : config.swap;
      element.setAttribute("hx-swap", swap);
      if (method === "get") {
        element.setAttribute(
          "hx-push-url",
          effectivePushUrl ? "true" : "false"
        );
      } else if (effectivePushUrl) {
        element.setAttribute("hx-push-url", "true");
      }
      element.dataset.spiceNavigation = "true";
      element.dataset.spiceRouterProcessed = "true";
      if (config.preload) {
        element.setAttribute("preload", "mouseover");
      }
      if (window.htmx) {
        window.htmx.process(element);
      }
      return true;
    }
    /* ---------------------------------------------------------------------- */
    /* Boost containers                                                       */
    /* ---------------------------------------------------------------------- */
    processBoostContainer(container) {
      if (!container) return;
      container.querySelectorAll("a[href]").forEach((anchor) => {
        if (anchor.dataset.spiceRouterProcessed === "true") return;
        if (!shouldEnhanceAnchor(anchor)) return;
        const to = anchor.getAttribute("href");
        if (this.initializeRequest(anchor, {
          to,
          method: "get"
        })) {
          anchor.dataset.spiceLink = "true";
        }
      });
      container.querySelectorAll(
        "button[hx-get], button[hx-post], button[hx-put], button[hx-patch], button[hx-delete]"
      ).forEach((button) => {
        if (button.dataset.spiceRouterProcessed === "true") return;
        const config = this.resolveConfig(button);
        button.setAttribute("hx-target", config.target);
        button.setAttribute("hx-select", config.select);
        if (!button.hasAttribute("hx-swap")) {
          button.setAttribute(
            "hx-swap",
            config.transition ? `${config.swap} transition:true` : config.swap
          );
        }
        button.dataset.spiceNavigation = "true";
        button.dataset.spiceRouterProcessed = "true";
        if (window.htmx) {
          window.htmx.process(button);
        }
      });
    }
    initBoostContainers(root = document) {
      if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) {
        return;
      }
      if (root.matches?.(CONTAINER_SELECTOR)) {
        this.processBoostContainer(root);
      }
      root.querySelectorAll?.(CONTAINER_SELECTOR).forEach((container) => {
        this.processBoostContainer(container);
      });
    }
    processDocument() {
      if (document.body) {
        this.initBoostContainers(document.body);
        if (window.htmx) {
          window.htmx.process(document.body);
        }
      }
      this.refreshActiveLinks();
    }
    processExistingContainers() {
      document.querySelectorAll(
        "[data-spice-router-processed]"
      ).forEach((element) => {
        delete element.dataset.spiceRouterProcessed;
      });
      this.processDocument();
    }
    /* ---------------------------------------------------------------------- */
    /* Active links                                                           */
    /* ---------------------------------------------------------------------- */
    refreshActiveLinks() {
      const currentURL = new URL(window.location.href);
      const currentPath = normalizePath(currentURL.pathname);
      document.querySelectorAll(
        "a[data-spice-link]"
      ).forEach((anchor) => {
        let active = false;
        try {
          const linkURL = new URL(
            anchor.href,
            window.location.href
          );
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
    /* ---------------------------------------------------------------------- */
    /* HTMX event listeners                                                   */
    /* ---------------------------------------------------------------------- */
    initListeners() {
      const events = {
        "htmx:beforeRequest": "beforeRequest",
        "htmx:beforeSwap": "beforeSwap",
        "htmx:afterSwap": "afterSwap",
        "htmx:afterRequest": "afterRequest",
        "htmx:pushedIntoHistory": "pushedIntoHistory",
        "htmx:responseError": "responseError",
        "htmx:sendError": "sendError",
        "htmx:timeout": "timeout",
        "htmx:sendAbort": "sendAbort"
      };
      for (const [event, handler] of Object.entries(events)) {
        document.addEventListener(
          event,
          this.boundHandlers[handler]
        );
      }
      window.addEventListener(
        "popstate",
        this.boundHandlers.popstate
      );
    }
    getTriggerElement(detail) {
      return detail?.requestConfig?.elt || detail?.elt || null;
    }
    isRouterRequest(detail) {
      const element = this.getTriggerElement(detail);
      return Boolean(
        element?.matches?.("[data-spice-navigation]")
      );
    }
    handleBeforeRequest(event) {
      const detail = event.detail || {};
      if (!this.isRouterRequest(detail)) return;
      const element = this.getTriggerElement(detail);
      const beforeEvent = emit(
        element,
        ROUTER_EVENTS.BEFORE_NAVIGATE,
        {
          element,
          target: detail.target,
          xhr: detail.xhr,
          requestConfig: detail.requestConfig
        },
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
        {
          element,
          target: detail.target,
          xhr: detail.xhr,
          requestConfig: detail.requestConfig
        },
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
      emit(target, ROUTER_EVENTS.AFTER_SWAP, {
        element,
        target,
        xhr: detail.xhr
      });
      emit(target, ROUTER_EVENTS.NAVIGATE, {
        element,
        target,
        url: window.location.href,
        xhr: detail.xhr
      });
      this.refreshActiveLinks();
      this.initBoostContainers(target);
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
    /* ---------------------------------------------------------------------- */
    /* Dynamic DOM                                                            */
    /* ---------------------------------------------------------------------- */
    observeDOM() {
      if (this.observer || !document.body) return;
      this.observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
          for (const node of mutation.addedNodes) {
            if (node.nodeType !== Node.ELEMENT_NODE) continue;
            this.initBoostContainers(node);
            const parentContainer = node.closest?.(
              CONTAINER_SELECTOR
            );
            if (parentContainer) {
              this.processBoostContainer(parentContainer);
            }
          }
        }
        this.refreshActiveLinks();
      });
      this.observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }
  };
  var spiceRouter = new SpiceRouter();
  if (typeof window !== "undefined") {
    window.SpiceRouter = spiceRouter;
    spiceRouter.registerElements();
    const start = () => {
      spiceRouter.start();
    };
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", start, {
        once: true
      });
    } else {
      start();
    }
    window.addEventListener("load", () => {
      spiceRouter.start();
      spiceRouter.processDocument();
    }, { once: true });
  }

  // ../djangospice/src/djangospice/spice/static/spice/js/spice-lookup.js
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
  function initializeSpiceLookups(root = document) {
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
  function destroySpiceLookups(root) {
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
  function startSpiceLookup() {
    initializeSpiceLookups(document);
  }
  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      startSpiceLookup,
      { once: true }
    );
  } else {
    startSpiceLookup();
  }
  document.addEventListener("htmx:load", (event) => {
    initializeSpiceLookups(event.detail?.elt || document);
  });
  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    destroySpiceLookups(event.detail?.elt);
  });

  // ../djangospice/src/djangospice/spice/static/spice/js/spice-table.js
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
  function initTableComponents() {
    document.querySelectorAll("[data-table]").forEach((el) => {
      if (!el.__tableInstance) {
        el.__tableInstance = new SpiceTable(el);
      }
    });
  }
  document.addEventListener("DOMContentLoaded", () => {
    initTableComponents();
  });
  document.addEventListener("htmx:afterSwap", () => {
    initTableComponents();
  });

  // ../djangospice/src/djangospice/spice/static/spice/js/spice-socket.js
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
  var SpiceSocketManager = class {
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
      let socket;
      try {
        socket = new WebSocketClass(this.getUrl());
        this.socket = socket;
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
        socket.addEventListener("open", (event) => {
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
        socket.addEventListener("message", (event) => {
          if (generation !== this.generation) return;
          this.handleMessage(event);
        });
        socket.addEventListener("error", (event) => {
          if (generation !== this.generation) return;
          this.emit("error", event);
        });
        socket.addEventListener("close", (event) => {
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
      const socket = this.socket;
      this.socket = null;
      if (socket && globalThis.WebSocket && socket.readyState !== globalThis.WebSocket.CLOSED && socket.readyState !== globalThis.WebSocket.CLOSING) {
        socket.close(code, reason);
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
  var SpiceSocket = new SpiceSocketManager();
  var _a, _b;
  if (typeof window !== "undefined") {
    window.Djangospice ?? (window.Djangospice = {});
    (_a = window.Djangospice).SpiceSocketManager ?? (_a.SpiceSocketManager = SpiceSocketManager);
    (_b = window.Djangospice).SpiceSocket ?? (_b.SpiceSocket = SpiceSocket);
  }
})();
//# sourceMappingURL=javascript.js.map
