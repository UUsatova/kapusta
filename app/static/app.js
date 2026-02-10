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

let amountChart = null;

function colorByIndex(index) {
  const palette = [
    'rgba(30, 136, 229, 0.75)',
    'rgba(67, 160, 71, 0.75)',
    'rgba(255, 167, 38, 0.75)',
    'rgba(239, 83, 80, 0.75)',
    'rgba(171, 71, 188, 0.75)',
    'rgba(38, 198, 218, 0.75)',
    'rgba(255, 112, 67, 0.75)',
    'rgba(124, 179, 66, 0.75)'
  ];
  return palette[index % palette.length];
}

function renderAmountStackedChart(labels, datasets) {
  const canvas = document.getElementById('amount-chart');
  if (!canvas || !window.Chart) {
    return;
  }

  const ctx = canvas.getContext('2d');

  if (amountChart) {
    amountChart.destroy();
  }

  const amountFormatter = new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  const barValuePlugin = {
    id: 'barValuePlugin',
    afterDatasetsDraw(chart) {
      const {ctx} = chart;
      ctx.save();
      ctx.fillStyle = '#334155';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';

      const topDatasetIndex = chart.data.datasets.length - 1;
      const topMeta = chart.getDatasetMeta(topDatasetIndex);
      topMeta.data.forEach((bar, index) => {
        const stackTotal = chart.data.datasets.reduce((acc, ds) => acc + (Number(ds.data[index]) || 0), 0);
        ctx.fillText(`${stackTotal.toFixed(0)}`, bar.x, bar.y - 4);
      });
      ctx.restore();
    }
  };

  const styledDatasets = datasets.map((ds, index) => ({
    label: `period_days: ${ds.label}`,
    data: ds.data,
    backgroundColor: colorByIndex(index),
    borderColor: '#ffffff',
    borderWidth: 1,
    stack: 'period'
  }));

  amountChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: styledDatasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          title: {
            display: true,
            text: 'amount'
          },
          ticks: {
            callback(value) {
              const raw = this.getLabelForValue(value);
              const parsed = Number(raw);
              if (Number.isNaN(parsed)) {
                return raw;
              }
              return amountFormatter.format(parsed);
            }
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'count(amount)'
          },
          stacked: true
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            title(items) {
              if (!items.length) {
                return '';
              }
              const parsed = Number(items[0].label);
              return `amount: ${Number.isNaN(parsed) ? items[0].label : amountFormatter.format(parsed)}`;
            },
            label(item) {
              return `${item.dataset.label}: ${Number(item.raw).toFixed(0)}`;
            },
            afterBody(items) {
              if (!items.length) {
                return '';
              }
              const total = items.reduce((acc, row) => acc + Number(row.raw || 0), 0);
              const lines = [`Сумма по столбцу: ${total.toFixed(0)}`];
              items.forEach((row) => {
                const value = Number(row.raw || 0);
                const share = total ? (value / total) * 100 : 0;
                lines.push(`${row.dataset.label}: ${share.toFixed(1)}%`);
              });
              return lines;
            }
          }
        }
      }
    },
    plugins: [barValuePlugin]
  });
}

document.addEventListener('DOMContentLoaded', initDataTable);
document.body.addEventListener('htmx:afterSwap', function (evt) {
  if (evt.target.id === 'table-container') {
    initDataTable();
  }
});
