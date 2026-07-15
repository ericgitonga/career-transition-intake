// Client type — show employment block for job-seekers, entrepreneur block for business owners / freelancers;
// also drives the Section 10 CV-vs-business-profile field, since it's the same route decision.
(function () {
  const empBlock  = document.getElementById('employment-block');
  const entBlock  = document.getElementById('entrepreneur-block');
  const esBlock   = document.getElementById('employed-status-block');
  const otherWrap = document.getElementById('client-type-other-wrap');

  const cvLabel  = document.getElementById('cv-label');
  const cvHint   = document.getElementById('cv-hint');
  const toggle   = document.getElementById('cv-fallback-toggle');
  const fallback = document.getElementById('cv-fallback');
  const cvInput  = document.getElementById('cv-input');

  let cvIsEntrepreneur = false;

  function toggleBaseText() {
    return cvIsEntrepreneur
      ? "Don't have a profile ready? Fill in your background here instead"
      : 'No CV ready? Fill in your background here instead';
  }

  function refreshCvToggleText() {
    const hidden = fallback.classList.contains('d-none');
    toggle.textContent = toggleBaseText() + (hidden ? ' ▾' : ' ▴');
  }

  function applyClientType(val) {
    const isEntrepreneur = val === 'Entrepreneur or business owner' || val === 'Freelancer or independent consultant';
    empBlock.classList.toggle('d-none', isEntrepreneur);
    entBlock.classList.toggle('d-none', !isEntrepreneur);
    if (isEntrepreneur) esBlock.classList.add('d-none');
    otherWrap.classList.toggle('d-none', val !== 'Other');

    cvIsEntrepreneur = isEntrepreneur;
    cvLabel.textContent = isEntrepreneur ? 'Business Profile / Pitch Deck *' : 'CV / Résumé *';
    cvHint.textContent = isEntrepreneur
      ? 'Upload a company profile, pitch deck, or bio — or fill in the background questions below.'
      : "Upload your CV — or fill in the background questions below if it isn't ready yet.";
    refreshCvToggleText();
  }

  toggle.addEventListener('click', function (e) {
    e.preventDefault();
    fallback.classList.toggle('d-none');
    refreshCvToggleText();
  });

  cvInput.addEventListener('change', function () {
    if (this.files.length > 0) {
      fallback.classList.add('d-none');
      refreshCvToggleText();
    }
  });

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

// Record when the page finished loading so we can measure time on form
const _pageLoadedAt = Date.now();

// Hours slider — update displayed value in real time
const range = document.getElementById('hrs-range');
const val   = document.getElementById('hrs-val');
range.addEventListener('input', () => val.textContent = range.value);

// Form submit via fetch → PDF download
document.getElementById('form').addEventListener('submit', async function (e) {
  e.preventDefault();
  const form   = this;
  const btn    = document.getElementById('submit-btn');
  const status = document.getElementById('status');

  // Require either a CV/business-profile upload or the background fallback fields —
  // whichever route Section 1's client type points to. Without one of these, the
  // consultant has nothing to generate a plan from.
  const cvInput = document.getElementById('cv-input');
  const fallbackFields = ['current_title', 'current_industry', 'years_experience', 'existing_certs', 'key_skills'];
  const fallbackFilled = fallbackFields.some(name => (form.elements[name].value || '').trim().length > 0);

  if (cvInput.files.length === 0 && !fallbackFilled) {
    bootstrap.Collapse.getOrCreateInstance(document.getElementById('s10')).show();
    if (document.getElementById('cv-fallback').classList.contains('d-none')) {
      document.getElementById('cv-fallback-toggle').click();
    }
    cvInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const isEntrepreneur = document.getElementById('cv-label').textContent.includes('Business');
    status.className = 'alert alert-danger';
    status.textContent = 'Please upload your ' + (isEntrepreneur ? 'business profile or pitch deck' : 'CV/résumé')
      + ', or fill in the background questions in Section 10, before submitting.';
    status.classList.remove('d-none');
    return;
  }

  document.getElementById('time-on-form').value = Math.round((Date.now() - _pageLoadedAt) / 1000);

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
