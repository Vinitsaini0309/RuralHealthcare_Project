/* ==========================================================================
   ST. JUDE EMERGENCY CARE - CLINIC DASHBOARD CONTROLLER
   All 8 Clinic Demand & Dispensing Modules Interactivity
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ------------------------------------------------------------------------
     1. TAB NAVIGATION CONTROLLER
     ------------------------------------------------------------------------ */
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPages = document.querySelectorAll('.tab-page');

  window.switchTab = function(targetTabId) {
    navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === targetTabId);
    });

    tabPages.forEach(page => {
      page.classList.toggle('active', page.id === targetTabId);
    });
  };

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      window.switchTab(btn.dataset.tab);
    });
  });

  const viewAllLinks = document.querySelectorAll('.view-all-link');
  viewAllLinks.forEach(link => {
    link.addEventListener('click', () => {
      window.switchTab(link.dataset.target);
    });
  });

  const quickRxBtn = document.getElementById('quick-rx-btn');
  if (quickRxBtn) {
    quickRxBtn.addEventListener('click', () => window.switchTab('tab-rx-scanner'));
  }


  /* ------------------------------------------------------------------------
     2. MODULE 5: PRESCRIPTION SCANNER & AUTO-DISPENSER (CORE CLINIC FEATURE)
     ------------------------------------------------------------------------ */
  const scanRxBtn = document.getElementById('scan-rx-btn');
  const confirmDispenseBtn = document.getElementById('confirm-dispense-btn');
  const rxStatusTag = document.getElementById('rx-status-tag');
  const stockLogTbody = document.getElementById('stock-log-tbody');

  function playScanBeep() {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc.type = 'sine';
      osc.frequency.value = 1800; // High beep
      gain.gain.value = 0.2;

      osc.connect(gain);
      gain.connect(audioCtx.destination);

      osc.start();
      osc.stop(audioCtx.currentTime + 0.12);
    } catch (e) {
      console.log('Audio not allowed without gesture');
    }
  }

  if (scanRxBtn) {
    scanRxBtn.addEventListener('click', () => {
      playScanBeep();
      alert('📟 PRESCRIPTION SCAN SUCCESSFUL!\nMatched Patient: Johnathan Doe (#RX-88402)\nItems: Amoxicillin 500mg (21 caps), Paracetamol 650mg (10 tabs).\nFloor Stock Verified & Reserved!');
    });
  }

  if (confirmDispenseBtn) {
    confirmDispenseBtn.addEventListener('click', () => {
      playScanBeep();

      if (rxStatusTag) {
        rxStatusTag.className = 'tag tag-green';
        rxStatusTag.textContent = 'Status: DISPENSED & DEDUCTED';
      }

      // Add to Ground-Truth Stock Log (Module 1)
      if (stockLogTbody) {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
          <td>#LOG-${Math.floor(1000 + Math.random() * 9000)}</td>
          <td>Amoxicillin 500mg & Paracetamol</td>
          <td><span class="tag tag-red">CONSUMED (DISPENSED)</span></td>
          <td>-31 units total</td>
          <td>Patient: Johnathan Doe (#RX-88402)</td>
          <td>Just Now</td>
        `;
        stockLogTbody.insertBefore(newRow, stockLogTbody.firstChild);
      }

      alert('💊 PRESCRIPTION DISPENSED!\n21 caps Amoxicillin & 10 tabs Paracetamol handed to patient.\nClinic floor inventory automatically updated & logged.');
    });
  }


  /* ------------------------------------------------------------------------
     3. MODULE 1: STOCK INTAKE & CONSUMPTION LOG
     ------------------------------------------------------------------------ */
  const logConsumptionBtn = document.getElementById('log-consumption-btn');
  if (logConsumptionBtn) {
    logConsumptionBtn.addEventListener('click', () => {
      const item = prompt('Enter Medicine Name for Manual Log:', 'Oxygen Cylinder 10L');
      if (item && stockLogTbody) {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
          <td>#LOG-${Math.floor(1000 + Math.random() * 9000)}</td>
          <td>${item}</td>
          <td><span class="tag tag-red">CONSUMED (MANUAL LOG)</span></td>
          <td>-1 unit</td>
          <td>Emergency Ward Dispense</td>
          <td>Just Now</td>
        `;
        stockLogTbody.insertBefore(newRow, stockLogTbody.firstChild);
        alert(`✅ Logged consumption of ${item} in ground-truth inventory.`);
      }
    });
  }


  /* ------------------------------------------------------------------------
     4. MODULE 2 & 3: REQUEST RESTOCK FROM WAREHOUSE
     ------------------------------------------------------------------------ */
  const openReqModalBtn = document.getElementById('open-request-modal-btn');
  const reqModal = document.getElementById('request-modal');
  const closeReqModal = document.getElementById('close-req-modal');
  const cancelReqBtn = document.getElementById('cancel-req-btn');
  const submitReqBtn = document.getElementById('submit-req-btn');
  const clinicRequestsTbody = document.getElementById('clinic-requests-tbody');

  window.requestRestockForItem = function(itemName) {
    const select = document.getElementById('req-item-name');
    if (select) select.value = itemName;
    if (reqModal) reqModal.classList.add('active');
  };

  if (openReqModalBtn && reqModal) {
    openReqModalBtn.addEventListener('click', () => reqModal.classList.add('active'));
  }

  if (closeReqModal) closeReqModal.addEventListener('click', () => reqModal.classList.remove('active'));
  if (cancelReqBtn) cancelReqBtn.addEventListener('click', () => reqModal.classList.remove('active'));

  if (submitReqBtn && clinicRequestsTbody) {
    submitReqBtn.addEventListener('click', () => {
      const item = document.getElementById('req-item-name').value;
      const qty = document.getElementById('req-item-qty').value || '100';
      const urgency = document.getElementById('req-item-urgency').value;

      const reqId = '#TR-' + Math.floor(4000 + Math.random() * 900);
      const newRow = document.createElement('tr');
      const urgencyClass = urgency.includes('ICU') ? 'tag-red' : 'tag-green';

      newRow.innerHTML = `
        <td>${reqId}</td>
        <td>${item}</td>
        <td>${qty} units</td>
        <td><span class="tag ${urgencyClass}">${urgency}</span></td>
        <td><span class="status-chip chip-yellow">Pending Warehouse Approval</span></td>
        <td><button class="table-btn approve-btn-sm" onclick="switchTab('tab-incoming')">View ETA Map</button></td>
      `;

      clinicRequestsTbody.insertBefore(newRow, clinicRequestsTbody.firstChild);
      reqModal.classList.remove('active');

      alert(`🚀 RESTOCK REQUEST SUBMITTED!\nRequest ID: ${reqId}\nRequested: ${qty} units of ${item}\nWarehouse Owner notified for decision-making & approval.`);
      window.switchTab('tab-requests');
    });
  }


  /* ------------------------------------------------------------------------
     5. MODULE 4: INCOMING DELIVERY TRACKER MAP
     ------------------------------------------------------------------------ */
  const clinicMapTruck = document.getElementById('clinic-map-truck');
  if (clinicMapTruck) {
    let pos = 320;
    setInterval(() => {
      pos += 3;
      if (pos > 520) pos = 60;
      clinicMapTruck.style.left = pos + 'px';
    }, 150);
  }


  /* ------------------------------------------------------------------------
     6. MODULE 6: ARRIVAL BARCODE SCANNER (RECEIPT VERIFICATION)
     ------------------------------------------------------------------------ */
  const scanArrivalBtn = document.getElementById('scan-arrival-btn');
  const arrivalStatusTag = document.getElementById('arrival-status-tag');

  if (scanArrivalBtn) {
    scanArrivalBtn.addEventListener('click', () => {
      playScanBeep();
      if (arrivalStatusTag) {
        arrivalStatusTag.textContent = 'Arrival Verified: 2 / 2 Batches Credited';
      }
      alert('📟 ARRIVAL BATCH VERIFIED!\nTruck #MD-04 arrival packages scanned at receiving dock.\nStock automatically credited to St. Jude Floor Inventory!');
    });
  }


  /* ------------------------------------------------------------------------
     7. MODULE 7: OBJECTION RAISE FORM
     ------------------------------------------------------------------------ */
  const raiseObjectionForm = document.getElementById('raise-objection-form');
  if (raiseObjectionForm) {
    raiseObjectionForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const shipment = document.getElementById('obj-shipment').value;
      const category = document.getElementById('obj-category').value;
      const qty = document.getElementById('obj-qty').value;

      const ticketId = '#OBJ-' + Math.floor(800 + Math.random() * 90);

      alert(`🚨 DELIVERY OBJECTION RAISED!\nTicket ${ticketId} created for ${shipment}.\nIssue: ${category} (${qty}).\nWarehouse Owner Dashboard notified for resolution.`);
      raiseObjectionForm.reset();
    });
  }

});
