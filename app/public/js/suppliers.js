// app/public/js/suppliers.js
// Suppliers Page Logic

let allSuppliers = [];
let viewMode = 'grid'; // 'grid' or 'table'

async function loadSuppliers() {
  const container = document.getElementById('suppliers-container');
  if (container) {
    if (viewMode === 'grid') {
      container.innerHTML = '<div class="skeleton skeleton-card" style="height: 200px; grid-column: 1/-1;"></div>';
    } else {
      showSkeleton('suppliers-table-body', 5);
    }
  }

  try {
    const response = await apiFetch('/suppliers');
    if (response.success && response.data) {
      allSuppliers = response.data;
      renderSuppliers();
    }
  } catch (err) {
    showToast('Failed to load suppliers: ' + err.message, 'danger');
  }
}

function renderSuppliers() {
  const gridContainer = document.getElementById('suppliers-grid');
  const tableCard = document.getElementById('suppliers-table-card');
  const tbody = document.getElementById('suppliers-table-body');
  
  if (viewMode === 'grid') {
    if (tableCard) tableCard.classList.add('hidden');
    if (gridContainer) {
      gridContainer.classList.remove('hidden');
      gridContainer.innerHTML = '';
      
      if (allSuppliers.length === 0) {
        gridContainer.innerHTML = `
          <div class="empty-state" style="grid-column: 1/-1;">
            <div class="empty-icon">🚚</div>
            <h3>No Suppliers Directory</h3>
            <p>Add a new supplier to start tracking profiles and performance.</p>
          </div>
        `;
        return;
      }
      
      allSuppliers.forEach(s => {
        const ratingVal = s.rating || 0;
        const ratingHtml = renderStars(ratingVal);
        
        const card = document.createElement('div');
        card.className = 'supplier-card animate-fade-in-up';
        card.innerHTML = `
          <div class="supplier-card-header">
            <div>
              <h3 class="text-primary">${s.name}</h3>
              <span class="supplier-email">${s.contact_email || 'No email contact'}</span>
            </div>
            <div class="supplier-card-actions">
              <button class="btn btn-secondary btn-icon" onclick="editSupplier('${s.supplier_id}')" title="Edit">✏️</button>
              <button class="btn btn-danger btn-icon" onclick="deleteSupplier('${s.supplier_id}')" title="Delete">🗑️</button>
            </div>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 12px;">
            <div><strong>Contact:</strong> ${s.contact_person || 'N/A'}</div>
            <div><strong>Phone:</strong> ${s.contact_phone || 'N/A'}</div>
          </div>
          <div class="supplier-meta">
            <div class="supplier-meta-item">
              <span class="meta-label">Lead Time</span>
              <span class="meta-value">${s.lead_time_days} days</span>
            </div>
            <div class="supplier-meta-item">
              <span class="meta-label">Rating</span>
              <span class="meta-value">${ratingHtml}</span>
            </div>
          </div>
        `;
        gridContainer.appendChild(card);
      });
    }
  } else {
    if (gridContainer) gridContainer.classList.add('hidden');
    if (tableCard) {
      tableCard.classList.remove('hidden');
      if (tbody) {
        tbody.innerHTML = '';
        if (allSuppliers.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" class="text-muted text-center" style="padding: 32px;">No suppliers cataloged</td></tr>`;
          return;
        }
        allSuppliers.forEach(s => {
          const ratingVal = s.rating || 0;
          const ratingHtml = renderStars(ratingVal);
          
          const tr = document.createElement('tr');
          tr.className = 'animate-fade-in';
          tr.innerHTML = `
            <td><span class="font-semibold text-primary">${s.name}</span></td>
            <td>${s.contact_person || 'N/A'}</td>
            <td>${s.contact_email || 'N/A'}</td>
            <td>${s.contact_phone || 'N/A'}</td>
            <td><span class="font-semibold">${s.lead_time_days} days</span></td>
            <td>${ratingHtml}</td>
            <td style="white-space: nowrap;">
              <button class="btn btn-secondary btn-sm" onclick="editSupplier('${s.supplier_id}')">Edit</button>
              <button class="btn btn-danger btn-sm" onclick="deleteSupplier('${s.supplier_id}')">Delete</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }
    }
  }
}

function toggleView(mode) {
  viewMode = mode;
  document.getElementById('btn-view-grid')?.classList.toggle('active', mode === 'grid');
  document.getElementById('btn-view-table')?.classList.toggle('active', mode === 'table');
  renderSuppliers();
}

function openSupplierModal(mode, sId = null) {
  const form = document.getElementById('supplier-form');
  if (form) form.reset();

  document.getElementById('edit-supplier-id').value = '';
  const title = document.getElementById('modal-title');

  if (mode === 'add') {
    if (title) title.textContent = 'Add Supplier Profile';
  } else {
    if (title) title.textContent = 'Edit Supplier Profile';
    const s = allSuppliers.find(sup => sup.supplier_id === sId);
    if (s) {
      document.getElementById('edit-supplier-id').value = s.supplier_id;
      document.getElementById('sup-name').value = s.name;
      document.getElementById('sup-contact').value = s.contact_person || '';
      document.getElementById('sup-email').value = s.contact_email || '';
      document.getElementById('sup-phone').value = s.contact_phone || '';
      document.getElementById('sup-lead').value = s.lead_time_days;
      document.getElementById('sup-rating').value = s.rating || '';
    }
  }
  openModal('supplier-modal');
}

function closeSupplierModal() {
  closeModal('supplier-modal');
}

async function handleSupplierFormSubmit(e) {
  e.preventDefault();
  
  const sId = document.getElementById('edit-supplier-id').value;
  const name = document.getElementById('sup-name').value.trim();
  const contact_person = document.getElementById('sup-contact').value.trim() || null;
  const contact_email = document.getElementById('sup-email').value.trim() || null;
  const contact_phone = document.getElementById('sup-phone').value.trim() || null;
  const lead_time_days = parseInt(document.getElementById('sup-lead').value, 10) || 5;
  const ratingStr = document.getElementById('sup-rating').value;
  const rating = ratingStr ? parseFloat(ratingStr) : null;

  const payload = { name, contact_person, contact_email, contact_phone, lead_time_days, rating };

  try {
    let response;
    if (!sId) {
      response = await apiFetch('/suppliers', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      if (response.success) {
        showToast('Supplier profile created', 'success');
      }
    } else {
      response = await apiFetch(`/suppliers/${sId}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
      if (response.success) {
        showToast('Supplier profile updated', 'success');
      }
    }
    
    closeSupplierModal();
    loadSuppliers();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

function editSupplier(sId) {
  openSupplierModal('edit', sId);
}

async function deleteSupplier(sId) {
  if (!confirm('Are you sure you want to delete this supplier profile?')) return;
  try {
    const response = await apiFetch(`/suppliers/${sId}`, { method: 'DELETE' });
    if (response.success) {
      showToast('Supplier profile deleted', 'success');
      loadSuppliers();
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('suppliers-container');
  if (container) {
    loadSuppliers();
    const form = document.getElementById('supplier-form');
    if (form) form.addEventListener('submit', handleSupplierFormSubmit);
    
    // Wire toggle buttons
    const btnGrid = document.getElementById('btn-view-grid');
    const btnTable = document.getElementById('btn-view-table');
    if (btnGrid) btnGrid.addEventListener('click', () => toggleView('grid'));
    if (btnTable) btnTable.addEventListener('click', () => toggleView('table'));
  }
});
