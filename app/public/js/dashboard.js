// app/public/js/dashboard.js
// Dashboard Page Logic

let charts = {};

async function initDashboard() {
  try {
    // Show loading skeleton/spinners if any
    await loadSummary();
    await loadDashboardTables();
    await loadCharts();
  } catch (err) {
    showToast('Failed to load dashboard data: ' + err.message, 'danger');
  }
}

async function loadSummary() {
  const result = await apiFetch('/dashboard/summary');
  if (result && result.success && result.data) {
    const data = result.data;
    
    // Populate cards
    document.getElementById('kpi-total-products').textContent = formatNumber(data.total_products);
    document.getElementById('kpi-inventory-value').textContent = formatCurrency(data.total_inventory_value);
    document.getElementById('kpi-low-stock').textContent = formatNumber(data.low_stock_count);
    document.getElementById('kpi-pending-orders').textContent = formatNumber(data.pending_orders);
    document.getElementById('kpi-stockout-rate').textContent = (data.stockout_rate || 0) + '%';
    document.getElementById('kpi-monthly-sales').textContent = formatCurrency(data.monthly_sales_total);
    document.getElementById('kpi-sales-transactions').textContent = formatNumber(data.total_sales_transactions);
    document.getElementById('kpi-total-suppliers').textContent = formatNumber(data.total_suppliers);
  }
}

async function loadDashboardTables() {
  // Load low stock alerts table
  try {
    const productsRes = await apiFetch('/products');
    const inventoryRes = await apiFetch('/inventory');
    
    if (productsRes.success && inventoryRes.success) {
      const products = productsRes.data;
      const inventory = inventoryRes.data;
      
      const lowStockList = [];
      
      inventory.forEach(inv => {
        const prod = products.find(p => p.product_id === inv.product_id);
        if (prod && inv.quantity < prod.reorder_point) {
          lowStockList.push({
            sku: prod.sku,
            name: prod.name,
            quantity: inv.quantity,
            reorder_point: prod.reorder_point,
            status: inv.quantity === 0 ? 'Out of Stock' : 'Low Stock'
          });
        }
      });
      
      const tbody = document.getElementById('low-stock-tbody');
      if (tbody) {
        if (lowStockList.length === 0) {
          tbody.innerHTML = `<tr><td colspan="4" class="text-muted text-center" style="padding: 24px;">No low stock alerts</td></tr>`;
        } else {
          tbody.innerHTML = lowStockList.map(item => `
            <tr>
              <td><span class="font-semibold">${item.sku}</span></td>
              <td>${item.name}</td>
              <td><span class="${item.quantity === 0 ? 'text-danger font-semibold' : 'text-warning'}">${item.quantity} / ${item.reorder_point}</span></td>
              <td>
                <span class="badge ${item.quantity === 0 ? 'badge-danger' : 'badge-warning'}">
                  ${item.status}
                </span>
              </td>
            </tr>
          `).join('');
        }
      }
    }
  } catch (e) {
    console.error('Failed to load low stock alerts table:', e);
  }

  // Load pending POs table
  try {
    const poRes = await apiFetch('/purchase-orders?status=Pending');
    const tbody = document.getElementById('pending-po-tbody');
    if (tbody && poRes.success) {
      const pos = poRes.data.slice(0, 5); // top 5
      if (pos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-muted text-center" style="padding: 24px;">No pending purchase orders</td></tr>`;
      } else {
        tbody.innerHTML = pos.map(po => `
          <tr>
            <td><span class="font-semibold">${po.sku || '—'}</span></td>
            <td>${po.supplier_name || 'Supplier'}</td>
            <td>${po.quantity} pcs</td>
            <td><span class="badge badge-warning">Pending</span></td>
          </tr>
        `).join('');
      }
    }
  } catch (e) {
    console.error('Failed to load pending POs table:', e);
  }
}

