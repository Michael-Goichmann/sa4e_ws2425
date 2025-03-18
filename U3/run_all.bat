@echo off
REM ============================================================================
REM run_all.bat
REM ----------------------------------------------------------------------------
REM Usage: run_all.bat [NUM_TRACKS] [LENGTH_OF_TRACK] [NUM_RUNDEN] [NUM_STREITWAGEN]
REM ----------------------------------------------------------------------------
REM Standardwerte:
REM   NUM_TRACKS       = 1
REM   LENGTH_OF_TRACK  = 5
REM   NUM_RUNDEN       = 6
REM   NUM_STREITWAGEN  = 4
REM ----------------------------------------------------------------------------
REM Voraussetzungen:
REM  - Python (python.exe) im PATH
REM  - Docker, Docker Compose im PATH
REM  - circular-course.py und generate_architecture.py im selben Ordner
REM  - docker-compose.yml mit Kafka/ZooKeeper im selben Ordner
REM ============================================================================

SET NUM_TRACKS=%1
IF "%NUM_TRACKS%"=="" SET NUM_TRACKS=1

SET LENGTH_OF_TRACK=%2
IF "%LENGTH_OF_TRACK%"=="" SET LENGTH_OF_TRACK=5

SET NUM_RUNDEN=%3
IF "%NUM_RUNDEN%"=="" SET NUM_RUNDEN=6

SET NUM_STREITWAGEN=%4
IF "%NUM_STREITWAGEN%"=="" SET NUM_STREITWAGEN=4

SET TRACKS_JSON=tracks.json

REM NEU: Broker-Liste für 3-Broker-Cluster
SET KAFKA_BOOTSTRAP_SERVERS=localhost:9092,localhost:9093,localhost:9094

ECHO Starte Cluster mit 3 Kafka-Brokern => KAFKA_BOOTSTRAP_SERVERS=%KAFKA_BOOTSTRAP_SERVERS%
ECHO.

ECHO ============================================================================
ECHO Verwende folgende Einstellungen:
ECHO   NUM_TRACKS       = %NUM_TRACKS%
ECHO   LENGTH_OF_TRACK  = %LENGTH_OF_TRACK%
ECHO   NUM_RUNDEN       = %NUM_RUNDEN%
ECHO   NUM_STREITWAGEN  = %NUM_STREITWAGEN%
ECHO   TRACKS_JSON      = %TRACKS_JSON%
ECHO ============================================================================

REM 1) JSON-Streckenbeschreibung erzeugen
ECHO [1/5] Erzeuge JSON-Streckenbeschreibung...
python circular-course.py %NUM_TRACKS% %LENGTH_OF_TRACK% %TRACKS_JSON%
IF ERRORLEVEL 1 (
    ECHO Fehler beim Erzeugen der JSON
    EXIT /B 1
)

REM 2) Segment-Skripte generieren
ECHO [2/5] Generiere Segment-Skripte...
python generate_architecture.py %TRACKS_JSON%
IF ERRORLEVEL 1 (
    ECHO Fehler beim Generieren der Segment-Skripte
    EXIT /B 1
)

REM 3) Kafka starten
ECHO [3/5] Starte Kafka per Docker-Compose...
docker-compose up -d
IF ERRORLEVEL 1 (
    ECHO Fehler beim Starten von Kafka
    EXIT /B 1
)

REM 4) Kurze Wartezeit, damit Kafka vollständig hochfährt
ECHO [4/5] Warte 10 Sekunden, damit Kafka stabil läuft...
powershell -Command "Start-Sleep -Seconds 10"

REM 5) Segmente starten
ECHO [5/5] Starte Segmente im Hintergrund...
PUSHD generated_segments

REM Erst alle "normalen" segment-*.py im Hintergrund starten
FOR %%F IN (segment-*.py) DO (
    ECHO Starte %%F ...
    START "Segment %%F" /B python %%F
)

REM 5b) Alle start-and-goal-*.py im Vordergrund starten
FOR %%F IN (start-and-goal-*.py) DO (
    ECHO Starte %%F [Start-Goal] mit %NUM_RUNDEN% Runden und %NUM_STREITWAGEN% Streitwagen...
    python %%F %NUM_RUNDEN% %NUM_STREITWAGEN%
)

POPD

ECHO ============================================================================
ECHO Alle Prozesse wurden gestartet.
ECHO - Docker-Container (Kafka/ZooKeeper) laufen im Hintergrund.
ECHO - Segment-Prozesse wurden im Hintergrund gestartet (START /B).
ECHO ============================================================================
EXIT /B 0
