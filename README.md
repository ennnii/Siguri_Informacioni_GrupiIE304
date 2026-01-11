# SI Log Event Manager (Linux)

Mini aplikacion Linux per **log event management** (monitorim file-sh + raport ditor).
Fokus: kush e prek nje file per here te pare (per ate user) shenohet si **suspicious**.

## Features
- Monitorim i file-ve (create/modify/delete/move) me `watchdog` (inotify ne Linux)
- Ruajtje ne SQLite (`security.db`)
- Raport ditor ne `reports/raport_YYYY-MM-DD.txt`
- Scheduler (kontroll suspicious + raport) me `schedule` (ose systemd timer)

## Instalimi
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run (CLI)
### 1) Monitor
```bash
python3 -m src.monitor --path /home/$USER --recursive
```

Opsione:
- `--db security.db`
- `--ignore .swp,.tmp,~,.log`
- `--log-file /var/log/si-monitor.log`
- `--verbose`

### 2) Raport ditor (manual)
```bash
python3 -m src.raport --db security.db --out reports
```

### 3) Scheduler (manual)
```bash
python3 -m src.scheduler --db security.db --out reports --check-minutes 10 --report-time 23:59
```

### 4) Menu app
```bash
python3 main.py
```

## Systemd (si Linux application)
shembuj te gatshem ne folderin `systemd/`.

### Monitor service
- Kopjo `systemd/si-monitor.service` ne `~/.config/systemd/user/`
```bash
mkdir -p ~/.config/systemd/user
cp systemd/si-monitor.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now si-monitor.service
systemctl --user status si-monitor.service
```

### Daily report timer
```bash
cp systemd/si-report.service ~/.config/systemd/user/
cp systemd/si-report.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now si-report.timer
systemctl --user list-timers | grep si-report
```

## Repo hygiene
- `venv/` nuk komitohet (eshte OS-specific + e rrit repo size)
- `reports/*.txt` nuk komitohen (mund te kene info reale)
- ruaj vetem `requirements.txt` dhe kodin
