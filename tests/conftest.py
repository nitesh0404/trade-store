import os
from pathlib import Path


os.environ.setdefault("DATABASE_URL", "sqlite:///./test_trade_store.db")

test_db_path = Path("test_trade_store.db")
if test_db_path.exists():
	test_db_path.unlink()
