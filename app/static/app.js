function initDataTable() {
  if (!window.jQuery) {
    return;
  }

  const table = $('#report-table');
  if (!table.length) {
    return;
  }

  if ($.fn.DataTable.isDataTable(table)) {
    table.DataTable().destroy();
  }

  table.DataTable({
    pageLength: 25,
    order: [],
    language: {
      url: 'https://cdn.datatables.net/plug-ins/1.13.8/i18n/ru.json'
    }
  });
}

document.addEventListener('DOMContentLoaded', initDataTable);
document.body.addEventListener('htmx:afterSwap', function (evt) {
  if (evt.target.id === 'table-container') {
    initDataTable();
  }
});
