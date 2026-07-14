// app/public/js/products.js
// Products Page Logic

let allProducts = [];
let currentPage = 1;
const itemsPerPage = 8;

async function loadProducts() {
  showSkeleton('products-table-body', 5);
  try {
    const response = await apiFetch('/products');
    if (response.success && response.data) {
      allProducts = response.data;
      
      // Dynamically populate categories filter dropdown
      populateCategoryFilter();
      
      renderProducts();
    }
  } catch (err) {
    showToast('Failed to load products: ' + err.message, 'danger');
  }
}

function populateCategoryFilter() {
  const categoryFilter = document.getElementById('category-filter');
  if (!categoryFilter) return;
  
  // Keep the first default option
  const defaultOption = categoryFilter.options[0];
  categoryFilter.innerHTML = '';
  categoryFilter.appendChild(defaultOption);

  const categories = [...new Set(allProducts.map(p => p.category).filter(Boolean))];
  categories.sort().forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    categoryFilter.appendChild(opt);
  });
}

function getFilteredProducts() {
  const searchInput = document.getElementById('search-input');
  const categoryFilter = document.getElementById('category-filter');

  const search = searchInput ? searchInput.value.toLowerCase() : '';
  const category = categoryFilter ? categoryFilter.value : '';

  return allProducts.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(search) || p.sku.toLowerCase().includes(search);
    const matchesCategory = category === '' || p.category === category;
    return matchesSearch && matchesCategory;
  });
}

