
/* ==========================================================================
   MEDICO HEALTHCARE & LOGISTICS - INTERACTIVE APPLICATION CONTROLLER
   Truck Path Motion, Sky Particle Canvas, Role Tabs, Form & Sound Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ------------------------------------------------------------------------
     1. AMBIENT SKY CANVAS PARTICLE ENGINE
     ------------------------------------------------------------------------ */
  const canvas = document.getElementById('sky-canvas');
  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];

  function resizeCanvas() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  class Particle {
    constructor() {
      this.reset();
    }

    reset() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.size = Math.random() * 3 + 1;
      this.speedY = -(Math.random() * 0.4 + 0.1);
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.opacity = Math.random() * 0.5 + 0.2;
      this.type = Math.random() > 0.85 ? 'cross' : 'dot';
    }

    update() {
      this.y += this.speedY;
      this.x += this.speedX;
      if (this.y < -10 || this.x < -10 || this.x > width + 10) {
        this.reset();
        this.y = height + 10;
      }
    }

    draw() {
      ctx.save();
      ctx.globalAlpha = this.opacity;
      if (this.type === 'cross') {
        ctx.strokeStyle = '#00E676';
        ctx.lineWidth = 1.5;
        const len = this.size * 2.5;
        ctx.beginPath();
        ctx.moveTo(this.x - len, this.y);
        ctx.lineTo(this.x + len, this.y);
        ctx.moveTo(this.x, this.y - len);
        ctx.lineTo(this.x, this.y + len);
        ctx.stroke();
      } else {
        ctx.fillStyle = '#A3E4D7';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }

  for (let i = 0; i < 45; i++) {
    particles.push(new Particle());
  }

  function animateParticles() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    requestAnimationFrame(animateParticles);
  }
  animateParticles();


  /* ------------------------------------------------------------------------
     2. SVG ROAD PATH TRUCK MOTION ENGINE
     ------------------------------------------------------------------------ */
  const truck = document.getElementById('medico-truck');
  const path = document.getElementById('truck-road-path');
  const roadSvg = document.getElementById('road-svg');
  const truckStatusMsg = document.getElementById('truck-status-msg');

  let pathLength = 0;
  let progress = 0; // 0 to 1
  let currentSpeed = 0.0008; // normal speed step

  function initTruckPath() {
    if (path) {
      pathLength = path.getTotalLength();
    }
  }
  initTruckPath();
  window.addEventListener('resize', initTruckPath);

  function animateTruck() {
    if (pathLength > 0 && truck && roadSvg) {
      progress += currentSpeed;
      if (progress > 1) {
        progress = 0; // Loop back to Warehouse
      }

      // Point at current distance
      const distance = progress * pathLength;
      const point = path.getPointAtLength(distance);

      // Next point for direction calculation
      const nextDistance = Math.min(distance + 2, pathLength);
      const nextPoint = path.getPointAtLength(nextDistance);

      // Convert SVG coordinates to percentage/px of road container
      const svgRect = roadSvg.getBoundingClientRect();
      const scaleX = svgRect.width / 1200; // viewBox width 1200
      const scaleY = svgRect.height / 240; // viewBox height 240

      const posX = point.x * scaleX - 65; // offset half truck width
      const posY = point.y * scaleY - 45; // offset truck height

      // Angle of rotation along path slope
      const dx = (nextPoint.x - point.x) * scaleX;
      const dy = (nextPoint.y - point.y) * scaleY;
      const angle = Math.atan2(dy, dx) * (180 / Math.PI);

      // Apply transformation
      truck.style.transform = `translate(${posX}px, ${posY}px) rotate(${angle}deg)`;

      // Dynamic Tooltip Dispatch Status
      if (progress < 0.25) {
        truckStatusMsg.textContent = '📦 Dispatching from Medico Warehouse Depot';
      } else if (progress >= 0.25 && progress < 0.75) {
        truckStatusMsg.textContent = '🚛 En Route: Transporting Vaccine & ICU Supplies';
      } else {
        truckStatusMsg.textContent = '🏥 Arriving at St. Jude Hospital Emergency Bay';
      }
    }
    requestAnimationFrame(animateTruck);
  }
  animateTruck();

  // Speed Control Buttons
  const speedButtons = document.querySelectorAll('.speed-btn');
  speedButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      speedButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.dataset.speed;
      if (mode === 'slow') currentSpeed = 0.0004;
      else if (mode === 'normal') currentSpeed = 0.0008;
      else if (mode === 'express') currentSpeed = 0.0018;
    });
  });


  /* ------------------------------------------------------------------------
     3. PORTAL ROLE SELECTOR TABS
     ------------------------------------------------------------------------ */
  const roleTabs = document.querySelectorAll('.role-tab');
  const roleBannerText = document.getElementById('role-banner-text');
  const usernameInput = document.getElementById('username-input');

  const roleConfigs = {
    doctor: {
      banner: 'Authenticating for Clinical Staff & Physicians',
      placeholder: 'e.g. DOC-9942@medico.org'
    },
    pharmacy: {
      banner: 'Authenticating for Pharmacy Depot & Supply Managers',
      placeholder: 'e.g. PHARM-4410@medico-depot.com'
    },
    patient: {
      banner: 'Authenticating for Secure Patient Medical Records',
      placeholder: 'e.g. PATIENT-7819@health.org'
    }
  };

  roleTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      roleTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const role = tab.dataset.role;
      if (roleConfigs[role]) {
        roleBannerText.textContent = roleConfigs[role].banner;
        usernameInput.placeholder = roleConfigs[role].placeholder;
      }
    });
  });


  /* ------------------------------------------------------------------------
     4. PASSWORD SHOW/HIDE & COMPLEXITY METER
     ------------------------------------------------------------------------ */
  const passwordInput = document.getElementById('password-input');
  const togglePasswordBtn = document.getElementById('toggle-password');
  const eyeIcon = document.getElementById('eye-icon');
  const meterBar = document.getElementById('meter-bar');
  const meterLabel = document.getElementById('meter-label');

  if (togglePasswordBtn && passwordInput && eyeIcon) {
    togglePasswordBtn.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      eyeIcon.className = type === 'password' ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
    });
  }

  if (passwordInput && meterBar && meterLabel) {
    passwordInput.addEventListener('input', (e) => {
      const val = e.target.value;
      meterBar.className = 'meter-bar';
      if (val.length === 0) {
        meterLabel.textContent = 'Encrypted 256-bit Connection';
      } else if (val.length < 6) {
        meterBar.classList.add('weak');
        meterLabel.textContent = 'Passcode Strength: Weak';
      } else if (val.length < 10) {
        meterBar.classList.add('medium');
        meterLabel.textContent = 'Passcode Strength: Moderate';
      } else {
        meterBar.classList.add('strong');
        meterLabel.textContent = 'Passcode Strength: Strong & Encrypted';
      }
    });
  }


  /* ------------------------------------------------------------------------
     5. DEMO LOGIN AUTOFILL HELPERS
     ------------------------------------------------------------------------ */
  const demoDoctorBtn = document.getElementById('demo-doctor-btn');
  const demoPharmacyBtn = document.getElementById('demo-pharmacy-btn');

  if (demoDoctorBtn) {
    demoDoctorBtn.addEventListener('click', () => {
      document.querySelector('.role-tab[data-role="doctor"]').click();
      usernameInput.value = 'doc.sarah@medico-care.org';
      passwordInput.value = 'MedicalPass2026!';
      passwordInput.dispatchEvent(new Event('input'));
    });
  }

  if (demoPharmacyBtn) {
    demoPharmacyBtn.addEventListener('click', () => {
      document.querySelector('.role-tab[data-role="pharmacy"]').click();
      usernameInput.value = 'pharmacy.depot@medico-supply.com';
      passwordInput.value = 'Warehouse#Supply99';
      passwordInput.dispatchEvent(new Event('input'));
    });
  }


  /* ------------------------------------------------------------------------
     6. TOGGLE FLOATING SKY ITEMS & AMBIENT MEDICAL HEARTBEAT SOUND
     ------------------------------------------------------------------------ */
  const toggleSkyBtn = document.getElementById('toggle-sky-btn');
  const skyContainer = document.getElementById('sky-elements');

  if (toggleSkyBtn && skyContainer) {
    toggleSkyBtn.addEventListener('click', () => {
      const isVisible = skyContainer.style.display !== 'none';
      skyContainer.style.display = isVisible ? 'none' : 'block';
      toggleSkyBtn.classList.toggle('active', !isVisible);
    });
  }

  // Web Audio Synth for Organic Pulse Beat
  const toggleSoundBtn = document.getElementById('toggle-sound-btn');
  const soundIcon = document.getElementById('sound-icon');
  let audioCtx = null;
  let isSoundActive = false;
  let beatTimer = null;

  function playHeartbeatSound() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(65, audioCtx.currentTime); // Low pulse freq
    osc.frequency.exponentialRampToValueAtTime(35, audioCtx.currentTime + 0.15);

    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
  }

  if (toggleSoundBtn && soundIcon) {
    toggleSoundBtn.addEventListener('click', () => {
      isSoundActive = !isSoundActive;
      toggleSoundBtn.classList.toggle('active', isSoundActive);
      soundIcon.className = isSoundActive ? 'fa-solid fa-volume-high' : 'fa-solid fa-volume-xmark';

      if (isSoundActive) {
        beatTimer = setInterval(() => {
          playHeartbeatSound();
          setTimeout(playHeartbeatSound, 220); // Lub-dub double pulse
        }, 1400);
      } else {
        if (beatTimer) clearInterval(beatTimer);
      }
    });
  }


  /* ------------------------------------------------------------------------
     7. FORM SUBMISSION & SUCCESS MODAL
     ------------------------------------------------------------------------ */
  const loginForm = document.getElementById('medico-login-form');
  const submitBtn = document.getElementById('submit-btn');
  const successModal = document.getElementById('success-modal');
  const modalSuccessText = document.getElementById('modal-success-text');

  if (loginForm && submitBtn && successModal) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const userVal = usernameInput.value || 'Medical User';
      submitBtn.disabled = true;
      submitBtn.querySelector('.btn-text').textContent = 'AUTHENTICATING...';
      submitBtn.querySelector('.btn-icon').innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';

      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').textContent = 'ACCESS MEDICO PORTAL';
        submitBtn.querySelector('.btn-icon').innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i>';

        modalSuccessText.textContent = `Welcome back, ${userVal}. Authenticated with 256-bit encryption. Accessing dashboard...`;
        successModal.classList.add('active');

        setTimeout(() => {
          successModal.classList.remove('active');
        }, 3200);
      }, 1200);
    });
  }

});
