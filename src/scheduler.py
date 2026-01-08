#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import schedule
import time
from datetime import datetime

from src.raport import RaportGenerator
from src.database import SecurityDatabase


class AlertSystem:
    def __init__(self, admin_email: str = "admin@example.com"):
        self.admin_email = admin_email

    def dergo_alarm_console(self, subjekti: str, mesazhi: str) -> None:
        print("\n" + "=" * 70)
        print("EMAIL ALERT (SIMULIM - console)")
        print(f"Per:      {self.admin_email}")
        print(f"Subjekti: {subjekti}")
        print("-" * 70)
        print(mesazhi)
        print("=" * 70 + "\n")

    def dergo_alarm_suspicious(self, events) -> None:
        if not events:
            return

        subjekti = f"LARM SIGURIE - {len(events)} aktivitete suspicious"
        mesazhi = f"""U gjeten {len(events)} aktivitete suspicious.

Detaje (max 5):
"""

        for event in events[:5]:
            event_id, data_ora, perdoruesi, veprimi, file_path, suspicious = event
            mesazhi += f"""- [{data_ora}] user={perdoruesi} action={veprimi}
  file={file_path}

"""

        if len(events) > 5:
            mesazhi += f"... dhe {len(events) - 5} aktivitete te tjera.\n\n"

        mesazhi += "Ju lutem kontrolloni keto aktivitete sa me shpejt.\n"
        self.dergo_alarm_console(subjekti, mesazhi)


class Scheduler:
    def __init__(self, db_path: str, reports_dir: str, admin_email: str):
        self.db = SecurityDatabase(db_path)
        self.generator = RaportGenerator(db_path=db_path, reports_dir=reports_dir)
        self.alert_system = AlertSystem(admin_email=admin_email)

    def kontrollo_suspicious_events(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Kontrollim suspicious...")
        suspicious = self.db.merr_suspicious_events(limit=200)
        if suspicious:
            print(f"  ⚠️  U gjeten {len(suspicious)} suspicious events")
            self.alert_system.dergo_alarm_suspicious(suspicious)
        else:
            print("  ✅ Nuk ka suspicious events")

    def gjenero_raport_ditor(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Gjenerim raporti ditor...")
        data = datetime.now().strftime("%Y-%m-%d")
        raport, filename = self.generator.gjenero_dhe_ruaj(data)
        subjekti = f"Raporti Ditor i Sigurise - {data}"
        self.alert_system.dergo_alarm_console(subjekti, raport)
        print(f"  ✓ Raporti u ruajt ne: {filename}")

    def setup_schedule(self, report_time: str, check_minutes: int):
        schedule.every().day.at(report_time).do(self.gjenero_raport_ditor)
        schedule.every(check_minutes).minutes.do(self.kontrollo_suspicious_events)

        print("\nDetyrat:")
        for job in schedule.get_jobs():
            print(f"  • {job}")
        print("\nCtrl+C per me ndalu\n")

    def run(self):
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler u ndal.\n")


def parse_args():
    ap = argparse.ArgumentParser(description="Scheduler per raport + alerts")
    ap.add_argument("--db", default="security.db", help="Rruga e databazes")
    ap.add_argument("--out", default="reports", help="Folder per raportet")
    ap.add_argument("--admin-email", default="admin@example.com", help="Email admin (vetem per console)")
    ap.add_argument("--report-time", default="23:59", help="Ora e raportit (HH:MM)")
    ap.add_argument("--check-minutes", type=int, default=10, help="Sa minuta midis kontrollimeve suspicious")
    return ap.parse_args()


def main():
    args = parse_args()
    if not os.path.exists(args.db):
        print(f"ERROR: Databaza '{args.db}' nuk ekziston! Fillimisht nis monitorin.")
        return

    s = Scheduler(db_path=args.db, reports_dir=args.out, admin_email=args.admin_email)
    s.setup_schedule(report_time=args.report_time, check_minutes=args.check_minutes)
    s.run()


if __name__ == "__main__":
    main()
