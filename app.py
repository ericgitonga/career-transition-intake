import gradio_client.utils as _gcu

# gradio-client 1.3.0 (bundled with gradio 4.x) doesn't guard against
# boolean schemas in json_schema_to_python_type, crashing the route handler.
_orig = _gcu.json_schema_to_python_type

def _safe_json_schema_to_python_type(schema, defs=None):
    try:
        return _orig(schema, defs)
    except TypeError:
        return "any"

_gcu.json_schema_to_python_type = _safe_json_schema_to_python_type

# Render blocks loopback connections, so Gradio's post-startup self-ping
# always fails and raises ValueError. The server IS accessible externally;
# bypass the internal check.
import gradio.networking as _gnet
_gnet.url_ok = lambda url: True

import os
from onboarding_form import app

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port, show_api=False)
