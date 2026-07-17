"""
Career Transition Plan CLI — generates one client's plan PDF via report_builder.py.

Run:  python3 generate_plan.py "Client Name"

Reads Clients/<Client Name>/plan_data.py's PLAN dict and writes
Clients/<Client Name>/<initials>_transition_plan.pdf alongside it.
"""

import importlib.util
import os
import sys

from report_builder import build_plan

HERE = os.path.dirname(__file__)


def load_plan(client_name):
    data_path = os.path.join(HERE, "Clients", client_name, "plan_data.py")
    spec = importlib.util.spec_from_file_location("plan_data", data_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PLAN


def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 generate_plan.py "Client Name"')

    client_name = sys.argv[1]
    data = load_plan(client_name)
    initials = data["client"]["initials"]
    output_path = os.path.join(HERE, "Clients", client_name, f"{initials}_transition_plan.pdf")
    build_plan(data, output_path)


if __name__ == "__main__":
    main()
