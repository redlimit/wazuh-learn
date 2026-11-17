#!/usr/bin/env python3
"""Custom integration Wazuh untuk mengirim alert ke Telegram.

Dipanggil lewat wrapper custom-telegram oleh modul Integrator.

Argumen:
    sys.argv[1]  path file alert JSON yang ditulis Integrator
    sys.argv[2]  nilai <api_key> di blok <integration>, dipakai sebagai chat ID
    sys.argv[3]  nilai <hook_url> di blok <integration>, URL endpoint sendMessage

Hanya memakai standard library supaya tidak bergantung pada paket tambahan.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

WAZUH_PATH = os.environ.get("WAZUH_PATH", "/var/ossec")
LOG_FILE = os.path.join(WAZUH_PATH, "logs", "integrations.log")
TIMEOUT = 10
MAX_LOG_CHARS = 700


def log(message):
    stamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    line = "{} custom-telegram: {}\n".format(stamp, message)
    try:
        with open(LOG_FILE, "a") as handle:
            handle.write(line)
    except OSError:
        sys.stderr.write(line)


def read_alert(path):
    with open(path) as handle:
        return json.load(handle)


def build_message(alert):
    rule = alert.get("rule", {})
    agent = alert.get("agent", {})

    lines = [
        "Wazuh alert",
        "Level: {}".format(rule.get("level", "-")),
        "Rule: {} ({})".format(rule.get("description", "-"), rule.get("id", "-")),
        "Agent: {} ({})".format(agent.get("name", "-"), agent.get("id", "-")),
        "Waktu: {}".format(alert.get("timestamp", "-")),
        "Lokasi: {}".format(alert.get("location", "-")),
    ]

    groups = rule.get("groups")
    if groups:
        lines.append("Groups: {}".format(", ".join(groups)))

    mitre = rule.get("mitre", {}).get("id")
    if mitre:
        lines.append("MITRE: {}".format(", ".join(mitre)))

    full_log = alert.get("full_log")
    if full_log:
        trimmed = full_log[:MAX_LOG_CHARS]
        if len(full_log) > MAX_LOG_CHARS:
            trimmed += " [dipotong]"
        lines.append("")
        lines.append(trimmed)

    return "\n".join(lines)


def send(hook_url, chat_id, text):
    payload = json.dumps(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    ).encode("utf-8")

    request = urllib.request.Request(
        hook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.getcode(), response.read().decode("utf-8", "replace")


def main():
    if len(sys.argv) < 4:
        log("ERROR - argumen tidak lengkap, butuh alert_file, api_key, hook_url")
        return 1

    alert_file, chat_id, hook_url = sys.argv[1], sys.argv[2], sys.argv[3]

    if not chat_id or not hook_url:
        log("ERROR - api_key (chat ID) atau hook_url kosong")
        return 1

    try:
        alert = read_alert(alert_file)
    except (OSError, ValueError) as error:
        log("ERROR - gagal membaca file alert {}: {}".format(alert_file, error))
        return 1

    text = build_message(alert)

    try:
        status, body = send(hook_url, chat_id, text)
    except urllib.error.HTTPError as error:
        log(
            "ERROR - Telegram menolak request, HTTP {}: {}".format(
                error.code, error.read().decode("utf-8", "replace")
            )
        )
        return 1
    except (urllib.error.URLError, OSError) as error:
        log("ERROR - gagal menghubungi Telegram: {}".format(error))
        return 1

    if status != 200:
        log("ERROR - Telegram menjawab HTTP {}: {}".format(status, body))
        return 1

    rule_id = alert.get("rule", {}).get("id", "-")
    log("INFO - alert rule {} terkirim ke chat {}".format(rule_id, chat_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
