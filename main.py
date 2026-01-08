#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path

def shfaq_menu():
    os.system("clear")
    print("SI LOG EVENT MANAGER")
    print("\nMENUJA KRYESORE:\n")
    print("  1. Fillo Monitorimin e File-ve")
    print("  2. Gjenero Raport Ditor")
    print("  3. Shiko Statistika")
    print("  4. Fillo Scheduler Automatik")
    print("  5. Shiko Events Suspicious")
    print("  6. Fshi Databazen (Reset)")
    print("  0. Dil")
    print("\n")

def shiko_statistika(db_path="security.db"):
    if not os.path.exists(db_path):
        print("\nDatabaza nuk ekziston! Fillo monitorimin fillimisht.")
        input("\nEnter per te vazhduar...")
        return

    from src.database import SecurityDatabase
    db = SecurityDatabase(db_path)
    stats = db.statistika()

    print("\nSTATISTIKA\n")
    print(f"  Total Events:       {stats['total_events']}")
    print(f"  Suspicious Events:  {stats['suspicious_events']}")
    print(f"  Perdorues Aktive:   {stats['perdorues_aktive']}")
    input("\nEnter per te vazhduar...")

def shiko_suspicious(db_path="security.db"):
    if not os.path.exists(db_path):
        print("\nDatabaza nuk ekziston!")
        input("\nEnter per te vazhduar...")
        return

    from src.database import SecurityDatabase
    db = SecurityDatabase(db_path)
    suspicious = db.merr_suspicious_events(limit=200)

    print("\n⚠️  EVENTS SUSPICIOUS\n")
    if not suspicious:
        print("Nuk ka events suspicious!\n")
    else:
        print(f"Totali (show 10): {len(suspicious)} events\n")
        for i, event in enumerate(suspicious[:10], 1):
            event_id, data_ora, perdoruesi, veprimi, file_path, suspicious_flag = event
            print(f"{i}. [{data_ora}] {perdoruesi} - {veprimi}")
            print(f"   File: {file_path}\n")

    input("Enter per te vazhduar...")

def reset_databaza(db_path="security.db"):
    print("\n⚠️ KUJDES: Do te fshihen te gjitha te dhenat!")
    konfirmo = input("\nShkruaj 'PO' per te konfirmuar: ")
    if konfirmo.upper() == "PO":
        if os.path.exists(db_path):
            os.remove(db_path)
            print("\nDatabaza u fshi!")
        else:
            print("\nDatabaza nuk ekziston!")
    else:
        print("\nAnuluar!")
    input("\nEnter per te vazhduar...")

def main():
    while True:
        shfaq_menu()
        zgjedhja = input("Zgjidhni (0-6): ").strip()

        if zgjedhja == "1":
            path = input("Path per monitorim (default: current folder): ").strip() or str(Path.cwd())
            recursive = input("Recursive? (y/n, default y): ").strip().lower()
            rec_flag = "--recursive" if recursive in ("", "y", "yes") else ""
            cmd = ["python3", "-m", "src.monitor", "--path", path]
            if rec_flag:
                cmd.append(rec_flag)
            subprocess.run(cmd)

        elif zgjedhja == "2":
            subprocess.run(["python3", "-m", "src.raport"])

        elif zgjedhja == "3":
            shiko_statistika()

        elif zgjedhja == "4":
            subprocess.run(["python3", "-m", "src.scheduler"])

        elif zgjedhja == "5":
            shiko_suspicious()

        elif zgjedhja == "6":
            reset_databaza()

        elif zgjedhja == "0":
            print("Faleminderit!\n")
            break
        else:
            print("\nZgjedhje e pavlefshme!")
            input("\nEnter per te vazhduar...")

if __name__ == "__main__":
    main()
