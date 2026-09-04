import './bootstrap';
import collapse from '@alpinejs/collapse'
import mask from '@alpinejs/mask'
import Chart from 'chart.js/auto'
import * as Money from './components/money.js'
import * as Helpers from './components/helpers.js'
import datepicker from './components/datepicker.js'
import selectSearch from "./components/select-search.js";
import select from "./components/select.js";
import multiSelect from "./components/multi-select.js";
import multiSelectSearch from "./components/multi-select-search.js";
import fileUpload from "./components/file-upload.js";
import multipleUpload from "./components/multiple-upload.js";
import autocomplete from "./components/autocomplete.js";

window.Money = Money;
window.Helpers = Helpers;
window.Chart = Chart;

Alpine.data('datepicker', datepicker);
Alpine.data('selectSearch', selectSearch);
Alpine.data('select', select);
Alpine.data('multiSelect', multiSelect);
Alpine.data('multiSelectSearch', multiSelectSearch);
Alpine.data('fileUpload', fileUpload);
Alpine.data('multipleUpload', multipleUpload);
Alpine.data('autocomplete', autocomplete);
Alpine.plugin(mask);
Alpine.plugin(collapse);

if (localStorage.getItem('asideOpen') === null) {
  localStorage.setItem('asideOpen', 'true');
}
