# Hosting the Onboarding Form on Hugging Face Spaces

Hugging Face Spaces runs Gradio apps for free on a persistent public URL — no 72-hour expiry.

---

## One-time setup

### 1. Create a Hugging Face account
Go to https://huggingface.co and sign up (free tier is sufficient).

### 2. Create a new Space
1. Click your profile avatar → **New Space**
2. Fill in:
   - **Space name**: e.g. `career-transition-intake`
   - **License**: MIT (or leave blank)
   - **SDK**: **Gradio**
   - **Hardware**: CPU Basic (free)
3. Click **Create Space** — this creates a Git repo at:
   `https://huggingface.co/spaces/<your-username>/career-transition-intake`

---

## Files to push

The Space repo needs exactly three files alongside `onboarding_form.py`:

### `app.py`
Hugging Face Spaces looks for `app.py` as the entrypoint, not `onboarding_form.py`.
Either rename the file or create `app.py` that imports it.

**Simplest approach — rename on upload:**
Upload `onboarding_form.py` as `app.py`. No code changes needed.

**Alternative — thin wrapper `app.py`:**
```python
from onboarding_form import app
app.launch()
```
Remove the `if __name__ == "__main__": app.launch(...)` block from `onboarding_form.py` if using this approach.

### `requirements.txt`
```
gradio>=4.0
reportlab
```

### `README.md` (Space card — required by HF)
```yaml
---
title: Career Transition Intake
emoji: 📋
colorFrom: blue
colorTo: teal
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
---
```
The YAML frontmatter is what Hugging Face reads to configure the Space.
The rest of the file can be left blank or contain a brief description.

---

## SMTP credentials (Secrets)

Never hardcode credentials in the uploaded files. Hugging Face Spaces has a Secrets store:

1. Open your Space → **Settings** tab → **Repository secrets**
2. Add two secrets:
   - `SMTP_USER` → your Gmail address (e.g. `gitonga@gmail.com`)
   - `SMTP_PASSWORD` → your Gmail App Password (16-character code from https://myaccount.google.com/apppasswords)

`onboarding_form.py` already reads these from `os.environ` — no code change needed:
```python
ENV_SMTP_USER = os.environ.get("SMTP_USER", "")
ENV_SMTP_PASS = os.environ.get("SMTP_PASSWORD", "")
```

---

## Deploying

### Option A — Hugging Face web UI (simplest)
1. Open your Space → **Files** tab → **Add file → Upload files**
2. Upload:
   - `onboarding_form.py` (rename to `app.py` during upload, or use the wrapper approach)
   - `requirements.txt`
   - `README.md` (with the YAML frontmatter above)
3. Click **Commit changes** — the Space rebuilds automatically (takes ~2 minutes)

### Option B — Git push
```bash
# Install Git LFS (required by HF)
git lfs install

# Clone your Space repo
git clone https://huggingface.co/spaces/<your-username>/career-transition-intake
cd career-transition-intake

# Copy files in
cp /path/to/onboarding_form.py app.py
# create requirements.txt and README.md as above

git add app.py requirements.txt README.md
git commit -m "initial deployment"
git push
```

---

## After deployment

- Your permanent public URL is:
  `https://<your-username>-career-transition-intake.hf.space`
- The Space rebuilds automatically on every push.
- If the Space goes to sleep (free tier sleeps after ~48 hours of inactivity), it wakes up the next time someone visits — takes ~30 seconds.

### To prevent sleep (optional)
Upgrade the Space hardware to **CPU Upgrade** ($0.03/hr) — paid Spaces never sleep.
Or keep the free tier and warn clients the first load may take 30 seconds.

---

## `launch()` change for Spaces

On Hugging Face Spaces, `share=True` is unnecessary and `inbrowser=True` has no effect.
The recommended call for a deployed Space:

```python
app.launch(server_name="0.0.0.0", server_port=7860)
```

For local runs keep `share=True` (or `share=False`) and `inbrowser=True` as currently set.
A clean way to handle both environments:

```python
import os

hf = bool(os.environ.get("SPACE_ID"))  # HF sets this automatically

app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=not hf,
    inbrowser=not hf,
    css=css,
    theme=gr.themes.Soft(),
)
```

This auto-detects whether it's running on Hugging Face and adjusts accordingly.
