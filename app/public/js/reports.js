// app/public/js/reports.js
// Reports & Documentation Page Logic

let currentReportData = null;
let currentReportType = '';

async function loadDocumentation(fileName) {
  const viewer = document.getElementById('report-viewer');
  if (!viewer) return;
  
  viewer.innerHTML = '<div class="text-muted text-center" style="padding-top: 100px;">Loading file contents...</div>';

  try {
    const response = await fetch(`/docs/${fileName}`);
    if (!response.ok) {
      throw new Error(`Failed to retrieve file (${response.status})`);
    }
    const text = await response.text();
    viewer.innerHTML = `
      <h2 style="margin-top: 0; margin-bottom: 24px; border-bottom: 2px solid var(--border-color); padding-bottom: 12px; font-size: 1.3rem;">
        📄 Documentation: ${fileName}
      </h2>
      <div style="font-size: 0.88rem;" class="animate-fade-in">
        ${parseMarkdown(text)}
      </div>
    `;
  } catch (err) {
    viewer.innerHTML = `
      <div class="alert alert-danger">
        <h4>Failed to load file</h4>
        <p>${err.message}</p>
      </div>
    `;
  }
}

// Simple regex markdown-to-HTML parser
function parseMarkdown(mdText) {
  let html = mdText
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^\s*-\s*(.*$)/gim, '<li>$1</li>')
    .replace(/^\s*\*\s*(.*$)/gim, '<li>$1</li>')
    .replace(/\n\s*\n/g, '</p><p>')
    .replace(/`(.*?)`/g, '<code style="background-color: var(--bg-primary); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>');
    
  return '<p>' + html + '</p>';
}

