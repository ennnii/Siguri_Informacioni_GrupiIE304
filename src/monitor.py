#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.database import SecurityDatabase


def setup_logging(log_file: str | None = None, verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


class FileMonitor(FileSystemEventHandler):
    def __init__(self, database: SecurityDatabase, monitored_path: str, ignored: List[str]):
        self.db = database
        self.monitored_path = monitored_path
        self.ignored_suffixes = ignored

        logging.info("Monitorimi u inicializua per: %s", monitored_path)

    def duhet_injoruar(self, filepath: str) -> bool:
        p = filepath.replace("\\", "/")

        # avoid noise / self recursion
        if "/.git/" in p or "/venv/" in p or "/__pycache__/" in p:
            return True
        if p.endswith("/security.db") or p.endswith("security.db"):
            return True
        if "/reports/" in p:
            return True

        for suf in self.ignored_suffixes:
            if suf and p.endswith(suf):
                return True

        return False

    def merr_perdorues(self) -> str:
        try:
            return os.getlogin()
        except Exception:
            import pwd
            return pwd.getpwuid(os.getuid()).pw_name

    def _log_event(self, event_type: str, filepath: str) -> None:
        perdoruesi = self.merr_perdorues()
        suspicious = self.db.shto_event(perdoruesi, event_type, filepath)

        if suspicious:
            logging.warning("SUSPICIOUS: user=%s action=%s file=%s", perdoruesi, event_type, filepath)
        else:
            logging.info("user=%s action=%s file=%s", perdoruesi, event_type, filepath)

    def on_created(self, event):
        if not event.is_directory and not self.duhet_injoruar(event.src_path):
            self._log_event("CREATED", event.src_path)

    def on_modified(self, event):
        if not event.is_directory and not self.duhet_injoruar(event.src_path):
            self._log_event("MODIFIED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory and not self.duhet_injoruar(event.src_path):
            self._log_event("DELETED", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            dest = getattr(event, "dest_path", "")
            src = getattr(event, "src_path", "")
            if dest and not self.duhet_injoruar(dest):
                self._log_event("MOVED", f"{src} -> {dest}")


def parse_args():
    ap = argparse.ArgumentParser(description="SI Log Event Manager - File monitor")
    ap.add_argument("--path", default=str(Path.cwd()), help="Folder qe do monitorohet (default: cwd)")
    ap.add_argument("--db", default="security.db", help="Rruga e databazes SQLite")
    ap.add_argument("--recursive", action="store_true", help="Monitorim rekursiv (nensubfoldera)")
    ap.add_argument("--ignore", default=".swp,.tmp,~,.log", help="Suffixes per me i injoru, te ndara me presje")
    ap.add_argument("--log-file", default=None, help="Ruaj log edhe ne file (p.sh. /var/log/si-monitor.log)")
    ap.add_argument("--verbose", action="store_true", help="Debug logs")
    return ap.parse_args()


def main():
    args = parse_args()
    setup_logging(args.log_file, args.verbose)

    monitored = os.path.abspath(args.path)
    if not os.path.isdir(monitored):
        raise SystemExit(f"Path nuk ekziston ose s'eshte folder: {monitored}")

    ignored = [x.strip() for x in args.ignore.split(",") if x.strip()]

    db = SecurityDatabase(args.db)
    handler = FileMonitor(db, monitored, ignored)

    observer = Observer()
    observer.schedule(handler, monitored, recursive=bool(args.recursive))
    observer.start()

    logging.info("Monitorimi ka fillu (Ctrl+C per ndalim). recursive=%s", bool(args.recursive))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Monitorimi u ndal")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