async function loadCharts() {
  const chartDefaults = getChartDefaults();

  try {
    const salesRes = await apiFetch('/sales');
    const productsRes = await apiFetch('/products');
    const inventoryRes = await apiFetch('/inventory');
    const forecastsRes = await apiFetch('/forecasts');

    if (!salesRes.success || !productsRes.success || !inventoryRes.success) return;

    const sales = salesRes.data;
    const products = productsRes.data;
    const inventory = inventoryRes.data;
    const forecasts = forecastsRes.data || [];

    // 1. Sales Trend (Line) - last 6 months
    const monthlySales = {};
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    // Initialize last 6 calendar months
    const now = new Date();
    const last6Months = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const label = months[d.getMonth()] + ' ' + String(d.getFullYear()).slice(-2);
      last6Months.push({ label, year: d.getFullYear(), month: d.getMonth() + 1, totalSales: 0, revenue: 0 });
    }

    sales.forEach(sale => {
      const sDate = new Date(sale.sale_date);
      const sYear = sDate.getFullYear();
      const sMonth = sDate.getMonth() + 1;
      
      const match = last6Months.find(m => m.year === sYear && m.month === sMonth);
      if (match) {
        match.totalSales += sale.quantity;
        match.revenue += sale.quantity * sale.unit_price;
      }
    });

    const salesTrendCtx = document.getElementById('salesTrendChart')?.getContext('2d');
    if (salesTrendCtx) {
      if (charts.salesTrend) charts.salesTrend.destroy();
      charts.salesTrend = new Chart(salesTrendCtx, {
        type: 'line',
        data: {
          labels: last6Months.map(m => m.label),
          datasets: [{
            label: 'Sales Volume (Qty)',
            data: last6Months.map(m => m.totalSales),
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37,99,235,0.1)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          ...chartDefaults,
          plugins: {
            ...chartDefaults.plugins,
            title: { display: false }
          }
        }
      });
    }

    // 2. Revenue Trend (Bar)
    const revenueTrendCtx = document.getElementById('revenueTrendChart')?.getContext('2d');
    if (revenueTrendCtx) {
      if (charts.revenueTrend) charts.revenueTrend.destroy();
      charts.revenueTrend = new Chart(revenueTrendCtx, {
        type: 'bar',
        data: {
          labels: last6Months.map(m => m.label),
          datasets: [{
            label: 'Revenue ($)',
            data: last6Months.map(m => m.revenue),
            backgroundColor: '#06b6d4',
            borderRadius: 6
          }]
        },
        options: {
          ...chartDefaults
        }
      });
    }

    // 3. Inventory Status (Doughnut)
    let healthyCount = 0;
    let lowCount = 0;
    let outCount = 0;

    inventory.forEach(inv => {
      const prod = products.find(p => p.product_id === inv.product_id);
      if (inv.quantity === 0) {
        outCount++;
      } else if (prod && inv.quantity < prod.reorder_point) {
        lowCount++;
      } else {
        healthyCount++;
      }
    });

    const inventoryCtx = document.getElementById('inventoryStatusChart')?.getContext('2d');
    if (inventoryCtx) {
      if (charts.inventory) charts.inventory.destroy();
      charts.inventory = new Chart(inventoryCtx, {
        type: 'doughnut',
        data: {
          labels: ['Healthy', 'Low Stock', 'Out of Stock'],
          datasets: [{
            data: [healthyCount, lowCount, outCount],
            backgroundColor: ['#22C55E', '#F59E0B', '#EF4444'],
            borderWidth: 1,
            borderColor: '#1e293b'
          }]
        },
        options: {
          ...chartDefaults,
          plugins: {
            ...chartDefaults.plugins,
            legend: {
              ...chartDefaults.plugins.legend,
              position: 'right'
            }
          }
        }
      });
    }

    // 4. Category Distribution (Pie)
    const categoryCounts = {};
    products.forEach(p => {
      const cat = p.category || 'Uncategorized';
      categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
    });

    const categoryCtx = document.getElementById('categoryChart')?.getContext('2d');
    if (categoryCtx) {
      if (charts.category) charts.category.destroy();
      charts.category = new Chart(categoryCtx, {
        type: 'pie',
        data: {
          labels: Object.keys(categoryCounts),
          datasets: [{
            data: Object.values(categoryCounts),
            backgroundColor: ['#2563EB', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'],
            borderWidth: 1,
            borderColor: '#1e293b'
          }]
        },
        options: {
          ...chartDefaults,
          plugins: {
            ...chartDefaults.plugins,
            legend: {
              ...chartDefaults.plugins.legend,
              position: 'right'
            }
          }
        }
      });
    }

    // 5. Forecast vs Actual (Mixed)
    // Gather forecast entries and match with sales.
    // We will aggregate recent predictions and sales by date
    const forecastDates = {};
    forecasts.slice(0, 10).forEach(f => {
      forecastDates[f.forecast_date] = { pred: f.predicted_qty, actual: 0 };
    });

    sales.forEach(s => {
      const dateStr = s.sale_date.split('T')[0];
      if (forecastDates[dateStr]) {
        forecastDates[dateStr].actual += s.quantity;
      }
    });

    const sortedDates = Object.keys(forecastDates).sort();
    const forecastCtx = document.getElementById('forecastVsActualChart')?.getContext('2d');
    if (forecastCtx && sortedDates.length > 0) {
      if (charts.forecastVsActual) charts.forecastVsActual.destroy();
      charts.forecastVsActual = new Chart(forecastCtx, {
        type: 'bar',
        data: {
          labels: sortedDates.map(d => formatDate(d)),
          datasets: [
            {
              type: 'bar',
              label: 'Actual Sales',
              data: sortedDates.map(d => forecastDates[d].actual),
              backgroundColor: 'rgba(34, 197, 94, 0.7)',
              borderRadius: 4
            },
            {
              type: 'line',
              label: 'Predicted Demand',
              data: sortedDates.map(d => forecastDates[d].pred),
              borderColor: '#f59e0b',
              borderWidth: 2,
              fill: false,
              tension: 0.3
            }
          ]
        },
        options: {
          ...chartDefaults
        }
      });
    } else if (forecastCtx) {
      // Fallback placeholder chart if no forecasts present
      if (charts.forecastVsActual) charts.forecastVsActual.destroy();
      charts.forecastVsActual = new Chart(forecastCtx, {
        type: 'bar',
        data: {
          labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
          datasets: [
            { type: 'bar', label: 'Actual Sales', data: [12, 19, 3, 5, 2], backgroundColor: 'rgba(34, 197, 94, 0.7)' },
            { type: 'line', label: 'Predicted Demand', data: [15, 15, 8, 7, 5], borderColor: '#f59e0b', borderWidth: 2 }
          ]
        },
        options: { ...chartDefaults }
      });
    }

    // 6. Top Products (Horizontal Bar)
    const productSales = {};
    sales.forEach(sale => {
      productSales[sale.product_id] = (productSales[sale.product_id] || 0) + sale.quantity;
    });

    const sortedProds = Object.entries(productSales)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5); // top 5

    const topProdNames = sortedProds.map(item => {
      const p = products.find(prod => prod.product_id === item[0]);
      return p ? p.name : 'Unknown';
    });
    const topProdQtys = sortedProds.map(item => item[1]);

    const topProductsCtx = document.getElementById('topProductsChart')?.getContext('2d');
    if (topProductsCtx && topProdQtys.length > 0) {
      if (charts.topProducts) charts.topProducts.destroy();
      charts.topProducts = new Chart(topProductsCtx, {
        type: 'bar',
        data: {
          labels: topProdNames,
          datasets: [{
            label: 'Quantity Sold',
            data: topProdQtys,
            backgroundColor: '#8b5cf6',
            borderRadius: 4
          }]
        },
        options: {
          ...chartDefaults,
          indexAxis: 'y'
        }
      });
    } else if (topProductsCtx) {
      // Fallback
      if (charts.topProducts) charts.topProducts.destroy();
      charts.topProducts = new Chart(topProductsCtx, {
        type: 'bar',
        data: {
          labels: ['Wireless Mouse', 'Keyboard', 'Webcam', 'Monitor', 'USB Cable'],
          datasets: [{ label: 'Quantity Sold', data: [120, 90, 75, 40, 30], backgroundColor: '#8b5cf6' }]
        },
        options: { ...chartDefaults, indexAxis: 'y' }
      });
    }

  } catch (err) {
    console.error('Failed to render charts:', err);
  }
}

// Global actions triggerable from dashboard
function generateForecast() {
  window.location.href = '/forecasts.html';
}

function addProduct() {
  window.location.href = '/products.html';
}

function newPO() {
  window.location.href = '/purchase-orders.html';
}

function downloadReport() {
  window.location.href = '/reports.html';
}

document.addEventListener('DOMContentLoaded', () => {
  // Only init if dashboard containers exist
  if (document.getElementById('kpi-total-products')) {
    initDashboard();
  }
});
