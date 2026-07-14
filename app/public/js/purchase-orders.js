// app/public/js/purchase-orders.js
// Purchase Orders Page Logic

let allPOs = [];
let allSuppliers = [];
let allProducts = [];
let selectedStatusFilter = ''; // Empty means 'All'

async function loadPOPage() {
  showSkeleton('po-table-body', 5);
  try {
    const supResponse = await apiFetch('/suppliers');
    const prodResponse = await apiFetch('/products');
    const poResponse = await apiFetch('/purchase-orders');

    if (supResponse.success && prodResponse.success && poResponse.success) {
      allSuppliers = supResponse.data;
      allProducts = prodResponse.data;
      allPOs = poResponse.data;

      // Newest first
      allPOs.sort((a, b) => new Date(b.order_date) - new Date(a.order_date));

      updatePOSummary();
      renderPOs();
      populateDropdowns();
    }
  } catch (err) {
    showToast('Failed to load page data: ' + err.message, 'danger');
  }
}

function updatePOSummary() {
  const pending = allPOs.filter(po => po.status === 'Pending').length;
  const sent = allPOs.filter(po => po.status === 'Sent').length;
  const received = allPOs.filter(po => po.status === 'Received').length;
  const cancelled = allPOs.filter(po => po.status === 'Cancelled').length;

  const countPending = document.getElementById('count-po-pending');
  const countSent = document.getElementById('count-po-sent');
  const countReceived = document.getElementById('count-po-received');
  const countCancelled = document.getElementById('count-po-cancelled');

  if (countPending) countPending.textContent = pending;
  if (countSent) countSent.textContent = sent;
  if (countReceived) countReceived.textContent = received;
  if (countCancelled) countCancelled.textContent = cancelled;
}

function selectStatusFilter(status) {
  selectedStatusFilter = status;
  
  // Highlight active card
  document.querySelectorAll('.po-status-card').forEach(card => {
    card.classList.toggle('selected', card.getAttribute('data-status') === status);
  });
  
  renderPOs();
}

function getFilteredPOs() {
  return allPOs.filter(po => {
    return selectedStatusFilter === '' || po.status === selectedStatusFilter;
  });
}

