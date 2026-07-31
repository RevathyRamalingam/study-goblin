import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"

assert APP_PATH.exists(), "app.py should exist"

spec = importlib.util.spec_from_file_location("study_goblin_app", APP_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