// ── Report Generation ──
async function generateReport(type) {
  currentReportType = type;
  const viewer = document.getElementById('report-viewer');
  if (!viewer) return;

  viewer.innerHTML = '<div class="text-muted text-center" style="padding-top: 100px;">Aggregating and generating report data...</div>';

  try {
    let response;
    let productsResponse = await apiFetch('/products');
    let products = productsResponse.success ? productsResponse.data : [];

    if (type === 'Inventory') {
      response = await apiFetch('/inventory');
      if (response.success) {
        currentReportData = response.data.map(item => {
          const prod = products.find(p => p.product_id === item.product_id);
          return {
            SKU: prod ? prod.sku : 'N/A',
            Product: prod ? prod.name : 'Unknown',
            Location: item.location,
            Quantity: item.quantity,
            'Reorder Point': prod ? prod.reorder_point : 10,
            Status: item.quantity === 0 ? 'Stockout' : (item.quantity < (prod ? prod.reorder_point : 10) ? 'Low' : 'Healthy')
          };
        });
        renderReportPreview('Inventory Balance Report', ['SKU', 'Product', 'Location', 'Quantity', 'Reorder Point', 'Status']);
      }
    } else if (type === 'Sales') {
      response = await apiFetch('/sales');
      if (response.success) {
        currentReportData = response.data.map(s => {
          const prod = products.find(p => p.product_id === s.product_id);
          return {
            Date: s.sale_date.split('T')[0],
            SKU: prod ? prod.sku : 'N/A',
            Product: prod ? prod.name : 'Unknown',
            Quantity: s.quantity,
            'Unit Price': formatCurrency(s.unit_price),
            Total: formatCurrency(s.quantity * s.unit_price),
            'Customer Type': s.customer_type
          };
        });
        renderReportPreview('Sales Performance Report', ['Date', 'SKU', 'Product', 'Quantity', 'Unit Price', 'Total', 'Customer Type']);
      }
    } else if (type === 'Forecast') {
      response = await apiFetch('/forecasts');
      if (response.success) {
        currentReportData = response.data.map(f => {
          const prod = products.find(p => p.product_id === f.product_id);
          return {
            SKU: prod ? prod.sku : 'N/A',
            Product: prod ? prod.name : 'Unknown',
            'Forecast Date': f.forecast_date,
            'Predicted Qty': f.predicted_qty,
            'Confidence Range': `[${f.confidence_low} - ${f.confidence_high}]`,
            Model: f.model_used
          };
        });
        renderReportPreview('Demand Forecast Metrics Report', ['SKU', 'Product', 'Forecast Date', 'Predicted Qty', 'Confidence Range', 'Model']);
      }
    } else if (type === 'Supplier') {
      response = await apiFetch('/suppliers');
      if (response.success) {
        currentReportData = response.data.map(s => ({
          Name: s.name,
          Contact: s.contact_person || 'N/A',
          Email: s.contact_email || 'N/A',
          Phone: s.contact_phone || 'N/A',
          'Lead Time': `${s.lead_time_days} days`,
          Rating: s.rating ? s.rating.toFixed(1) + ' ★' : 'N/A'
        }));
        renderReportPreview('Supplier Lead Time & Rating Report', ['Name', 'Contact', 'Email', 'Phone', 'Lead Time', 'Rating']);
      }
    }
  } catch (err) {
    viewer.innerHTML = `
      <div class="alert alert-danger">
        <h4>Failed to generate report</h4>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function renderReportPreview(title, headers) {
  const viewer = document.getElementById('report-viewer');
  if (!viewer || !currentReportData || currentReportData.length === 0) return;

  const rowsHtml = currentReportData.map(row => {
    return `<tr>${headers.map(h => `<td>${row[h] !== undefined ? row[h] : '—'}</td>`).join('')}</tr>`;
  }).join('');

  viewer.innerHTML = `
    <div class="d-flex justify-between align-center mb-md" style="border-bottom: 2px solid var(--border-color); padding-bottom: 12px;">
      <h2 style="margin: 0; font-size: 1.3rem;">📊 Generated: ${title}</h2>
      <div class="d-flex gap-sm">
        <button class="btn btn-primary btn-sm" onclick="exportToPDF()">Export PDF</button>
        <button class="btn btn-success btn-sm" onclick="exportToExcel()">Export Excel</button>
        <button class="btn btn-outline btn-sm" onclick="exportToCSV()">Export CSV</button>
      </div>
    </div>
    <div class="table-wrapper animate-fade-in">
      <table class="report-table">
        <thead>
          <tr>
            ${headers.map(h => `<th>${h}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
    </div>
  `;
}

// ── Export Utilities ──
function exportToCSV() {
  if (!currentReportData || currentReportData.length === 0) {
    showToast('No report data to export', 'warning');
    return;
  }

  const headers = Object.keys(currentReportData[0]);
  const csvContent = [
    headers.join(','),
    ...currentReportData.map(row => 
      headers.map(h => {
        const val = String(row[h] || '').replace(/"/g, '""');
        return val.includes(',') ? `"${val}"` : val;
      }).join(',')
    )
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${currentReportType.toLowerCase()}_report.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast('Report exported to CSV', 'success');
}

function exportToExcel() {
  if (!currentReportData || currentReportData.length === 0) {
    showToast('No report data to export', 'warning');
    return;
  }

  if (typeof XLSX === 'undefined') {
    showToast('SheetJS Excel library is loading, please try again in a moment...', 'info');
    return;
  }

  const worksheet = XLSX.utils.json_to_sheet(currentReportData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Report');
  XLSX.writeFile(workbook, `${currentReportType.toLowerCase()}_report.xlsx`);
  showToast('Report exported to Excel', 'success');
}

function exportToPDF() {
  if (!currentReportData || currentReportData.length === 0) {
    showToast('No report data to export', 'warning');
    return;
  }

  const { jsPDF } = window.jspdf;
  if (!jsPDF) {
    showToast('jsPDF library is loading, please try again...', 'info');
    return;
  }

  const doc = new jsPDF();
  doc.setFont('Helvetica', 'normal');
  doc.setFontSize(16);
  doc.text(`AI Smart Inventory - ${currentReportType} Report`, 14, 20);
  doc.setFontSize(10);
  doc.text(`Generated At: ${new Date().toLocaleString()}`, 14, 28);
  
  // Format table rows
  const headers = Object.keys(currentReportData[0]);
  const rows = currentReportData.map(row => headers.map(h => String(row[h] || '')));

  // Use jsPDF Simple table generation
  let y = 38;
  doc.setFontSize(9);
  
  // Draw headers
  headers.forEach((h, idx) => {
    doc.text(String(h), 14 + (idx * 28), y);
  });
  doc.line(14, y + 2, 196, y + 2);
  y += 8;

  // Draw rows
  rows.forEach(row => {
    if (y > 275) {
      doc.addPage();
      y = 20;
    }
    row.forEach((cell, idx) => {
      doc.text(cell.substring(0, 18), 14 + (idx * 28), y);
    });
    y += 6;
  });

  doc.save(`${currentReportType.toLowerCase()}_report.pdf`);
  showToast('Report exported to PDF', 'success');
}
