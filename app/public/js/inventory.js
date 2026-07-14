// app/public/js/inventory.js
// Inventory Page Logic

let allInventory = [];
let currentPage = 1;
const itemsPerPage = 8;

async function loadInventory() {
  showSkeleton('inventory-table-body', 5);
  try {
    const productsRes = await apiFetch('/products');
    const inventoryRes = await apiFetch('/inventory');
    
    if (productsRes.success && inventoryRes.success) {
      const products = productsRes.data;
      const inventory = inventoryRes.data;

      // Join inventory with product details
      allInventory = inventory.map(item => {
        const prod = products.find(p => p.product_id === item.product_id);
        const unit_cost = prod ? prod.unit_cost : 0;
        const reorder_point = prod ? prod.reorder_point : 10;
        
        // Premium indicator computations
        const reservedStock = Math.floor(item.quantity * 0.1); // mock 10% reserved
        const availableStock = item.quantity - reservedStock;
        const safetyStock = reorder_point;
        const inventoryValue = item.quantity * unit_cost;

        return {
          ...item,
          sku: prod ? prod.sku : 'N/A',
          name: prod ? prod.name : 'Unknown',
          category: prod ? prod.category : 'General',
          unit_cost,
          reorder_point,
          reservedStock,
          availableStock,
          safetyStock,
          inventoryValue
        };
      });

      // Update KPI widgets
      updateKPIWidgets();

      renderInventory();
    }
  } catch (err) {
    showToast('Failed to load inventory: ' + err.message, 'danger');
  }
}

function updateKPIWidgets() {
  const totalItems = allInventory.reduce((acc, item) => acc + item.quantity, 0);
  const totalValue = allInventory.reduce((acc, item) => acc + item.inventoryValue, 0);
  const lowStockCount = allInventory.filter(item => item.quantity < item.reorder_point).length;
  const healthyStockCount = allInventory.filter(item => item.quantity >= item.reorder_point).length;

  const totalItemsEl = document.getElementById('kpi-inv-total-items');
  const totalValueEl = document.getElementById('kpi-inv-total-value');
  const lowStockEl = document.getElementById('kpi-inv-low-stock');
  const healthyStockEl = document.getElementById('kpi-inv-healthy');

  if (totalItemsEl) totalItemsEl.textContent = formatNumber(totalItems);
  if (totalValueEl) totalValueEl.textContent = formatCurrency(totalValue);
  if (lowStockEl) lowStockEl.textContent = formatNumber(lowStockCount);
  if (healthyStockEl) healthyStockEl.textContent = formatNumber(healthyStockCount);
}

function getFilteredInventory() {
  const searchInput = document.getElementById('search-input');
  const statusFilter = document.getElementById('status-filter');

  const search = searchInput ? searchInput.value.toLowerCase() : '';
  const status = statusFilter ? statusFilter.value : '';

  return allInventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(search) || 
                          item.sku.toLowerCase().includes(search) || 
                          item.location.toLowerCase().includes(search);
    
    let matchesStatus = true;
    if (status === 'healthy') {
      matchesStatus = item.quantity >= item.reorder_point;
    } else if (status === 'low') {
      matchesStatus = item.quantity > 0 && item.quantity < item.reorder_point;
    } else if (status === 'stockout') {
      matchesStatus = item.quantity === 0;
    }

    return matchesSearch && matchesStatus;
  });
}

function renderInventory() {
  const tbody = document.getElementById('inventory-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  const filtered = getFilteredInventory();

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-muted text-center" style="padding: 32px;">No inventory records found</td></tr>`;
    renderPagination(0);
    return;
  }

  const totalItems = filtered.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (currentPage > totalPages) currentPage = Math.max(1, totalPages);

  const startIdx = (currentPage - 1) * itemsPerPage;
  const endIdx = Math.min(startIdx + itemsPerPage, totalItems);
  const pageItems = filtered.slice(startIdx, endIdx);

  pageItems.forEach(item => {
    let badgeClass = 'badge-success';
    let statusLabel = 'Healthy';
    
    if (item.quantity === 0) {
      badgeClass = 'badge-danger';
      statusLabel = 'Out of Stock';
    } else if (item.quantity < item.reorder_point) {
      badgeClass = 'badge-warning';
      statusLabel = 'Low Stock';
    }

    const tr = document.createElement('tr');
    tr.className = 'animate-fade-in';
    tr.innerHTML = `
      <td><span class="font-semibold text-primary">${item.sku}</span></td>
      <td><span class="text-primary font-medium">${item.name}</span></td>
      <td><span class="badge badge-neutral">${item.location}</span></td>
      <td><span class="font-semibold">${formatNumber(item.quantity)}</span></td>
      <td>${formatNumber(item.reservedStock)}</td>
      <td>${formatNumber(item.availableStock)}</td>
      <td>${formatNumber(item.safetyStock)}</td>
      <td><span class="font-semibold text-success">${formatCurrency(item.inventoryValue)}</span></td>
      <td><span class="badge ${badgeClass}">${statusLabel}</span></td>
      <td>
        <button class="btn btn-primary btn-sm" onclick="adjustStock('${item.inventory_id}')">Adjust</button>
      </td>
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
  prevBtn.onclick = () => { currentPage--; renderProducts(); };
  paginationContainer.appendChild(prevBtn);

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = currentPage === i ? 'active' : '';
      btn.onclick = () => { currentPage = i; renderInventory(); };
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
  nextBtn.onclick = () => { currentPage++; renderInventory(); };
  paginationContainer.appendChild(nextBtn);
}

function filterInventory() {
  currentPage = 1;
  renderInventory();
}

function adjustStock(invId) {
  const form = document.getElementById('adjustment-form');
  if (!form) return;
  form.reset();

  const item = allInventory.find(i => i.inventory_id === invId);
  if (item) {
    document.getElementById('adjust-inventory-id').value = item.inventory_id;
    document.getElementById('adjust-prod-name').value = `${item.sku} - ${item.name}`;
    document.getElementById('adjust-qty').value = item.quantity;
    document.getElementById('adjust-location').value = item.location;
    openModal('adjustment-modal');
  }
}

function closeAdjustmentModal() {
  closeModal('adjustment-modal');
}

async function handleAdjustmentSubmit(e) {
  e.preventDefault();
  
  const invId = document.getElementById('adjust-inventory-id').value;
  const quantity = parseInt(document.getElementById('adjust-qty').value, 10) || 0;
  const location = document.getElementById('adjust-location').value.trim();
  const reason = document.getElementById('adjust-reason').value.trim();

  try {
    const response = await apiFetch(`/inventory/${invId}`, {
      method: 'PUT',
      body: JSON.stringify({ quantity, location, reason })
    });

    if (response.success) {
      showToast('Inventory updated successfully', 'success');
      closeAdjustmentModal();
      loadInventory();
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('inventory-table-body');
  if (tbody) {
    loadInventory();
    const form = document.getElementById('adjustment-form');
    if (form) form.addEventListener('submit', handleAdjustmentSubmit);
  }
});
