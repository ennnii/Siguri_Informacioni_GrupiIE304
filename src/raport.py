#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
from datetime import datetime
from collections import Counter
import os
from pathlib import Path


class RaportGenerator:
    def __init__(self, db_path: str = "security.db", reports_dir: str = "reports"):
        self.db_path = db_path
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def merr_te_dhenat(self, data: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM events
            WHERE data_ora LIKE ?
            ORDER BY data_ora DESC
            """,
            (f"{data}%",),
        )
        events = cursor.fetchall()

        cursor.execute(
            """
            SELECT * FROM events
            WHERE data_ora LIKE ? AND suspicious = 1
            ORDER BY data_ora DESC
            """,
            (f"{data}%",),
        )
        suspicious_events = cursor.fetchall()

        conn.close()
        return events, suspicious_events

    def gjenero_raport_tekst(self, data: str):
        events, suspicious_events = self.merr_te_dhenat(data)

        if not events:
            return f"Nuk ka te dhena per daten {data}"

        total_events = len(events)
        total_suspicious = len(suspicious_events)

        perdoruesit = [e[2] for e in events]
        perdorues_unike = list(set(perdoruesit))

        veprimet = [e[3] for e in events]
        veprime_count = Counter(veprimet)

        files = [e[4] for e in events]
        files_count = Counter(files)
        top_files = files_count.most_common(5)

        perdorues_count = Counter(perdoruesit)
        top_perdorues = perdorues_count.most_common(5)

        raport = []
        raport.append("╔" + "═" * 68 + "╗")
        raport.append("║" + " " * 15 + "RAPORTI DITOR I SIGURISE" + " " * 31 + "║")
        raport.append("║" + f" Data: {data}" + " " * (68 - len(f" Data: {data}")) + "║")
        raport.append("╚" + "═" * 68 + "╝")
        raport.append("")

        raport.append("PERMBLEDHJE E PERGJITHSHME")
        raport.append(f"  • Totali i Events:              {total_events}")
        raport.append(f"  • Events Suspicious:            {total_suspicious} ({total_suspicious/total_events*100:.1f}%)")
        raport.append(f"  • Perdorues Aktive:             {len(perdorues_unike)}")
        raport.append(f"  • CREATED:                      {veprime_count.get('CREATED', 0)}")
        raport.append(f"  • MODIFIED:                     {veprime_count.get('MODIFIED', 0)}")
        raport.append(f"  • DELETED:                      {veprime_count.get('DELETED', 0)}")
        raport.append(f"  • MOVED:                        {veprime_count.get('MOVED', 0)}")
        raport.append("")

        raport.append("TOP 5 PERDORUESIT ME AKTIVE")
        raport.append("")
        for i, (user, count) in enumerate(top_perdorues, 1):
            raport.append(f"  {i}. {user:30s} {count:3d} veprime")
        raport.append("")

        raport.append("TOP 5 FILE-T ME TE MODIFIKUARA")
        raport.append("")
        for i, (file, count) in enumerate(top_files, 1):
            file_short = file if len(file) <= 50 else "..." + file[-47:]
            raport.append(f"  {i}. {file_short:50s} {count:3d} here")
        raport.append("")

        if suspicious_events:
            raport.append("⚠️  AKTIVITETE SUSPICIOUS (DETAJE)")
            raport.append("")
            for event in suspicious_events[:10]:
                event_id, data_ora, perdoruesi, veprimi, file_path, suspicious = event
                ora = data_ora.split()[1] if " " in data_ora else data_ora
                file_short = file_path if len(file_path) <= 50 else "..." + file_path[-47:]
                raport.append(f"  [{ora}] ALARM!")
                raport.append(f"    Perdoruesi:  {perdoruesi}")
                raport.append(f"    Veprimi:     {veprimi}")
                raport.append(f"    File:        {file_short}")
                raport.append("    Arsye:       Perdoruesi nuk e ka modifikuar kete file me pare")
                raport.append("")
            if len(suspicious_events) > 10:
                raport.append(f"  ... dhe {len(suspicious_events) - 10} aktivitete te tjera suspicious")
            raport.append("")
        else:
            raport.append("✅ NUK KA AKTIVITETE SUSPICIOUS")
            raport.append("")

        raport.append("Raporti u gjenerua me: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return "\n".join(raport)

    def ruaj_raport(self, raport: str, data: str) -> str:
        filename = os.path.join(self.reports_dir, f"raport_{data}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(raport)
        return filename

    def gjenero_dhe_ruaj(self, data: str):
        raport = self.gjenero_raport_tekst(data)
        filename = self.ruaj_raport(raport, data)
        return raport, filename


def parse_args():
    ap = argparse.ArgumentParser(description="Gjenero raport ditor nga security.db")
    ap.add_argument("--db", default="security.db", help="Rruga e databazes SQLite")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Data YYYY-MM-DD (default: sot)")
    ap.add_argument("--out", default="reports", help="Folder per raportet (default: reports)")
    return ap.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.db):
        print(f"ERROR: Databaza '{args.db}' nuk ekziston! Fillimisht nis monitorin.")
        return

    gen = RaportGenerator(db_path=args.db, reports_dir=args.out)
    raport, filename = gen.gjenero_dhe_ruaj(args.date)
    print("\n" + raport)
    print(f"\nRaporti u ruajt ne: {filename}\n")


if __name__ == "__main__":
    main()
