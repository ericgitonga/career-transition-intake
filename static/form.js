// Client type — show employment block for job-seekers, entrepreneur block for business owners / freelancers
(function () {
  const empBlock  = document.getElementById('employment-block');
  const entBlock  = document.getElementById('entrepreneur-block');
  const esBlock   = document.getElementById('employed-status-block');

  const otherWrap = document.getElementById('client-type-other-wrap');

  function applyClientType(val) {
    const isEntrepreneur = val === 'Entrepreneur or business owner' || val === 'Freelancer or independent consultant';
    empBlock.classList.toggle('d-none', isEntrepreneur);
    entBlock.classList.toggle('d-none', !isEntrepreneur);
    if (isEntrepreneur) esBlock.classList.add('d-none');
    otherWrap.classList.toggle('d-none', val !== 'Other');
  }

  document.querySelectorAll('input[name="client_type"]').forEach(function (radio) {
    radio.addEventListener('change', function () { applyClientType(this.value); });
    if (radio.checked) applyClientType(radio.value);
  });
})();

// Employment status follow-up — only show when "Yes" (currently employed) is selected
(function () {
  const esBlock = document.getElementById('employed-status-block');
  document.querySelectorAll('input[name="employed"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      esBlock.classList.toggle('d-none', this.value !== 'Yes');
    });
  });
})();

// Target role title — reveal only when clarity is "Very clear" or "Clear"
document.querySelectorAll('input[name="target_clarity"]').forEach(function (radio) {
  radio.addEventListener('change', function () {
    const wrap = document.getElementById('role-title-wrap');
    const show = this.value.startsWith('Very clear') || this.value.startsWith('Clear —');
    wrap.classList.toggle('d-none', !show);
  });
});

// Portfolio links — show/hide based on yes/no radio; dynamic add/remove rows
(function () {
  const wrap = document.getElementById('portfolio-links-wrap');
  const list = document.getElementById('portfolio-links-list');

  document.querySelectorAll('input[name="portfolio_has_work"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      wrap.classList.toggle('d-none', this.value !== 'yes');
    });
  });

  document.getElementById('add-portfolio-link').addEventListener('click', function () {
    const row = document.createElement('div');
    row.className = 'input-group mb-2 portfolio-link-row';
    row.innerHTML =
      '<input type="url" name="portfolio_links" class="form-control" placeholder="https://">' +
      '<button type="button" class="btn btn-outline-secondary remove-link" tabindex="-1" title="Remove this link">×</button>';
    list.appendChild(row);
    row.querySelector('input').focus();
  });

  list.addEventListener('click', function (e) {
    if (e.target.classList.contains('remove-link')) {
      const rows = list.querySelectorAll('.portfolio-link-row');
      if (rows.length > 1) {
        e.target.closest('.portfolio-link-row').remove();
      }
    }
  });
})();

// CV fallback — toggle visibility via link; auto-hide when a file is selected
(function () {
  const toggle   = document.getElementById('cv-fallback-toggle');
  const fallback = document.getElementById('cv-fallback');
  const cvInput  = document.getElementById('cv-input');

  toggle.addEventListener('click', function (e) {
    e.preventDefault();
    const hidden = fallback.classList.toggle('d-none');
    toggle.textContent = hidden
      ? 'No CV ready? Fill in your background here instead ▾'
      : 'No CV ready? Fill in your background here instead ▴';
  });

  cvInput.addEventListener('change', function () {
    if (this.files.length > 0) {
      fallback.classList.add('d-none');
      toggle.textContent = 'No CV ready? Fill in your background here instead ▾';
    }
  });
})();

// Hours slider — update displayed value in real time
const range = document.getElementById('hrs-range');
const val   = document.getElementById('hrs-val');
range.addEventListener('input', () => val.textContent = range.value);

// Form submit via fetch → PDF download
document.getElementById('form').addEventListener('submit', async function (e) {
  e.preventDefault();
  const btn    = document.getElementById('submit-btn');
  const status = document.getElementById('status');

  btn.disabled = true;
  btn.textContent = 'Processing…';
  status.className = 'alert alert-info';
  status.textContent = 'Generating your PDF…';
  status.classList.remove('d-none');

  try {
    const res = await fetch('/submit', { method: 'POST', body: new FormData(this) });

    if (res.ok) {
      const blob = await res.blob();
      const cd   = res.headers.get('content-disposition') || '';
      const m    = cd.match(/filename="?([^"]+)"?/);
      const name = m ? m[1] : 'intake.pdf';

      const url = URL.createObjectURL(blob);
      const a   = document.getElementById('pdf-anchor');
      a.href     = url;
      a.download = name;
      document.getElementById('pdf-link').classList.remove('d-none');

      // Trigger automatic download
      const tmp = document.createElement('a');
      tmp.href = url; tmp.download = name;
      document.body.appendChild(tmp); tmp.click(); document.body.removeChild(tmp);

      const emailStatus = res.headers.get('x-email-status');
      const emailNote = emailStatus === 'sent'
        ? ' A copy has been emailed to your consultant.'
        : emailStatus === 'failed'
        ? ' (Email delivery failed — please contact your consultant directly.)'
        : '';

      status.className = 'alert alert-success';
      status.textContent = 'Your intake form has been submitted. Your PDF is downloading now.' + emailNote;

    } else {
      const txt = await res.text();
      status.className = 'alert alert-danger';
      if (res.status === 400 && (txt.includes('CSRF') || txt.includes('session token') || txt.includes('Bad Request'))) {
        status.innerHTML = 'Your session expired while you were filling in the form. '
          + '<strong>Please refresh the page and resubmit</strong> — '
          + 'your answers will still be visible in the form.';
      } else if (res.status === 400) {
        status.textContent = txt;
      } else if (res.status === 413) {
        status.textContent = 'Your files are too large. The total upload size must be under 10 MB.';
      } else if (res.status === 429) {
        status.textContent = 'Too many submissions. Please wait a few minutes and try again.';
      } else {
        status.textContent = 'Something went wrong. Please try again or contact your consultant directly.';
      }
    }
  } catch (err) {
    status.className = 'alert alert-danger';
    status.textContent = 'Network error: ' + err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit Onboarding Form';
  }
});
