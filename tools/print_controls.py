"""Prints every control in the Acturis window as a ready-to-copy line, for example:

    child_window(title="UNDERWRITING", auto_id="[PolicyAdmin]", control_type="ListItem")

Copy auto_id and control_type into a dict in acturis/locators.py:
    {"auto_id": "[PolicyAdmin]", "control_type": "ListItem"}

Run it while Acturis is open on the screen you want to automate:
    python tools/print_controls.py        (whole window: can take a few minutes)
    python tools/print_controls.py 8      (only 8 levels deep: faster)

The output goes to results/controls.txt because the tree is big.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from acturis import config, ui  # noqa: E402


def main():
    depth = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if not ui.main_window_exists(timeout=2):
        sys.exit("Acturis isn't open. Start it (and log in) first.")
    config.RESULTS_DIR.mkdir(exist_ok=True)
    output = config.RESULTS_DIR / "controls.txt"
    ui.main_window_spec().print_control_identifiers(depth=depth, filename=str(output))
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
