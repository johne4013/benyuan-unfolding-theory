import sys
from pathlib import Path

# Add the scripts directory so test modules can import scripts directly.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