function renderPOs() {
  const tbody = document.getElementById('po-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  const filtered = getFilteredPOs();

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-muted text-center" style="padding: 32px;">No purchase orders found</td></tr>`;
    return;
  }

  filtered.forEach(po => {
    let statusClass = 'badge-primary';
    let timelineClass = 'pending';
    
    if (po.status === 'Pending') {
      statusClass = 'badge-warning';
      timelineClass = 'pending';
    } else if (po.status === 'Sent') {
      statusClass = 'badge-info';
      timelineClass = 'sent';
    } else if (po.status === 'Received') {
      statusClass = 'badge-success';
      timelineClass = 'received';
    } else if (po.status === 'Cancelled') {
      statusClass = 'badge-danger';
      timelineClass = 'cancelled';
    }

    let actionsHtml = '';
    if (po.status === 'Pending') {
      actionsHtml = `
        <button class="btn btn-primary btn-sm" onclick="updatePOStatus('${po.po_id}', 'Sent')">Send</button>
        <button class="btn btn-danger btn-sm" onclick="updatePOStatus('${po.po_id}', 'Cancelled')">Cancel</button>
      `;
    } else if (po.status === 'Sent') {
      actionsHtml = `
        <button class="btn btn-success btn-sm" onclick="updatePOStatus('${po.po_id}', 'Received')">Receive</button>
        <button class="btn btn-danger btn-sm" onclick="updatePOStatus('${po.po_id}', 'Cancelled')">Cancel</button>
      `;
    } else {
      actionsHtml = `<span class="text-muted" style="font-size: 0.8rem;">Completed</span>`;
    }

    const tr = document.createElement('tr');
    tr.className = 'animate-fade-in';
    tr.innerHTML = `
      <td>${formatDate(po.order_date)}</td>
      <td><span class="font-semibold text-primary">${po.supplier_name || 'Supplier'}</span></td>
      <td><span class="font-semibold">${po.sku || 'N/A'}</span></td>
      <td><span class="text-primary font-medium">${po.product_name || 'Unknown'}</span></td>
      <td>${formatNumber(po.quantity)} pcs</td>
      <td>${formatCurrency(po.unit_cost)}</td>
      <td>${formatDate(po.expected_delivery)}</td>
      <td><span class="timeline-badge ${timelineClass}">${po.status}</span></td>
      <td style="white-space: nowrap;">${actionsHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

function populateDropdowns() {
  const supSelect = document.getElementById('po-supplier-id');
  if (supSelect) {
    supSelect.innerHTML = '<option value="">-- Choose Supplier --</option>';
    allSuppliers.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.supplier_id;
      opt.textContent = s.name;
      supSelect.appendChild(opt);
    });
  }

  const prodSelect = document.getElementById('po-product-id');
  if (prodSelect) {
    prodSelect.innerHTML = '<option value="">-- Choose Product --</option>';
    allProducts.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.product_id;
      opt.textContent = `${p.sku} - ${p.name}`;
      prodSelect.appendChild(opt);
    });
  }
}

function handleProductChange() {
  const pId = document.getElementById('po-product-id').value;
  const helper = document.getElementById('po-cost-helper');
  const costInput = document.getElementById('po-cost');

  if (!pId) {
    if (helper) helper.textContent = '';
    return;
  }

  const prod = allProducts.find(p => p.product_id === pId);
  if (prod) {
    if (helper) helper.textContent = `Catalog unit cost: ${formatCurrency(prod.unit_cost)}`;
    if (costInput && !costInput.value) {
      costInput.value = prod.unit_cost.toFixed(2);
    }
  }
}

function openPOModal() {
  const form = document.getElementById('po-form');
  if (form) form.reset();
  
  const helper = document.getElementById('po-cost-helper');
  if (helper) helper.textContent = '';

  // Default expected delivery date: 7 days from today
  const deliveryDate = new Date();
  deliveryDate.setDate(deliveryDate.getDate() + 7);
  const expectedInput = document.getElementById('po-expected');
  if (expectedInput) expectedInput.value = deliveryDate.toISOString().split('T')[0];

  openModal('po-modal');
}

function closePOModal() {
  closeModal('po-modal');
}

async function handlePOFormSubmit(e) {
  e.preventDefault();
  
  const supplier_id = document.getElementById('po-supplier-id').value;
  const product_id = document.getElementById('po-product-id').value;
  const quantity = parseInt(document.getElementById('po-qty').value, 10) || 0;
  const unit_cost = parseFloat(document.getElementById('po-cost').value) || 0;
  const expected_delivery = document.getElementById('po-expected').value;
  const notes = document.getElementById('po-notes')?.value || '';

  const payload = { supplier_id, product_id, quantity, unit_cost, expected_delivery, notes };

  try {
    const response = await apiFetch('/purchase-orders', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (response.success) {
      showToast('Purchase order created successfully', 'success');
      closePOModal();
      loadPOPage();
    }
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

async function updatePOStatus(poId, status) {
  let confirmMsg = `Are you sure you want to mark this PO as ${status}?`;
  if (status === 'Received') {
    confirmMsg = `Mark this purchase order as Received? This will automatically add ${formatNumber(allPOs.find(p => p.po_id === poId)?.quantity || 0)} units to the warehouse inventory.`;
  }
  
  if (!confirm(confirmMsg)) return;

  const todayStr = new Date().toISOString().split('T')[0];
  const payload = {
    status,
    actual_delivery: status === 'Received' ? todayStr : null
  };

  try {
    const response = await apiFetch(`/purchase-orders/${poId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });

    if (response.success) {
      showToast(`Purchase order updated to ${status}`, 'success');
      loadPOPage();
    }
  } catch (err) {
    showToast('Failed to update PO status: ' + err.message, 'danger');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('po-table-body');
  if (tbody) {
    loadPOPage();
    
    const form = document.getElementById('po-form');
    if (form) form.addEventListener('submit', handlePOFormSubmit);

    // Status summary cards click handlers
    document.querySelectorAll('.po-status-card').forEach(card => {
      card.addEventListener('click', () => {
        const status = card.getAttribute('data-status');
        selectStatusFilter(status);
      });
    });
  }
});
