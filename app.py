"""
Hallucination Detector — Root Entry Point
-----------------------------------------
This file delegates execution to src/app.py, ensuring out-of-the-box compatibility
with deployment platforms that expect an app.py in the repository root
(such as Streamlit Community Cloud, Hugging Face Spaces, Docker, and Render).
"""

import sys
import runpy
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Execute the main Streamlit application
runpy.run_path(str(SRC / "app.py"), run_name="__main__")
