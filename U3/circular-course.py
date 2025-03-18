#!/usr/bin/env python3
import sys
import json

def generate_tracks(num_tracks: int, length_of_track: int):
    """
    Erzeugt eine Datenstruktur mit 'num_tracks' Tracks,
    wobei JEDER Track folgende Sonder-Segmente enthält:
      - start-and-goal-t
      - 1 bottleneck-t (mit 2 unterschiedlichen Nachfolgern)
      - 1 caesar-t (wird von jedem Token genau einmal während des Rennens besucht)
    """
    all_tracks = []

    for t in range(1, num_tracks + 1):
        track_id = str(t)
        segments = []

        # 1) Start-and-goal segment
        start_segment = {
            "segmentId": f"start-and-goal-{t}",
            "type": "start-goal",
            "nextSegments": [f"segment-{t}-1"]
        }
        segments.append(start_segment)

        # Calculate segments distribution
        num_segments = length_of_track - 3
        pre_bottleneck = num_segments // 2

        # 2) Normal segments before bottleneck
        for i in range(1, pre_bottleneck + 1):
            segment = {
                "segmentId": f"segment-{t}-{i}",
                "type": "normal",
                "nextSegments": [f"segment-{t}-{i+1}" if i < pre_bottleneck else f"bottleneck-{t}"]
            }
            segments.append(segment)

        # 3) Bottleneck segment
        bottleneck = {
            "segmentId": f"bottleneck-{t}",
            "type": "bottleneck",
            # Two paths: to caesar or back to start
            "nextSegments": [f"segment-{t}-{pre_bottleneck+1}", f"start-and-goal-{t}"]
        }
        segments.append(bottleneck)

        # 4) Normal segments after bottleneck (path to Caesar)
        for i in range(pre_bottleneck + 1, num_segments + 1):
            segment = {
                "segmentId": f"segment-{t}-{i}",
                "type": "normal",
                "nextSegments": [f"caesar-{t}"]
            }
            segments.append(segment)

        # 5) Caesar segment
        caesar = {
            "segmentId": f"caesar-{t}",
            "type": "caesar",
            "nextSegments": [f"start-and-goal-{t}"]
        }
        segments.append(caesar)

        track = {
            "trackId": track_id,
            "segments": segments
        }
        all_tracks.append(track)

    return {"tracks": all_tracks}


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <num_tracks> <length_of_track> <output_file>")
        sys.exit(1)

    num_tracks = int(sys.argv[1])
    length_of_track = int(sys.argv[2])
    output_file = sys.argv[3]

    # ACHTUNG: Bei sehr kleinem length_of_track < 2 kann es sein, dass wir
    # nicht genügend Normal-Segmente haben. Hier ggf. anpassen oder Warnung ausgeben:
    if length_of_track < 2:
        print(f"Warnung: length_of_track={length_of_track} < 2 - die erzeugte Struktur enthält evtl. kaum Normal-Segmente.")

    tracks_data = generate_tracks(num_tracks, length_of_track)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tracks_data, f, indent=2)
        f.write('\n')
    print(f"Successfully generated {num_tracks} track(s) of length {length_of_track} into '{output_file}'")

if __name__ == "__main__":
    main()
