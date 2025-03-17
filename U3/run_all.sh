#!/usr/bin/env bash
#
# Script zum Erzeugen der JSON-Streckenbeschreibung,
# Generieren der Segment-Skripte,
# Starten von Kafka und schließlich Starten aller Segmente.
#
# Voraussetzung:
#  - circular-course.py und generate_architecture.py liegen im selben Ordner
#  - docker-compose.yml mit Kafka/ ZooKeeper liegt im selben Ordner
#  - python3, docker und docker-compose sind installiert
#  - Alle Python-Abhängigkeiten für die Kafka-Python-Clients sind vorhanden
#    (z.B. "pip install kafka-python")

###############################################################################
# 1) Parameter und Default-Werte
###############################################################################

# Anzahl Tracks (Rundkurse)
NUM_TRACKS=${1:-2}
# Anzahl Segmente pro Track
LENGTH_OF_TRACK=${5:-3}
# Anzahl Runden für Start-and-Goal-Segmente
NUM_RUNDEN=${6:-5}
# Anzahl zu startender Streitwagen pro Start-and-Goal
NUM_STREITWAGEN=${4:-2}
# Ausgabedatei für JSON
TRACKS_JSON="tracks.json"

echo "Verwende folgende Einstellungen:"
echo "  NUM_TRACKS         = $NUM_TRACKS"
echo "  LENGTH_OF_TRACK    = $LENGTH_OF_TRACK"
echo "  NUM_RUNDEN         = $NUM_RUNDEN"
echo "  NUM_STREITWAGEN    = $NUM_STREITWAGEN"
echo "  TRACKS_JSON        = $TRACKS_JSON"
echo "----------------------------------------------------------------------------"

###############################################################################
# 2) JSON-Streckenbeschreibung erzeugen
###############################################################################
echo ">> Erzeuge JSON-Streckenbeschreibung via circular-course.py..."
python3 circular-course.py "$NUM_TRACKS" "$LENGTH_OF_TRACK" "$TRACKS_JSON"
if [ $? -ne 0 ]; then
  echo "Fehler beim Erzeugen der Strecken-JSON."
  exit 1
fi
echo "----------------------------------------------------------------------------"

###############################################################################
# 3) Segment-Skripte generieren
###############################################################################
echo ">> Generiere Segment-Skripte in Ordner 'generated_segments'..."
python3 generate_architecture.py "$TRACKS_JSON"
if [ $? -ne 0 ]; then
  echo "Fehler beim Generieren der Segment-Skripte."
  exit 1
fi
echo "----------------------------------------------------------------------------"

###############################################################################
# 4) Kafka starten
###############################################################################
echo ">> Starte Kafka via docker-compose..."
docker-compose up -d
if [ $? -ne 0 ]; then
  echo "Fehler beim Starten von Kafka über docker-compose."
  exit 1
fi

# Optional: kurze Wartezeit, damit Kafka vollständig hochfährt
echo "Warte 10 Sekunden, damit Kafka/ Zookeeper hochfahren..."
sleep 10
echo "----------------------------------------------------------------------------"

###############################################################################
# 5) Starten der generierten Segmente
###############################################################################
# Wir starten die Segmente in der Regel im Hintergrund (&).
# Du kannst aber auch in verschiedenen Terminals starten, je nach Bedarf.

echo ">> Starte Segment-Skripte..."

cd generated_segments || exit 1

# Zuerst alle "normal" Segmente im Hintergrund starten
# (Sinnvoll: filtern nach 'segment-*' um Start-and-Goal zu unterscheiden)
for seg_file in segment-*.py; do
    echo "Starte $seg_file im Hintergrund..."
    python3 "$seg_file" &
done

# Dann die Start-and-Goal-Segmente starten
# (Sie erfordern CLI-Parameter: <Runden> <Anzahl_Tokens>)
for sng_file in start-and-goal-*.py; do
    echo "Starte $sng_file mit $NUM_RUNDEN Runden und $NUM_STREITWAGEN Streitwagen..."
    python3 "$sng_file" "$NUM_RUNDEN" "$NUM_STREITWAGEN" &
done

# Hinweis:
# - Wir starten hier alles im Hintergrund. So bleibt das Skript nicht hängen.
# - Willst du auf die Ausgabe warten, müsstest du "fg" benutzen oder
#   die Prozesse einzeln starten.

echo "----------------------------------------------------------------------------"
echo "Alle Prozesse wurden gestartet."
echo "Logs liegen auf der Konsole (wenn du docker logs <kafka> usw. checken möchtest)."
echo "Die Segment-Skripte laufen im Hintergrund. Du kannst sie mit 'jobs' oder 'ps' einsehen."
