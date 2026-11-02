var Djangospice = (() => {
  // ../djangospice/src/djangospice/lookup/static/lookup/js/index.js
  (function(window2, document2) {
    "use strict";
    const SELECTOR = "select[data-djangospice-lookup]";
    const EVENT_PREFIX = "djangospice:lookup";
    const DEFAULTS = Object.freeze({
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
    const instances = /* @__PURE__ */ new WeakMap();
    function parseBoolean(value, fallback) {
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
      if (!value) {
        return [];
      }
      return String(value).split(",").map((item) => item.trim()).filter(Boolean);
    }
    function debounce(callback, delay) {
      let timer = null;
      const debounced = function(...args) {
        window2.clearTimeout(timer);
        timer = window2.setTimeout(
          () => callback.apply(this, args),
          delay
        );
      };
      debounced.cancel = function() {
        window2.clearTimeout(timer);
        timer = null;
      };
      return debounced;
    }
    function escapeSelector(value) {
      if (window2.CSS && typeof window2.CSS.escape === "function") {
        return window2.CSS.escape(value);
      }
      return String(value).replace(/[\^$.*+?()[\]{}|]/g, "\\$&");
    }
    function createElement(tag, className, attributes = {}) {
      const element = document2.createElement(tag);
      if (className) {
        element.className = className;
      }
      for (const [name, value] of Object.entries(attributes)) {
        if (value === null || value === void 0) {
          continue;
        }
        if (value === true) {
          element.setAttribute(name, "");
        } else if (value !== false) {
          element.setAttribute(name, String(value));
        }
      }
      return element;
    }
    class LookupController {
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
          delay: DEFAULTS.delay,
          pageSize: parseInteger(data.lookupPageSize, DEFAULTS.pageSize),
          minimumInputLength: parseInteger(data.lookupMinSearchLength, DEFAULTS.minimumInputLength),
          searchParam: data.lookupSearchParam || DEFAULTS.searchParam,
          pageParam: data.lookupPageParam || DEFAULTS.pageParam,
          pageSizeParam: data.lookupPageSizeParam || DEFAULTS.pageSizeParam,
          placeholder: data.lookupPlaceholder || DEFAULTS.placeholder,
          searchPlaceholder: data.lookupSearchPlaceholder || DEFAULTS.searchPlaceholder,
          allowClear: parseBoolean(data.lookupAllowClear, DEFAULTS.allowClear),
          token: data.lookupToken || null,
          tokenHeader: data.lookupTokenHeader || DEFAULTS.tokenHeader
        };
      }
      initialize() {
        this.dependencies = this.readDependencies();
        this.createInterface();
        this.bindEvents();
        this.bindDependencies();
        this.syncDisabledState();
        this.syncFromSelect();
        this.renderInitialResults();
      }
      readDependencies() {
        return parseDependencies(this.select.dataset.lookupDependencies);
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
      createInterface() {
        const parent = this.select.parentNode;
        if (!parent) return;
        this.wrapper = createElement("div", "djangospice-lookup");
        this.wrapper.dataset.djangospiceLookupWrapper = "";
        if (this.select.multiple) {
          this.selection = createElement("div", "djangospice-lookup__selection");
        } else {
          this.selection = null;
        }
        this.search = createElement("input", "djangospice-lookup__input", {
          type: "search",
          autocomplete: "off",
          role: "combobox",
          "aria-autocomplete": "list",
          "aria-expanded": "false",
          "aria-haspopup": "listbox",
          placeholder: this.config.searchPlaceholder
        });
        if (this.config.allowClear) {
          this.clearButton = createElement("button", "djangospice-lookup__clear", {
            type: "button",
            "aria-label": "Clear selection"
          });
          this.clearButton.textContent = "\xD7";
        } else {
          this.clearButton = null;
        }
        this.listbox = createElement("div", "djangospice-lookup__dropdown", {
          role: "listbox",
          tabindex: "-1"
        });
        this.status = createElement("div", "djangospice-lookup__status", {
          role: "status",
          "aria-live": "polite"
        });
        this.status.hidden = true;
        parent.insertBefore(this.wrapper, this.select);
        if (this.selection) {
          this.wrapper.appendChild(this.selection);
        }
        this.wrapper.appendChild(this.search);
        if (this.clearButton) {
          this.wrapper.appendChild(this.clearButton);
        }
        this.wrapper.appendChild(this.listbox);
        this.wrapper.appendChild(this.status);
        this.wrapper.appendChild(this.select);
        this.select.classList.add("djangospice-lookup__native");
        this.listbox.id = this.getListboxId();
        this.search.setAttribute("aria-controls", this.listbox.id);
        this.wrapper.classList.add("is-enhanced");
      }
      syncDisabledState() {
        const disabled = this.select.disabled || this.hasDependencies() && !this.isDependencySatisfied();
        this.search.disabled = disabled;
        if (this.clearButton) {
          this.clearButton.disabled = disabled;
        }
        this.wrapper.classList.toggle("is-disabled", disabled);
        this.wrapper.setAttribute("aria-disabled", String(disabled));
      }
      getListboxId() {
        if (this.select.id) {
          return `${this.select.id}-lookup-listbox`;
        }
        return `djangospice-lookup-${Math.random().toString(36).slice(2)}`;
      }
      // ============================================================
      // Events
      // ============================================================
      bindEvents() {
        this.handleSearch = debounce(() => {
          this.searchLookup();
        }, this.config.delay);
        this.search.addEventListener("input", this.handleSearch);
        this.search.addEventListener("focus", () => {
        });
        this.search.addEventListener("click", () => {
          if (this.select.disabled) {
            return;
          }
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
          if (option) {
            event.preventDefault();
          }
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
            const removeBtn = event.target.closest("[data-lookup-remove]");
            if (!removeBtn) return;
            event.stopPropagation();
            this.toggleMultipleValue(removeBtn.dataset.lookupRemove);
          });
        }
        this.select.addEventListener("change", () => {
          this.syncFromSelect();
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
        document2.addEventListener("mousedown", this.handleDocumentClick);
      }
      // ============================================================
      // Dependencies
      // ============================================================
      bindDependencies() {
        for (const dependency of this.dependencies) {
          const source = this.findDependency(dependency);
          if (!source) continue;
          const handler = () => {
            this.handleDependencyChange();
          };
          source.addEventListener("change", handler);
          this.dependencyListeners.push({ element: source, handler });
        }
      }
      findDependency(name) {
        if (!name) return null;
        const lookup = document2.querySelector(`[data-lookup-name="${escapeSelector(name)}"]`);
        if (lookup) return lookup;
        return document2.querySelector(`[name="${escapeSelector(name)}"]`);
      }
      isDependencySatisfied() {
        if (!this.hasDependencies()) {
          return true;
        }
        return this.dependencies.every((dependency) => {
          const value = this.getDependencyValue(dependency);
          if (Array.isArray(value)) {
            return value.length > 0;
          }
          return value !== null && value !== void 0 && value !== "";
        });
      }
      handleDependencyChange() {
        if (!this.hasDependencies()) {
          return;
        }
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
      // ============================================================
      // Search & Loading
      // ============================================================
      searchLookup() {
        const term = this.search.value.trim();
        if (this.hasDependencies() && !this.isDependencySatisfied()) {
          this.clearLookupResults();
          this.close();
          return;
        }
        if (term.length < this.config.minimumInputLength) {
          if (this.hasDependencies()) {
            return;
          }
          this.clearRemoteResults({
            restoreInitial: true
          });
          if (this.config.minimumInputLength) {
            this.setStatus(
              `Enter at least ${this.config.minimumInputLength} character${this.config.minimumInputLength === 1 ? "" : "s"}.`
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
        this.abortController = new AbortController();
        const url = new URL(this.config.url, window2.location.origin);
        if (term) {
          url.searchParams.set(this.config.searchParam, term);
        }
        url.searchParams.set(this.config.pageParam, String(page));
        url.searchParams.set(this.config.pageSizeParam, String(this.config.pageSize));
        this.appendDependencies(url);
        const headers = { Accept: "application/json" };
        if (this.config.token) {
          headers[this.config.tokenHeader] = this.config.token;
        }
        this.setLoading(true);
        try {
          const response = await fetch(url.toString(), {
            method: "GET",
            headers,
            credentials: "same-origin",
            signal: this.abortController.signal
          });
          if (this.destroyed || requestId !== this.requestSequence) return;
          if (!response.ok) {
            throw new Error(`Lookup request failed: ${response.status}`);
          }
          const data = await response.json();
          this.handleResponse(data, { page, replace });
        } catch (error) {
          if (error.name === "AbortError") return;
          this.setError("Unable to load results.");
          this.dispatch("error", { error });
        } finally {
          if (requestId === this.requestSequence) {
            this.setLoading(false);
          }
        }
      }
      appendDependencies(url) {
        for (const dependency of this.dependencies) {
          const value = this.getDependencyValue(dependency);
          if (value === null || value === void 0 || value === "") continue;
          if (Array.isArray(value)) {
            for (const item of value) {
              url.searchParams.append(dependency, item);
            }
            continue;
          }
          url.searchParams.set(dependency, value);
        }
      }
      abortRequest() {
        if (this.abortController) {
          this.abortController.abort();
          this.abortController = null;
        }
      }
      // ============================================================
      // Response & Rendering
      // ============================================================
      handleResponse(data, { page, replace }) {
        const results = Array.isArray(data?.results) ? data.results : [];
        if (replace) {
          this.clearRemoteResults({ restoreInitial: false });
        }
        this.renderResults(results);
        const pagination = data?.pagination || {};
        this.hasNext = Boolean(pagination.has_next ?? pagination.more ?? false);
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
          Array.from(this.listbox.querySelectorAll("[data-lookup-option]")).map(
            (option) => option.dataset.lookupValue
          )
        );
        for (const result of results) {
          const value = result?.value ?? result?.id ?? "";
          const label = result?.label ?? result?.text ?? "";
          if (!value) continue;
          const stringValue = String(value);
          if (existing.has(stringValue)) continue;
          const option = createElement("div", "djangospice-lookup__option", {
            role: "option",
            "data-lookup-option": "",
            "data-lookup-value": stringValue
          });
          option.textContent = label;
          if (selected.has(stringValue)) {
            option.classList.add("is-selected");
            option.setAttribute("aria-selected", "true");
          } else {
            option.setAttribute("aria-selected", "false");
          }
          this.listbox.appendChild(option);
          existing.add(stringValue);
        }
        this.updateHighlight();
      }
      checkLoadMore() {
        if (this.loading || !this.hasNext) return;
        const threshold = 50;
        const position = this.listbox.scrollTop + this.listbox.clientHeight;
        const height = this.listbox.scrollHeight;
        if (height - position <= threshold) {
          const term = this.search.value.trim();
          this.load({ term, page: this.page + 1, replace: false });
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
      getSelectedValues() {
        return Array.from(this.select.selectedOptions).map((option) => option.value);
      }
      selectResult(value, label = null) {
        if (!value) return;
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
          if (option.value === stringValue) {
            option.selected = !option.selected;
            found = true;
            break;
          }
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
        this.clearRemoteResults({ restoreInitial });
      }
      syncFromSelect() {
        const selectedValues = new Set(this.getSelectedValues());
        if (!this.select.multiple) {
          const selectedValue = this.getSelectedValues()[0];
          this.search.value = selectedValue ? this.getOptionLabel(selectedValue) : "";
        }
        const optionEls = this.listbox.querySelectorAll("[data-lookup-option]");
        optionEls.forEach((el) => {
          const isSelected = selectedValues.has(el.dataset.lookupValue);
          el.classList.toggle("is-selected", isSelected);
          el.setAttribute("aria-selected", String(isSelected));
        });
        if (this.selection) {
          this.selection.innerHTML = "";
          for (const value of selectedValues) {
            const label = this.getOptionLabel(value);
            const tag = createElement("span", "djangospice-lookup__tag", {
              "data-lookup-tag": value
            });
            tag.textContent = label;
            const removeBtn = createElement("button", "djangospice-lookup__tag-remove", {
              type: "button",
              "aria-label": `Remove ${label}`,
              "data-lookup-remove": value
            });
            removeBtn.textContent = "\xD7";
            tag.appendChild(removeBtn);
            this.selection.appendChild(tag);
          }
        }
      }
      getOptionLabel(value) {
        const option = Array.from(this.select.options).find((opt) => opt.value === String(value));
        if (option) return option.textContent;
        const optionEl = this.listbox.querySelector(`[data-lookup-value="${escapeSelector(value)}"]`);
        if (optionEl) return optionEl.textContent;
        return value;
      }
      dispatchChange() {
        this.select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      dispatch(eventName, detail = {}) {
        const event = new CustomEvent(`${EVENT_PREFIX}:${eventName}`, {
          detail,
          bubbles: true,
          cancelable: true
        });
        this.wrapper.dispatchEvent(event);
      }
      open() {
        if (this.select.disabled || this.hasDependencies() && !this.isDependencySatisfied()) {
          return;
        }
        this.wrapper.classList.add("is-open");
        this.search.setAttribute("aria-expanded", "true");
      }
      close() {
        this.wrapper.classList.remove("is-open");
        this.search.setAttribute("aria-expanded", "false");
        this.highlightedIndex = -1;
        this.updateHighlight();
      }
      handleKeydown(event) {
        const options = Array.from(this.listbox.querySelectorAll("[data-lookup-option]"));
        switch (event.key) {
          case "ArrowDown":
            event.preventDefault();
            if (!this.wrapper.classList.contains("is-open")) {
              this.open();
            } else if (options.length) {
              this.highlightedIndex = (this.highlightedIndex + 1) % options.length;
              this.updateHighlight();
              this.scrollHighlightedIntoView(options[this.highlightedIndex]);
            }
            break;
          case "ArrowUp":
            event.preventDefault();
            if (options.length) {
              this.highlightedIndex = (this.highlightedIndex - 1 + options.length) % options.length;
              this.updateHighlight();
              this.scrollHighlightedIntoView(options[this.highlightedIndex]);
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
        const options = Array.from(this.listbox.querySelectorAll("[data-lookup-option]"));
        options.forEach((el, index) => {
          const isHighlighted = index === this.highlightedIndex;
          el.classList.toggle("is-highlighted", isHighlighted);
        });
      }
      scrollHighlightedIntoView(optionEl) {
        if (!optionEl) return;
        const parent = this.listbox;
        const parentRect = parent.getBoundingClientRect();
        const optionRect = optionEl.getBoundingClientRect();
        if (optionRect.bottom > parentRect.bottom) {
          parent.scrollTop += optionRect.bottom - parentRect.bottom;
        } else if (optionRect.top < parentRect.top) {
          parent.scrollTop -= parentRect.top - optionRect.top;
        }
      }
      destroy() {
        this.destroyed = true;
        this.abortRequest();
        this.handleSearch.cancel();
        document2.removeEventListener("mousedown", this.handleDocumentClick);
        for (const { element, handler } of this.dependencyListeners) {
          element.removeEventListener("change", handler);
        }
        if (this.wrapper && this.wrapper.parentNode) {
          this.wrapper.parentNode.insertBefore(this.select, this.wrapper);
          this.wrapper.remove();
        }
        this.select.classList.remove("djangospice-lookup__native");
      }
    }
    function initializeLookups(root = document2) {
      const selects = [];
      if (root instanceof Element && root.matches(SELECTOR)) {
        selects.push(root);
      }
      if (typeof root.querySelectorAll === "function") {
        selects.push(...root.querySelectorAll(SELECTOR));
      }
      selects.forEach((select) => {
        if (!instances.has(select)) {
          instances.set(select, new LookupController(select));
        }
      });
    }
    if (document2.readyState === "loading") {
      document2.addEventListener(
        "DOMContentLoaded",
        () => initializeLookups(),
        { once: true }
      );
    } else {
      initializeLookups();
    }
    document2.addEventListener("htmx:load", (event) => {
      initializeLookups(event.detail.elt);
    });
  })(window, document);

  // ../djangospice/src/djangospice/notification/static/notification/js/index.js
  (function(global) {
    "use strict";
    const Djangospice = global.Djangospice ?? (global.Djangospice = {});
    const EVENT_TYPES = [
      "notification_created",
      "notification_read",
      "notification_unread",
      "notification_deleted"
    ];
    class Notification {
      constructor() {
        this.listeners = /* @__PURE__ */ new Map();
        this.initialized = false;
        this.realtime = null;
        this.realtimeHandlers = [];
      }
      initialize() {
        if (this.initialized) return this;
        this.bindRealtimeEvents();
        this.initialized = true;
        return this;
      }
      /**
       * Normalize serialized Python values recursively.
       */
      normalize(value) {
        if (value === null || value === void 0) {
          return value;
        }
        if (Array.isArray(value)) {
          return value.map((item) => this.normalize(item));
        }
        if (typeof value !== "object") {
          return value;
        }
        if (value.__type__ === "dataclass") {
          return this.normalize(value.data);
        }
        if (value.__type__ === "uuid_primitive") {
          return value.value;
        }
        return Object.fromEntries(
          Object.entries(value).map(([key, item]) => [
            key,
            this.normalize(item)
          ])
        );
      }
      /**
       * Subscribe to original server event names.
       */
      bindRealtimeEvents() {
        const realtime = Djangospice.Realtime;
        if (!realtime || this.realtime === realtime) return;
        this.realtime = realtime;
        for (const eventName of EVENT_TYPES) {
          const handler = (event) => {
            this.handleRealtimeEvent(eventName, event);
          };
          realtime.on(eventName, handler);
          this.realtimeHandlers.push([
            eventName,
            handler
          ]);
        }
      }
      /**
       * Forward the complete normalized server payload.
       */
      handleRealtimeEvent(eventName, event) {
        const payload = this.normalize(event?.data ?? event);
        if (!payload || typeof payload !== "object") {
          return;
        }
        this.emit(eventName, payload);
      }
      on(event, callback) {
        if (typeof callback !== "function") {
          throw new TypeError(
            "Notification listener must be a function."
          );
        }
        if (!this.listeners.has(event)) {
          this.listeners.set(event, /* @__PURE__ */ new Set());
        }
        this.listeners.get(event).add(callback);
        return () => this.off(event, callback);
      }
      off(event, callback) {
        this.listeners.get(event)?.delete(callback);
      }
      emit(event, data = null) {
        this.listeners.get(event)?.forEach((callback) => {
          try {
            callback(data);
          } catch (error) {
            console.error(
              `Notification listener failed (${event}):`,
              error
            );
          }
        });
      }
      destroy() {
        if (this.realtime) {
          for (const [event, handler] of this.realtimeHandlers) {
            this.realtime.off?.(event, handler);
          }
        }
        this.realtimeHandlers = [];
        this.realtime = null;
        this.listeners.clear();
        this.initialized = false;
      }
    }
    Djangospice.NotificationClass ?? (Djangospice.NotificationClass = Notification);
    Djangospice.Notification ?? (Djangospice.Notification = new Notification());
  })(globalThis);

  // ../djangospice/src/djangospice/table_widget/static/table_widget/js/index.js
  var TableContextMenu = class {
    constructor(menu) {
      this.menu = menu;
      this.tableId = menu.dataset.tableId;
      this.rowId = null;
      this.table = null;
      this.onContextMenu = this.onContextMenu.bind(this);
      this.onDocumentClick = this.onDocumentClick.bind(this);
      this.onDocumentKeydown = this.onDocumentKeydown.bind(this);
      this.onActionClick = this.onActionClick.bind(this);
      this.initialize();
    }
    initialize() {
      this.table = document.getElementById(this.tableId);
      if (!this.table) {
        return;
      }
      this.table.addEventListener(
        "contextmenu",
        this.onContextMenu
      );
      document.addEventListener(
        "click",
        this.onDocumentClick
      );
      document.addEventListener(
        "keydown",
        this.onDocumentKeydown
      );
      this.menu.addEventListener(
        "click",
        this.onActionClick
      );
    }
    onContextMenu(event) {
      const row = event.target.closest("[data-table-row]");
      if (!row || !this.table.contains(row)) {
        return;
      }
      const objectId = row.dataset.objectId;
      if (!objectId) {
        return;
      }
      event.preventDefault();
      this.rowId = objectId;
      this.show(
        event.clientX,
        event.clientY
      );
    }
    show(x, y) {
      this.menu.classList.remove("hidden");
      const rect = this.menu.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const margin = 8;
      let left = x;
      let top = y;
      if (left + rect.width > viewportWidth - margin) {
        left = viewportWidth - rect.width - margin;
      }
      if (top + rect.height > viewportHeight - margin) {
        top = viewportHeight - rect.height - margin;
      }
      this.menu.style.left = `${Math.max(margin, left)}px`;
      this.menu.style.top = `${Math.max(margin, top)}px`;
      this.menu.focus();
    }
    hide() {
      this.menu.classList.add("hidden");
    }
    onDocumentClick(event) {
      if (!this.menu.contains(event.target)) {
        this.hide();
      }
    }
    onDocumentKeydown(event) {
      if (event.key !== "Escape") {
        return;
      }
      this.hide();
    }
    onActionClick(event) {
      const action = event.target.closest(
        "[data-context-action]"
      );
      if (!action || !this.menu.contains(action)) {
        return;
      }
      const actionName = action.dataset.action;
      if (!actionName || !this.rowId) {
        return;
      }
      event.preventDefault();
      this.execute(actionName);
      this.hide();
    }
    execute(actionName) {
      if (!this.table || !this.rowId) {
        return;
      }
      const baseUrl = this.table.dataset.url;
      if (!baseUrl) {
        return;
      }
      const url = new URL(
        baseUrl,
        window.location.origin
      );
      url.searchParams.set(
        "action",
        actionName
      );
      url.searchParams.set(
        "selected_id",
        this.rowId
      );
      const target = this.table.dataset.target;
      if (window.htmx) {
        const options = {};
        if (target) {
          options.target = target;
          options.swap = "outerHTML";
        }
        window.htmx.ajax(
          "GET",
          url.toString(),
          options
        );
        return;
      }
      window.location.href = url.toString();
    }
    destroy() {
      if (this.table) {
        this.table.removeEventListener(
          "contextmenu",
          this.onContextMenu
        );
      }
      document.removeEventListener(
        "click",
        this.onDocumentClick
      );
      document.removeEventListener(
        "keydown",
        this.onDocumentKeydown
      );
      this.menu.removeEventListener(
        "click",
        this.onActionClick
      );
      this.hide();
      this.table = null;
      this.rowId = null;
    }
  };
  function initializeTableContextMenus(root = document) {
    root.querySelectorAll("[data-context-menu]").forEach((menu) => {
      if (menu._tableContextMenu) {
        return;
      }
      menu._tableContextMenu = new TableContextMenu(menu);
    });
  }
  document.addEventListener(
    "DOMContentLoaded",
    () => {
      initializeTableContextMenus();
    }
  );
  document.body.addEventListener(
    "htmx:afterSwap",
    (event) => {
      initializeTableContextMenus(
        event.target
      );
    }
  );
  document.body.addEventListener(
    "htmx:beforeCleanupElement",
    (event) => {
      const element = event.target;
      if (element.matches?.("[data-context-menu]")) {
        element._tableContextMenu?.destroy();
        return;
      }
      element.querySelectorAll?.("[data-context-menu]").forEach((menu) => {
        menu._tableContextMenu?.destroy();
      });
    }
  );

  // ../djangospice/src/djangospice/websocket/static/websocket/js/index.js
  (function(global) {
    "use strict";
    const DEFAULT_OPTIONS = {
      path: "/ws/realtime/",
      host: null,
      port: null,
      protocol: null,
      reconnect: true,
      reconnectDelay: 1e3,
      maxReconnectDelay: 3e4,
      maxRetries: Infinity
    };
    class RealtimeManager {
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
        const WebSocketClass = global.WebSocket;
        if (!WebSocketClass) {
          return Promise.reject(
            new Error("Realtime: WebSocket is not supported.")
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
            new Error("Realtime: previous connection is closing.")
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
                `Realtime: connection closed (${event.code}).`
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
          new Error("Realtime: connection cancelled.")
        );
        this.connectionPromise = null;
        this.settleConnection = null;
        const socket = this.socket;
        this.socket = null;
        if (socket && global.WebSocket && socket.readyState !== global.WebSocket.CLOSED && socket.readyState !== global.WebSocket.CLOSING) {
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
        if (!this.socket || !global.WebSocket || this.socket.readyState !== global.WebSocket.OPEN) {
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
            "Realtime: listener must be a function."
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
            global.setTimeout(() => {
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
        this.reconnectTimer = global.setTimeout(() => {
          this.reconnectTimer = null;
          this.connect().catch(() => {
          });
        }, delay);
      }
      clearReconnectTimer() {
        if (this.reconnectTimer !== null) {
          global.clearTimeout(this.reconnectTimer);
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
        return !!this.socket && !!global.WebSocket && this.socket.readyState === global.WebSocket.OPEN;
      }
      get connecting() {
        return this.status === "connecting";
      }
    }
    global.Djangospice ?? (global.Djangospice = {});
    const Djangospice = global.Djangospice;
    Djangospice.RealtimeManager ?? (Djangospice.RealtimeManager = RealtimeManager);
    Djangospice.Realtime ?? (Djangospice.Realtime = new Djangospice.RealtimeManager());
  })(globalThis);
})();
//# sourceMappingURL=javascript.js.map
