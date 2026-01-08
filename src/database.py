#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

EventRow = Tuple[int, str, str, str, str, int]

class SecurityDatabase:
    def __init__(self, db_name: str = "security.db"):
        self.db_name = db_name
        self.krijo_tabela()

    def _conn(self):
        return sqlite3.connect(self.db_name)

    def krijo_tabela(self) -> None:
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_ora TEXT,
                perdoruesi TEXT,
                veprimi TEXT,
                file_path TEXT,
                suspicious INTEGER
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                perdoruesi TEXT,
                sa_here INTEGER DEFAULT 1,
                UNIQUE(file_path, perdoruesi)
            )
            """
        )

        conn.commit()
        conn.close()

    def shto_event(self, perdoruesi: str, veprimi: str, file_path: str) -> int:
        conn = self._conn()
        cursor = conn.cursor()

        tani = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            SELECT id FROM file_history
            WHERE file_path = ? AND perdoruesi = ?
            """,
            (file_path, perdoruesi),
        )

        ka_me_pare = cursor.fetchone() is not None
        eshte_suspicious = 0 if ka_me_pare else 1

        cursor.execute(
            """
            INSERT INTO events (data_ora, perdoruesi, veprimi, file_path, suspicious)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tani, perdoruesi, veprimi, file_path, eshte_suspicious),
        )

        if not ka_me_pare:
            cursor.execute(
                """
                INSERT OR IGNORE INTO file_history (file_path, perdoruesi)
                VALUES (?, ?)
                """,
                (file_path, perdoruesi),
            )
        else:
            cursor.execute(
                """
                UPDATE file_history
                SET sa_here = sa_here + 1
                WHERE file_path = ? AND perdoruesi = ?
                """,
                (file_path, perdoruesi),
            )

        conn.commit()
        conn.close()
        return eshte_suspicious

    def statistika(self) -> Dict[str, int]:
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM events")
        total = int(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM events WHERE suspicious = 1")
        suspicious = int(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(DISTINCT perdoruesi) FROM events")
        perdorues = int(cursor.fetchone()[0])

        conn.close()

        return {
            "total_events": total,
            "suspicious_events": suspicious,
            "perdorues_aktive": perdorues,
        }

    def merr_suspicious_events(self, limit: int = 50) -> List[EventRow]:
        conn = self._conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, data_ora, perdoruesi, veprimi, file_path, suspicious
            FROM events
            WHERE suspicious = 1
            ORDER BY data_ora DESC
            LIMIT ?
            """,
            (limit,),
        )

        events = cursor.fetchall()
        conn.close()
        return events
