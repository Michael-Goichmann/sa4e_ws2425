#!/usr/bin/env python3

import os
import json
import requests
import datetime

# Pfad zu einer Datei, in der wir uns merken, bis wann wir Daten abgefragt haben
LAST_SYNC_FILE = "/home/nordpol/sync_nordpol_last.json"

# Regionale Endpoints
REGIONS = [
    {
        "name": "EU",
        "url": "http://192.168.56.10:5001/wishes/sync" 
        # oder je nachdem, wie dein EU-Service-Endpoint lautet
    },
    {
        "name": "NA",
        "url": "http://192.168.56.10:5002/wishes/sync"
    }
    # etc.
]

# Nordpol-Endpunkt
NORDPOL_URL = "http://192.168.56.10:5003/wishes"  # "POST" hier

def load_last_sync():
    """Lädt den letzten Sync-Zeitstempel aus einer JSON-Datei."""
    if not os.path.exists(LAST_SYNC_FILE):
        return None
    with open(LAST_SYNC_FILE, "r") as f:
        data = json.load(f)
        return data.get("lastSync")

def save_last_sync(timestamp_str):
    """Schreibt den neuen Sync-Zeitstempel in die Datei."""
    with open(LAST_SYNC_FILE, "w") as f:
        json.dump({"lastSync": timestamp_str}, f)

def main():
    # 1) Letzten Zeitstempel laden
    last_sync = load_last_sync()
    if last_sync:
        print(f"Last sync: {last_sync}")
    else:
        print("No previous sync found. Will fetch everything.")
    
    # Falls kein Timestamp vorhanden -> hole alles, oder nimm Startdatum
    # parse Datum in ISO-Format
    if last_sync is None:
        last_sync_iso = None
    else:
        last_sync_iso = last_sync  # wir gehen davon aus, es ist ein ISO-String

    # 2) Für jede Region: GET /wishes/sync?updatedAfter=<timestamp>
    new_wishes_count = 0

    for region in REGIONS:
        params = {}
        if last_sync_iso:
            params["updatedAfter"] = last_sync_iso
        
        print(f"Fetching from region {region['name']} at {region['url']} with params={params}")
        try:
            response = requests.get(region["url"], params=params, timeout=10)
            response.raise_for_status()  # wirft Fehler, wenn 4xx/5xx
            wishes_list = response.json()  # Liste von Wish-Objekten
        except Exception as e:
            print(f"Error fetching from {region['name']}: {e}")
            continue
        
        print(f" -> Received {len(wishes_list)} new/updated wishes from {region['name']}")
        new_wishes_count += len(wishes_list)

        # 3) POST jeden Wish an den Nordpol oder in Bulk
        for wish in wishes_list:
            try:
                # Nordpol speichert
                # Wir nehmen an: Nordpol hat POST /wishes
                np_resp = requests.post(NORDPOL_URL, json=wish, timeout=5)
                # np_resp.raise_for_status() # optional, wenn wir strict sein wollen
            except Exception as e:
                print(f" Error posting wish to Nordpol: {e}")

    # 4) "lastSync" auf jetzt setzen, z.B. current UTC time
    new_sync_time = datetime.datetime.utcnow().isoformat()
    save_last_sync(new_sync_time)

    print(f"Synced {new_wishes_count} wishes. Updated lastSync to {new_sync_time}.")

if __name__ == "__main__":
    main()
