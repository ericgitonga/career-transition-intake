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
      status.textContent = 'Error: ' + txt;
    }
  } catch (err) {
    status.className = 'alert alert-danger';
    status.textContent = 'Network error: ' + err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit Onboarding Form';
  }
});
