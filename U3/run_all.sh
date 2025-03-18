#!/usr/bin/env bash
################################################################################
# run_all.sh
# ------------------------------------------------------------------------------
# Usage: ./run_all.sh [NUM_TRACKS] [LENGTH_OF_TRACK] [NUM_RUNDEN] [NUM_STREITWAGEN]
# ------------------------------------------------------------------------------
# Standardwerte (falls Parameter fehlen):
#   NUM_TRACKS       = 1
#   LENGTH_OF_TRACK  = 5
#   NUM_RUNDEN       = 6
#   NUM_STREITWAGEN  = 4
# ------------------------------------------------------------------------------
# Voraussetzungen:
#  - Python (python3) im PATH
#  - Docker, Docker Compose im PATH
#  - circular-course.py und generate_architecture.py im selben Ordner
#  - docker-compose.yml mit Kafka/ZooKeeper im selben Ordner
################################################################################

# 1) Argumente einlesen und ggf. Standardwerte setzen
NUM_TRACKS="${1:-1}"
LENGTH_OF_TRACK="${2:-5}"
NUM_RUNDEN="${3:-6}"
NUM_STREITWAGEN="${4:-4}"

TRACKS_JSON="tracks.json"

# 2) Broker-Liste für 3-Broker-Cluster (Umgebungsvariable)
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092,localhost:9093,localhost:9094"

echo "Starte Cluster mit 3 Kafka-Brokern => KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}"
echo

echo "==============================================================================="
echo "Verwende folgende Einstellungen:"
echo "  NUM_TRACKS       = ${NUM_TRACKS}"
echo "  LENGTH_OF_TRACK  = ${LENGTH_OF_TRACK}"
echo "  NUM_RUNDEN       = ${NUM_RUNDEN}"
echo "  NUM_STREITWAGEN  = ${NUM_STREITWAGEN}"
echo "  TRACKS_JSON      = ${TRACKS_JSON}"
echo "==============================================================================="

# 3) JSON-Streckenbeschreibung erzeugen
echo "[1/5] Erzeuge JSON-Streckenbeschreibung..."
python3 circular-course.py "${NUM_TRACKS}" "${LENGTH_OF_TRACK}" "${TRACKS_JSON}"
if [ $? -ne 0 ]; then
    echo "Fehler beim Erzeugen der JSON"
    exit 1
fi

# 4) Segment-Skripte generieren
echo "[2/5] Generiere Segment-Skripte..."
python3 generate_architecture.py "${TRACKS_JSON}"
if [ $? -ne 0 ]; then
    echo "Fehler beim Generieren der Segment-Skripte"
    exit 1
fi

# 5) Kafka starten
echo "[3/5] Starte Kafka per Docker-Compose..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Fehler beim Starten von Kafka"
    exit 1
fi

# 6) Kurze Wartezeit, damit Kafka vollständig hochfährt
echo "[4/5] Warte 10 Sekunden, damit Kafka stabil funktioniert..."
sleep 10

# 7) Segmente starten
echo "[5/5] Starte Segmente..."

pushd generated_segments >/dev/null 2>&1

# Erst alle "bottleneck-*.py" im Hintergrund starten
for f in bottleneck-*.py; do
    if [ -f "$f" ]; then
        echo "Starte $f (Bottleneck) ..."
        python3 "$f" &
    fi
done

# Dann alle "caesar-*.py" im Hintergrund starten
for f in caesar-*.py; do
    if [ -f "$f" ]; then
        echo "Starte $f (Caesar) ..."
        python3 "$f" &
    fi
done

# Dann alle "segment-*.py" im Hintergrund starten
for f in segment-*.py; do
    if [ -f "$f" ]; then
        echo "Starte $f (Normal) ..."
        python3 "$f" &
    fi
done

# Zum Schluss: start-and-goal-*.py mit CLI-Parametern (im Vordergrund),
# damit du die Ausgabe direkt im Terminal siehst
for f in start-and-goal-*.py; do
    if [ -f "$f" ]; then
        echo "Starte $f [Start-Goal] mit ${NUM_RUNDEN} Runden und ${NUM_STREITWAGEN} Streitwagen..."
        python3 "$f" "${NUM_RUNDEN}" "${NUM_STREITWAGEN}"
    fi
done

popd >/dev/null 2>&1

echo "==============================================================================="
echo "Alle Prozesse wurden gestartet."
echo "- Docker-Container (Kafka/ZooKeeper) laufen im Hintergrund."
echo "- Segment-Prozesse (Bottleneck/Caesar/Normal) wurden im Hintergrund gestartet (&)."
echo "  Start-and-Goal-Segmente liefen im Vordergrund, um ihre Ausgabe anzuzeigen."
echo "==============================================================================="

exit 0
