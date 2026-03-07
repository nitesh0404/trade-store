import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0,str(PROJECT_ROOT))
	
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_trade_store.db")

test_db_path = Path("test_trade_store.db")
if test_db_path.exists():
	test_db_path.unlink()
