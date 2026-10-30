import "@fortawesome/fontawesome-free/js/all"
import "@/css/main.css";
import "@/css/app.css";

import htmx from "htmx.org";
window.htmx = htmx; 

import "htmx-ext-ws";

import Alpine from "alpinejs";
window.Alpine = Alpine

import Sortable from 'sortablejs';
window.Sortable = Sortable

import NProgress from "nprogress";
import "nprogress/nprogress.css";
window.NProgress = NProgress

document.addEventListener('DOMContentLoaded', () => {
    Alpine.start()
});

document.body.addEventListener("htmx:configRequest", function (event) {
    const token = document.querySelector('meta[name="csrf-token"]').content;
    event.detail.headers['X-CSRFToken'] = token;
});

