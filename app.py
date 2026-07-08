"""
Hugging Face Spaces entrypoint.
HF looks for app.py; this thin wrapper imports the form and launches it
with settings appropriate for the host environment.
"""
import os
import gradio as gr
from onboarding_form import app, css

hf = bool(os.environ.get("SPACE_ID"))  # HF sets SPACE_ID automatically

app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=not hf,
    inbrowser=not hf,
    css=css,
    theme=gr.themes.Soft(),
)
