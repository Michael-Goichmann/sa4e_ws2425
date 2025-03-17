#!/usr/bin/env python3
import json
import sys
import os

START_GOAL_TEMPLATE = r'''#!/usr/bin/env python3
"""
Automatisch erzeugt für: {segment_id}
Track: {track_id}
Dieses Segment startet Tokens (Streitwagen) und misst deren Runden.
"""

import time
import json
import sys
from kafka import KafkaConsumer, KafkaProducer

def main():
    # Argumente: rundenanzahl, anzahl_tokens
    if len(sys.argv) < 3:
        print("Usage: python {seg_id}.py <runden> <anzahl_tokens>")
        sys.exit(1)

    max_runden = int(sys.argv[1])
    anzahl_tokens = int(sys.argv[2])

    # Kafka Setup
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    consumer = KafkaConsumer(
        '{input_topic}',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='{segment_id}-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    # Dictionaries
    startzeiten = {{}}
    rundenzaehler = {{}}

    # Tokens erzeugen (z.B. wagen_1 ... wagen_n)
    for i in range(1, anzahl_tokens+1):
        token_id = "wagen_" + str(i)
        startzeiten[token_id] = time.time()
        rundenzaehler[token_id] = 0

        msg = {{
            "token_id": token_id,
            "runden": 0
        }}
        producer.send('{output_topic}', msg)
    print("Start-and-goal-Segment {{segment_id}} hat {{anzahl_tokens}} Tokens ins Rennen geschickt."
      .format(segment_id='{segment_id}', anzahl_tokens=anzahl_tokens))


    # Token-Verarbeitung
    while True:
        for message in consumer:
            data = message.value
            token_id = data["token_id"]
            aktuelle_runde = data["runden"]

            neue_runde = aktuelle_runde + 1
            rundenzaehler[token_id] = neue_runde

            if neue_runde >= max_runden:
                # Ziel erreicht
                endzeit = time.time()
                laufzeit = endzeit - startzeiten[token_id]
                print("Streitwagen {{}} hat sein Ziel erreicht! Runden: {{}}, Laufzeit: {{:.3f}}s"
                      .format(token_id, max_runden, laufzeit))
                del startzeiten[token_id]
                del rundenzaehler[token_id]

                if len(rundenzaehler) == 0:
                    print("Rennen beendet für alle Streitwagen.")
                    return
            else:
                # Nächste Runde
                msg = {{
                    "token_id": token_id,
                    "runden": neue_runde
                }}
                producer.send('{output_topic}', msg)

if __name__ == "__main__":
    main()
'''

NORMAL_TEMPLATE = r'''#!/usr/bin/env python3
"""
Automatisch erzeugt für: {segment_id}
Track: {track_id}
Dieses Segment leitet Tokens nur weiter.
"""

import json
from kafka import KafkaConsumer, KafkaProducer

def main():
    consumer = KafkaConsumer(
        '{input_topic}',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='{segment_id}-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    print(f"Segment '{segment_id}' lauscht auf Topic '{input_topic}' und leitet weiter an '{output_topic}'.")
    for message in consumer:
        data = message.value
        # Token direkt weiterleiten
        producer.send('{output_topic}', data)

if __name__ == "__main__":
    main()
'''


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <tracks_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Datei {json_file} nicht gefunden!")
        sys.exit(1)

    # JSON laden
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verzeichnis für generierte Dateien erstellen
    out_dir = "generated_segments"
    os.makedirs(out_dir, exist_ok=True)

    # Für jeden Track und jedes Segment eine Python-Datei anlegen
    tracks = data["tracks"]
    for track in tracks:
        track_id = track["trackId"]
        segments = track["segments"]
        for seg in segments:
            segment_id = seg["segmentId"]
            seg_type = seg["type"]
            next_segments = seg["nextSegments"]

            # Für Einfachheit nehmen wir an, dass es hier immer GENAU EIN nächstes Segment gibt
            # (Das Script generiert maximal 1 Eintrag in nextSegments in dieser Aufgabe.)
            # In komplexeren Fällen müsste man ggf. mehrere Topics ansteuern.
            output_topic = ""
            if len(next_segments) == 1:
                output_topic = next_segments[0] + "-in"
            else:
                # Sammel-Topic? Für Demo hier nicht weiter vertieft
                output_topic = "multi-output-topic"

            input_topic = segment_id + "-in"

            if seg_type == "start-goal":
                template_filled = START_GOAL_TEMPLATE.format(
                    segment_id=segment_id,
                    track_id=track_id,
                    input_topic=input_topic,
                    output_topic=output_topic,
                    seg_id=segment_id,
                )
            else:
                template_filled = NORMAL_TEMPLATE.format(
                    segment_id=segment_id,
                    track_id=track_id,
                    input_topic=input_topic,
                    output_topic=output_topic,
                )

            # Python-Datei schreiben
            filename = f"{segment_id}.py"
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "w", encoding="utf-8") as sf:
                sf.write(template_filled)
            # Ausführbar machen (optional, Linux/Mac)
            os.chmod(filepath, 0o755)

    print(f"Fertig! Segment-Skripte wurden in '{out_dir}' erzeugt.")


if __name__ == "__main__":
    main()