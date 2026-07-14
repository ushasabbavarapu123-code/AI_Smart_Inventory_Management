// app/public/js/sales.js
// Sales Page Logic

let allSales = [];
let allProducts = [];
let currentPage = 1;
const itemsPerPage = 10;
let salesChart = null;

async function loadSalesPage() {
  showSkeleton('sales-table-body', 5);
  try {
    const prodResponse = await apiFetch('/products');
    const salesResponse = await apiFetch('/sales');
    
    if (prodResponse.success && salesResponse.success) {
      allProducts = prodResponse.data;
      allSales = salesResponse.data;
      
      // Chronological sort (newest first)
      allSales.sort((a, b) => new Date(b.sale_date) - new Date(a.sale_date));

      updateSalesKPIs();
      renderSalesTable();
      populateProductsDropdown();
      renderSalesChart();
    }
  } catch (err) {
    showToast('Failed to load sales data: ' + err.message, 'danger');
  }
}

function updateSalesKPIs() {
  const totalSalesVal = allSales.reduce((acc, s) => acc + (s.quantity * s.unit_price), 0);
  const totalQty = allSales.reduce((acc, s) => acc + s.quantity, 0);
  const transactionCount = allSales.length;
  
  // Calculate average order value (AOV)
  const aov = transactionCount > 0 ? (totalSalesVal / transactionCount) : 0;

  const totalSalesEl = document.getElementById('kpi-sales-total');
  const totalQtyEl = document.getElementById('kpi-sales-qty');
  const countEl = document.getElementById('kpi-sales-count');
  const aovEl = document.getElementById('kpi-sales-aov');

  if (totalSalesEl) totalSalesEl.textContent = formatCurrency(totalSalesVal);
  if (totalQtyEl) totalQtyEl.textContent = formatNumber(totalQty);
  if (countEl) countEl.textContent = formatNumber(transactionCount);
  if (aovEl) aovEl.textContent = formatCurrency(aov);
}

function getFilteredSales() {
  const searchInput = document.getElementById('search-input');
  const customerFilter = document.getElementById('customer-filter');
  const startDateInput = document.getElementById('start-date-filter');
  const endDateInput = document.getElementById('end-date-filter');

  const search = searchInput ? searchInput.value.toLowerCase() : '';
  const customer = customerFilter ? customerFilter.value : '';
  const start = startDateInput ? startDateInput.value : '';
  const end = endDateInput ? endDateInput.value : '';

  return allSales.filter(s => {
    const prod = allProducts.find(p => p.product_id === s.product_id);
    const sku = prod ? prod.sku : '';
    const name = prod ? prod.name : '';

    const matchesSearch = name.toLowerCase().includes(search) || sku.toLowerCase().includes(search);
    const matchesCustomer = customer === '' || s.customer_type === customer;
    
    let matchesDate = true;
    if (start) {
      matchesDate = matchesDate && s.sale_date >= start;
    }
    if (end) {
      matchesDate = matchesDate && s.sale_date <= end;
    }

    return matchesSearch && matchesCustomer && matchesDate;
  });
}

function renderSalesTable() {
  const tbody = document.getElementById('sales-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  const filtered = getFilteredSales();

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-muted text-center" style="padding: 32px;">No sales transactions found</td></tr>`;
    renderPagination(0);
    return;
  }

  const totalItems = filtered.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (currentPage > totalPages) currentPage = Math.max(1, totalPages);

  const startIdx = (currentPage - 1) * itemsPerPage;
  const endIdx = Math.min(startIdx + itemsPerPage, totalItems);
  const pageItems = filtered.slice(startIdx, endIdx);

  pageItems.forEach(s => {
    const prod = allProducts.find(p => p.product_id === s.product_id);
    const sku = prod ? prod.sku : 'N/A';
    const name = prod ? prod.name : 'Unknown';
    const totalVal = s.quantity * s.unit_price;

    const tr = document.createElement('tr');
    tr.className = 'animate-fade-in';
    tr.innerHTML = `
      <td>${formatDate(s.sale_date)}</td>
      <td><span class="font-semibold text-primary">${sku}</span></td>
      <td><span class="text-primary font-medium">${name}</span></td>
      <td>${formatNumber(s.quantity)}</td>
      <td>${formatCurrency(s.unit_price)}</td>
      <td><span class="badge ${s.customer_type === 'Wholesale' ? 'badge-primary' : 'badge-info'}">${s.customer_type}</span></td>
      <td><span class="font-semibold text-success">${formatCurrency(totalVal)}</span></td>
    `;
    tbody.appendChild(tr);
  });

  renderPagination(totalItems);
}

