import os
from src.database import SecurityDatabase

def test_suspicious_first_time(tmp_path):
    dbfile = tmp_path / "t.db"
    db = SecurityDatabase(str(dbfile))
    assert db.shto_event("user1", "MODIFIED", "/tmp/a.txt") == 1
    assert db.shto_event("user1", "MODIFIED", "/tmp/a.txt") == 0
    assert db.shto_event("user2", "MODIFIED", "/tmp/a.txt") == 1
