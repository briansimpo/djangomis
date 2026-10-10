import "@fortawesome/fontawesome-free/js/all"
import "@/css/main.css";
import "@/css/app.css";
import "@/css/lookup.css";

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

import "@/js/app";
import "@/js/lookup";