function renderPagination(totalItems) {
  const paginationContainer = document.getElementById('pagination-container');
  if (!paginationContainer) return;
  paginationContainer.innerHTML = '';

  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (totalPages <= 1) return;

  const prevBtn = document.createElement('button');
  prevBtn.textContent = '←';
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = () => { currentPage--; renderSalesTable(); };
  paginationContainer.appendChild(prevBtn);

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = currentPage === i ? 'active' : '';
      btn.onclick = () => { currentPage = i; renderSalesTable(); };
      paginationContainer.appendChild(btn);
    } else if (i === currentPage - 2 || i === currentPage + 2) {
      const dots = document.createElement('span');
      dots.textContent = '...';
      dots.className = 'page-info';
      paginationContainer.appendChild(dots);
    }
  }

  const nextBtn = document.createElement('button');
  nextBtn.textContent = '→';
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => { currentPage++; renderSalesTable(); };
  paginationContainer.appendChild(nextBtn);
}

function filterSales() {
  currentPage = 1;
  renderSalesTable();
  renderSalesChart();
}

function populateProductsDropdown() {
  const select = document.getElementById('sale-product-id');
  if (!select) return;
  select.innerHTML = '<option value="">-- Choose a product --</option>';
  allProducts.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.product_id;
    opt.textContent = `${p.sku} - ${p.name}`;
    select.appendChild(opt);
  });
}

function handleProductChange() {
  const pId = document.getElementById('sale-product-id').value;
  const helper = document.getElementById('sale-cost-helper');
  const priceInput = document.getElementById('sale-price');

  if (!pId) {
    if (helper) helper.textContent = '';
    return;
  }

  const prod = allProducts.find(p => p.product_id === pId);
  if (prod) {
    if (helper) helper.textContent = `Catalog unit cost: ${formatCurrency(prod.unit_cost)}`;
    if (priceInput && !priceInput.value) {
      priceInput.value = (prod.unit_cost * 1.4).toFixed(2); // Recommend 40% markup
    }
  }
}

function openSaleModal() {
  const form = document.getElementById('sale-form');
  if (form) form.reset();
  
  const helper = document.getElementById('sale-cost-helper');
  if (helper) helper.textContent = '';

  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('sale-date');
  if (dateInput) dateInput.value = today;

  openModal('sale-modal');
}

function closeSaleModal() {
  closeModal('sale-modal');
}

async function handleSaleFormSubmit(e) {
  e.preventDefault();
  
  const product_id = document.getElementById('sale-product-id').value;
  const quantity = parseInt(document.getElementById('sale-qty').value, 10) || 0;
  const unit_price = parseFloat(document.getElementById('sale-price').value) || 0;
  const sale_date = document.getElementById('sale-date').value;
  const customer_type = document.getElementById('sale-cust-type').value;

  const payload = { product_id, quantity, unit_price, sale_date, customer_type };

  try {
    const response = await apiFetch('/sales', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (response.success) {
      showToast('Sale recorded successfully', 'success');
      closeSaleModal();
      loadSalesPage();
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function renderSalesChart() {
  const filtered = getFilteredSales();
  const salesByDate = {};
  
  // Aggregate sales by date (last 10 transactions dates)
  filtered.slice(0, 15).forEach(s => {
    const d = s.sale_date.split('T')[0];
    salesByDate[d] = (salesByDate[d] || 0) + (s.quantity * s.unit_price);
  });

  const sortedDates = Object.keys(salesByDate).sort();
  const chartCtx = document.getElementById('salesRevenueChart')?.getContext('2d');
  
  if (chartCtx) {
    if (salesChart) salesChart.destroy();
    salesChart = new Chart(chartCtx, {
      type: 'line',
      data: {
        labels: sortedDates.map(d => formatDate(d)),
        datasets: [{
          label: 'Revenue ($)',
          data: sortedDates.map(d => salesByDate[d]),
          borderColor: '#22C55E',
          backgroundColor: 'rgba(34,197,94,0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: getChartDefaults()
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('sales-table-body');
  if (tbody) {
    loadSalesPage();
    const form = document.getElementById('sale-form');
    if (form) form.addEventListener('submit', handleSaleFormSubmit);
  }
});
