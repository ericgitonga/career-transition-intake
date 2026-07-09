import gradio_client.utils as _gcu

# gradio 4.x ships with gradio-client 1.3.0 (a 5.x client). Its
# json_schema_to_python_type() doesn't guard against boolean schemas,
# crashing the route handler for every request. Patch it here.
_orig = _gcu.json_schema_to_python_type

def _safe_json_schema_to_python_type(schema, defs=None):
    try:
        return _orig(schema, defs)
    except TypeError:
        return "any"

_gcu.json_schema_to_python_type = _safe_json_schema_to_python_type

import os
from onboarding_form import app

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port, show_api=False)
