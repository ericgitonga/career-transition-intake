"""
Cloud Run entrypoint. PORT is set to 8080 by Cloud Run at runtime.
"""
import os
from onboarding_form import app

port = int(os.environ.get("PORT", 7860))

app.launch(server_name="0.0.0.0", server_port=port, ssr_mode=False)