function renderProducts() {
  const tbody = document.getElementById('products-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  const filtered = getFilteredProducts();

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-muted text-center" style="padding: 32px;">No products found</td></tr>`;
    renderPagination(0);
    return;
  }

  // Pagination logic
  const totalItems = filtered.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (currentPage > totalPages) currentPage = Math.max(1, totalPages);

  const startIdx = (currentPage - 1) * itemsPerPage;
  const endIdx = Math.min(startIdx + itemsPerPage, totalItems);
  const pageItems = filtered.slice(startIdx, endIdx);

  pageItems.forEach(p => {
    const tr = document.createElement('tr');
    tr.className = 'animate-fade-in';
    tr.innerHTML = `
      <td><span class="font-semibold text-primary">${p.sku}</span></td>
      <td><span class="text-primary font-medium">${p.name}</span></td>
      <td><span class="badge badge-neutral">${p.category || 'N/A'}</span></td>
      <td>${formatCurrency(p.unit_cost)}</td>
      <td>${formatNumber(p.reorder_point)}</td>
      <td style="white-space: nowrap;">
        <button class="btn btn-secondary btn-sm" onclick="editProduct('${p.product_id}')">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteProduct('${p.product_id}')">Delete</button>
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

  // Simple page buttons
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
      const btn = document.createElement('button');
      btn.textContent = i;
      btn.className = currentPage === i ? 'active' : '';
      btn.onclick = () => { currentPage = i; renderProducts(); };
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
  nextBtn.onclick = () => { currentPage++; renderProducts(); };
  paginationContainer.appendChild(nextBtn);
}

function filterProducts() {
  currentPage = 1;
  renderProducts();
}

function openProductModal(mode, pId = null) {
  const form = document.getElementById('product-form');
  if (!form) return;
  form.reset();

  document.getElementById('edit-product-id').value = '';
  document.getElementById('prod-sku').disabled = false;
  
  const title = document.getElementById('modal-title');

  if (mode === 'add') {
    if (title) title.textContent = 'Add New Product';
  } else {
    if (title) title.textContent = 'Edit Product';
    const p = allProducts.find(prod => prod.product_id === pId);
    if (p) {
      document.getElementById('edit-product-id').value = p.product_id;
      document.getElementById('prod-sku').value = p.sku;
      document.getElementById('prod-sku').disabled = true; // Sku immutable
      document.getElementById('prod-name').value = p.name;
      document.getElementById('prod-category').value = p.category || '';
      document.getElementById('prod-cost').value = p.unit_cost;
      document.getElementById('prod-reorder').value = p.reorder_point;
    }
  }
  openModal('product-modal');
}

function closeProductModal() {
  closeModal('product-modal');
}

async function handleProductFormSubmit(e) {
  e.preventDefault();
  const product_id = document.getElementById('edit-product-id').value;
  const sku = document.getElementById('prod-sku').value.trim();
  const name = document.getElementById('prod-name').value.trim();
  const category = document.getElementById('prod-category').value;
  const unit_cost = parseFloat(document.getElementById('prod-cost').value) || 0;
  const reorder_point = parseInt(document.getElementById('prod-reorder').value, 10) || 0;

  const payload = { sku, name, category, unit_cost, reorder_point };

  try {
    let response;
    if (!product_id) {
      response = await apiFetch('/products', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      if (response.success) {
        showToast('Product added successfully', 'success');
        // Let's create an inventory record for this product with quantity 0
        try {
          await apiFetch('/inventory', {
            method: 'POST',
            body: JSON.stringify({ product_id: response.data.product_id, quantity: 0, location: 'Warehouse-A' })
          });
        } catch (invErr) {
          console.error('Failed to auto-create inventory:', invErr);
        }
      }
    } else {
      response = await apiFetch(`/products/${product_id}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
      if (response.success) {
        showToast('Product updated successfully', 'success');
      }
    }
    
    closeProductModal();
    loadProducts();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function editProduct(pId) {
  openProductModal('edit', pId);
}

async function deleteProduct(pId) {
  if (!confirm('Are you sure you want to delete this product? All related inventory metrics will be affected.')) return;
  try {
    const response = await apiFetch(`/products/${pId}`, { method: 'DELETE' });
    if (response.success) {
      showToast('Product deleted successfully', 'success');
      loadProducts();
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// CSV Export
function exportProductsToCSV() {
  if (allProducts.length === 0) {
    showToast('No products to export', 'warning');
    return;
  }

  const headers = ['Product ID', 'SKU', 'Name', 'Category', 'Unit Cost ($)', 'Reorder Point', 'Created At'];
  const rows = allProducts.map(p => [
    p.product_id,
    p.sku,
    `"${p.name.replace(/"/g, '""')}"`,
    p.category || '',
    p.unit_cost,
    p.reorder_point,
    p.created_at
  ]);

  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'products_export.csv');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Products exported successfully', 'success');
}

// CSV Import
async function importProductsFromCSV(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function (evt) {
    const text = evt.target.result;
    const lines = text.split('\n').map(line => line.trim()).filter(Boolean);
    if (lines.length <= 1) {
      showToast('CSV file is empty', 'warning');
      return;
    }

    // Assume header row exists: sku, name, category, unit_cost, reorder_point
    const headers = lines[0].toLowerCase().split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
    
    let successCount = 0;
    let failCount = 0;

    for (let i = 1; i < lines.length; i++) {
      // Basic CSV parsing split by comma (not supporting nested commas for simplicity in seed files)
      const values = lines[i].split(',').map(v => v.trim().replace(/^["']|["']$/g, ''));
      if (values.length < headers.length) continue;

      const payload = {};
      headers.forEach((h, idx) => {
        if (h.includes('sku')) payload.sku = values[idx];
        else if (h.includes('name')) payload.name = values[idx];
        else if (h.includes('category')) payload.category = values[idx];
        else if (h.includes('cost')) payload.unit_cost = parseFloat(values[idx]) || 0;
        else if (h.includes('reorder')) payload.reorder_point = parseInt(values[idx], 10) || 10;
      });

      if (!payload.sku || !payload.name) {
        failCount++;
        continue;
      }

      try {
        const response = await apiFetch('/products', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        if (response.success) {
          successCount++;
          // auto-initialize empty inventory
          await apiFetch('/inventory', {
            method: 'POST',
            body: JSON.stringify({ product_id: response.data.product_id, quantity: 0, location: 'Warehouse-A' })
          }).catch(err => console.error('Failed auto-inventory creation on CSV import:', err));
        } else {
          failCount++;
        }
      } catch (err) {
        failCount++;
      }
    }

    showToast(`Imported: ${successCount} products. Failed: ${failCount}`, successCount > 0 ? 'success' : 'danger');
    loadProducts();
    // Reset file input
    e.target.value = '';
  };
  reader.readAsText(file);
}

document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('products-table-body');
  if (tbody) {
    loadProducts();
    const form = document.getElementById('product-form');
    if (form) form.addEventListener('submit', handleProductFormSubmit);
    
    const fileInput = document.getElementById('csv-import-input');
    if (fileInput) fileInput.addEventListener('change', importProductsFromCSV);
  }
});
