document.addEventListener('DOMContentLoaded', () => {
    Alpine.start()
});


document.body.addEventListener("htmx:configRequest", function (event) {
    const token = document.querySelector('meta[name="csrf-token"]').content;
    event.detail.headers['X-CSRFToken'] = token;

    // Only apply to the specific filter form
    const form = event.detail.elt.closest(".htmx-table-filter");
    
    if (!form) return;

    const params = event.detail.parameters;

    for (const key in params) {
        // Remove the parameter if it's an empty string, null, or undefined
        if (params[key] === "" || params[key] === null || params[key] === undefined) {
            delete params[key];
        }
    }
});


const modal = document.getElementById("htmx-confirm-modal");
const modalMessage = document.getElementById("htmx-confirm-modal-message");
const btnCancel = document.getElementById("htmx-confirm-modal-cancel");
const btnOk = document.getElementById("htmx-confirm-modal-ok");


document.addEventListener('alpine:init', () => {
    Alpine.data('handleBulkSelect', handleBulkSelect);
    Alpine.data('handleBulkAction', handleBulkAction);
});


document.addEventListener("contextmenu", function (e) {
    const row = e.target.closest("tr[data-row-actions]");
    if (!row) return;
  
    let actions;
    try {
        actions = JSON.parse(row.dataset.rowActions);
    } catch {
        return;
    }

    if (!Array.isArray(actions) || actions.length === 0) {
        return;
    }
  
    e.preventDefault();
    showContextMenu(e.pageX, e.pageY, actions);
});
  

document.addEventListener("dblclick", e => {

    const row = e.target.closest("tr[data-row-actions]");
    if (!row) return;

    // Ignore interactive elements inside the row
    if (e.target.closest("a, button, input, select, textarea")) return;

    let actions;
    try {
        actions = JSON.parse(row.dataset.rowActions);
    } catch {
        return;
    }

    if (!Array.isArray(actions) || actions.length === 0) return;

    // Pick primary action that is NOT HTMX and has a URL
    const primary = actions.find(a => a.is_primary && !a.is_htmx && a.url);
    if (!primary) return;

    window.location.href = primary.url;
});

  
document.addEventListener("click",  () => {
    hideContextMenu();
});


document.addEventListener("DOMContentLoaded", () => {
    markClickableRows();
});


document.body.addEventListener("htmx:afterSwap", e => {
    markClickableRows(e.target);
});


function markClickableRows(root = document) {
    // If root itself is a <tr>, we need to include it
    const rows = [];
    if (root.matches && root.matches("tr[data-row-actions]")) {
        rows.push(root);
    }
    rows.push(...root.querySelectorAll("tr[data-row-actions]"));

    rows.forEach(row => {
        try {
            const actions = JSON.parse(row.dataset.rowActions);

            // clickable if a primary action exists that is NOT HTMX
            const hasPrimary = actions.some(
                a => a.is_primary && !a.is_htmx && a.url
            );

            row.classList.toggle("row-clickable", hasPrimary);
        } catch {
            row.classList.remove("row-clickable");
        }
    });
}


function handleBulkSelect() {
    return {
        selected: [],

        init() {
            // Attach listeners only inside this component
            const container = this.$el;

            // Select-all checkbox
            const selectAll = container.querySelector('input[name="selectall"]')
            if (selectAll) {
                selectAll.addEventListener('change', (e) => this.toggleAll(e))
            }

            // Row checkboxes
            container.querySelectorAll('input[name="selection"]').forEach(cb => {
                cb.addEventListener('change', (e) => this.toggleRow(e))
            })
        },

        toggleAll(e) {
            const checked = e.target.checked
            this.$el.querySelectorAll('input[name="selection"]').forEach(cb => cb.checked = checked)
            this.syncSelected()
        },

        toggleRow(e) {
            if (!e.target.checked) {
                const selectAll = this.$el.querySelector('input[name="selectall"]')
                if (selectAll) selectAll.checked = false
            }
            this.syncSelected()
        },

        syncSelected() {
            const checkboxes = this.$el.querySelectorAll('input[name="selection"]');
            
            // 1. Update the 'selected' array
            this.selected = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);

            // 2. Toggle  'table-active' class on the parent row
            checkboxes.forEach(cb => {
                const row = cb.closest('tr');
                if (row) {
                    cb.checked 
                        ? row.classList.add('htmx-table-active') 
                        : row.classList.remove('htmx-table-active');
                }
            });
        }
    }
}


function handleBulkAction() {
    return {
        handleConfirm(evt) {
            const option = this.$refs.actionSelect.selectedOptions[0];
            const canConfirm = option?.dataset.confirm === 'true';
            const confirmMessage = option?.dataset.message;

            if (canConfirm) {
                evt.preventDefault(); 

                showConfirmModal(confirmMessage, () => {
                    evt.detail.issueRequest(); 
                    hideConfirmModal();
                });
            }
        }
    }
}


function showContextMenu(x, y, actions) {
    const menu = document.getElementById("htmx-context-menu");
    menu.innerHTML = "";
  
    actions.forEach(action => {
        const btn = document.createElement("button");
        if (action.is_danger) btn.classList.add("danger");
    
        btn.innerHTML = `
            ${action.icon ? `<i class="${action.icon}"></i>` : ""}
            <span>${action.label}</span>
        `;
  
        btn.onclick = (event) => executeMenuAction(action, event);
    
        menu.appendChild(btn);
    });
  
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.classList.remove("hidden");
  
}

  
function hideContextMenu() {
    const contextMenu = document.getElementById("htmx-context-menu");
    if (contextMenu) {
        contextMenu.classList.add("hidden");
    }
}


function executeMenuAction(action, event) {
    if (action.confirm) {
        showConfirmModal(action.confirm, () => sendAjaxRequest(action, event));
    } else {
        sendAjaxRequest(action, event);
    }
}


function sendAjaxRequest(action, event) {
    if (action.is_htmx) {
        htmx.ajax(action.hx_method, action.hx_url, {
            source: event.currentTarget,
            target: action.hx_target,
            values: action.payload
        });
    } else {
        window.location.href = action.url;
    }

    hideConfirmModal();
}


function showConfirmModal(message, onConfirm) {
    modalMessage.textContent = message;

    function confirmHandler() {
        onConfirm();
        removeListeners();
    }

    function cancelHandler() {
        hideConfirmModal();
        removeListeners();
    }

    function removeListeners() {
        btnOk.removeEventListener("click", confirmHandler);
        btnCancel.removeEventListener("click", cancelHandler);
        modal.removeEventListener("cancel", cancelHandler);
    }

    btnOk.addEventListener("click", confirmHandler);
    btnCancel.addEventListener("click", cancelHandler);

    // close modal on ESC key
    modal.addEventListener("cancel", cancelHandler);

    modal.showModal();
}


function hideConfirmModal() {
    if (modal.open) {
        modal.close();
    }
}
