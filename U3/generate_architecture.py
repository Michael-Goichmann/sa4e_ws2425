#!/usr/bin/env python3
import json
import sys
import os

START_GOAL_TEMPLATE = r'''#!/usr/bin/env python3
"""
Automatically generated for: {segment_id}
Track: {track_id}
This segment starts tokens (chariots) and measures their rounds.
"""

import time
import json
import sys
import os
from kafka import KafkaConsumer, KafkaProducer

def main():
    # Dynamic broker list via environment variable
    BROKER_LIST = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")

    # Arguments: num_rounds, num_tokens
    if len(sys.argv) < 3:
        print("Usage: python {{seg_id}}.py <rounds> <num_tokens>")
        sys.exit(1)

    max_runden = int(sys.argv[1])
    anzahl_tokens = int(sys.argv[2])

    # Kafka Setup
    producer = KafkaProducer(
        bootstrap_servers=BROKER_LIST,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    consumer = KafkaConsumer(
        '{input_topic}',
        bootstrap_servers=BROKER_LIST,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='{segment_id}-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    # Dictionaries
    startzeiten = {{}}  # start times
    rundenzaehler = {{}}  # round counter
    processed_messages = set()

    # Generate tokens
    segment_id = "{segment_id}"
    output_topic = "{output_topic}"  # Define output_topic variable explicitly
    
    for i in range(1, anzahl_tokens+1):
        token_id = "wagen_" + str(i)
        startzeiten[token_id] = time.time()
        rundenzaehler[token_id] = 0

        msg = {{
            "token_id": token_id,
            "runden": 0
        }}
        producer.send(output_topic, msg)
        producer.flush()
        print(f"[{{segment_id}}] Token {{token_id}} started -> {{output_topic}}")

    print("Start-and-goal-Segment '{{}}' has {{}} tokens in the race."
          .format(segment_id, anzahl_tokens))

    # Token processing
    while True:
        try:
            for message in consumer:
                data = message.value
                token_id = data["token_id"]
                aktuelle_runde = data["runden"]
                
                msg_id = f"{{token_id}}-{{aktuelle_runde}}"
                
                if msg_id in processed_messages:
                    continue
                    
                processed_messages.add(msg_id)
                
                if token_id not in startzeiten:
                    continue

                neue_runde = aktuelle_runde + 1
                rundenzaehler[token_id] = neue_runde

                if neue_runde >= max_runden:
                    try:
                        endzeit = time.time()
                        laufzeit = endzeit - startzeiten[token_id]
                        print("Chariot {{}} has reached its goal! Rounds: {{}}, Runtime: {{:.3f}}s"
                              .format(token_id, max_runden, laufzeit))
                    finally:
                        if token_id in startzeiten:
                            del startzeiten[token_id]
                        if token_id in rundenzaehler:
                            del rundenzaehler[token_id]

                    if len(rundenzaehler) == 0:
                        print("Race finished for all chariots.")
                        producer.flush()
                        return
                else:
                    msg = {{
                        "token_id": token_id,
                        "runden": neue_runde
                    }}
                    producer.send('{output_topic}', msg)
                
                if len(processed_messages) > 1000:
                    processed_messages.clear()

        except KeyboardInterrupt:
            print("Program is being terminated...")
            break
        except Exception as e:
            print(f"Error: {{e}}")
            continue

    producer.flush()
    producer.close()
    consumer.close()

if __name__ == "__main__":
    main()
'''
NORMAL_TEMPLATE = r'''#!/usr/bin/env python3
"""
Automatically generated for: {segment_id}
Track: {track_id}
This segment only forwards tokens.
"""

import json
import os
import time
from kafka import KafkaConsumer, KafkaProducer

def main():
    segment_id = "{segment_id}"
    input_topic = "{input_topic}"
    output_topic = "{output_topic}"
    group_id = segment_id + '-group-' + str(time.time())
    
    # Dynamic broker list via environment variable
    BROKER_LIST = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")

    # Message tracking to avoid duplicates
    processed_messages = set()

    consumer = KafkaConsumer(
        input_topic,
        bootstrap_servers=BROKER_LIST,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=BROKER_LIST,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        print("Segment '{{}}' listening on Topic '{{}}' and forwarding to '{{}}'."
              .format(segment_id, input_topic, output_topic))
        for message in consumer:
            data = message.value
            # Create a unique message identifier
            token_id = data['token_id']
            runden = data['runden']
            msg_id = f"{{token_id}}-{{runden}}"
            
            # Skip if we've already processed this message
            if msg_id in processed_messages:
                continue
                
            processed_messages.add(msg_id)
            producer.send(output_topic, data)
            producer.flush()
            
            # Cleanup old messages from set (keep only last 1000)
            if len(processed_messages) > 1000:
                processed_messages.clear()
    except KeyboardInterrupt:
        print("Program is being terminated...")
    finally:
        producer.close()
        consumer.close()

if __name__ == "__main__":
    main()
'''

CAESAR_TEMPLATE = r'''#!/usr/bin/env python3
"""
Automatically generated for: {segment_id}
Track: {track_id}
This segment represents a meeting with Caesar.
"""

import json
import os
import time
import random
from kafka import KafkaConsumer, KafkaProducer
from threading import Lock

def main():
    segment_id = "{segment_id}"
    # Input topics as list:
    input_topics = {input_topics}
    # Output topics as list (can contain 1 or more):
    output_topics = {output_topics}
    group_id = segment_id + '-group-' + str(time.time())

    BROKER_LIST = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")

    consumer = KafkaConsumer(
        *input_topics,
        bootstrap_servers=BROKER_LIST,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=BROKER_LIST,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Caesar-Segment '{{}}' listening on {{}} and forwarding to {{}}."
          .format(segment_id, input_topics, output_topics))

    processed_messages = set()

    try:
        for message in consumer:
            data = message.value
            token_id = data.get("token_id")
            runden = data.get("runden", 0)

            # Create unique message ID
            msg_id = "{{}}-{{}}".format(token_id, runden)
            if msg_id in processed_messages:
                continue
            processed_messages.add(msg_id)

            # Only process tokens that are trying to visit Caesar
            if not data.get("try_caesar", False):
                continue

            print("[Caesar] welcoming Chariot '{{}}' in Segment '{{}}'. (round={{}})"
                  .format(token_id, segment_id, runden))
            
            data["caesar_visited"] = True
            data["try_caesar"] = False
            
            producer.send(output_topics[0], data)
            producer.flush()

            if len(processed_messages) > 1000:
                processed_messages.clear()

    except KeyboardInterrupt:
        print("Caesar-Segment '{{}}' shutting down...".format(segment_id))
    finally:
        producer.close()
        consumer.close()

if __name__ == "__main__":
    main()
'''

BOTTLENECK_TEMPLATE = r'''#!/usr/bin/env python3
"""
Automatically generated for: {segment_id}
Track: {track_id}
Bottleneck segment: Token must wait for random time before continuing.
"""

import json
import os
import time
import random
from kafka import KafkaConsumer, KafkaProducer
from threading import Lock

def main():
    segment_id = "{segment_id}"
    input_topics = {input_topics}
    output_topics = {output_topics}
    group_id = segment_id + '-group-' + str(time.time())

    BROKER_LIST = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")

    consumer = KafkaConsumer(
        *input_topics,
        bootstrap_servers=BROKER_LIST,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=BROKER_LIST,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Bottleneck-Segment '{{}}' listening on {{}} and forwarding to {{}}. Random wait time!"
          .format(segment_id, input_topics, output_topics))

    # Lock for synchronizing access to shared state
    bottleneck_lock = Lock()
    processed_messages = set()
    
    # Track Caesar visits
    caesar_visited = set()  # Tokens that have visited Caesar in the entire race
    current_round_visitors = {{}}  # Dictionary to track which token visited Caesar in each round
    
    try:
        for message in consumer:
            data = message.value
            token_id = data.get("token_id")
            runden = data.get("runden", 0)
            has_visited_caesar = data.get("caesar_visited", False)

            # Create unique message ID to avoid duplicates
            msg_id = "{{}}-{{}}".format(token_id, runden)
            if msg_id in processed_messages:
                continue
            processed_messages.add(msg_id)

            with bottleneck_lock:
                delay = random.uniform(1.0, 2.0)
                print("[Bottleneck] Chariot '{{}}' blocking segment '{{}}' for {{:.1f}}s"
                      .format(token_id, segment_id, delay))
                time.sleep(delay)

                # Check if any token has visited Caesar in this round
                round_has_visitor = runden in current_round_visitors
                
                # Send to Caesar if:
                # 1. This token hasn't visited Caesar before in the race
                # 2. No token has visited Caesar in this round yet
                if (not has_visited_caesar and 
                    token_id not in caesar_visited and 
                    not round_has_visitor):
                    
                    # Mark this token as visiting Caesar in this round
                    current_round_visitors[runden] = token_id
                    caesar_visited.add(token_id)
                    
                    # Set flag for Caesar segment to process
                    data["try_caesar"] = True
                    
                    # Send to Caesar path
                    producer.send(output_topics[0], data)
                else:
                    # Token doesn't qualify to visit Caesar, send to direct path
                    data["try_caesar"] = False
                    producer.send(output_topics[1], data)

            producer.flush()

            # Cleanup old messages periodically
            if len(processed_messages) > 1000:
                processed_messages.clear()
                
                # Also cleanup old round data (keep only recent rounds)
                current_round_visitors = {{k: v for k, v in current_round_visitors.items() 
                                       if k >= runden - 2}}

    except KeyboardInterrupt:
        print("Bottleneck-Segment '{{}}' shutting down...".format(segment_id))
    finally:
        producer.close()
        consumer.close()

if __name__ == "__main__":
    main()
'''



def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <tracks_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"File {json_file} not found!")
        sys.exit(1)

    # Load JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create directory for generated files
    out_dir = "generated_segments"
    os.makedirs(out_dir, exist_ok=True)

    # Create a Python file for each track and segment
    tracks = data["tracks"]
    for track in tracks:
        track_id = track["trackId"]
        segments = track["segments"]
        for seg in segments:
            segment_id = seg["segmentId"]
            seg_type = seg["type"]
            next_segments = seg["nextSegments"]

            # For simplicity we assume: EXACTLY ONE next segment
            if len(next_segments) == 1:
                output_topic = next_segments[0] + "-in"
            else:
                output_topic = "multi-output-topic"

            input_topic = segment_id + "-in"

            if seg_type == "start-goal":
                template_filled = START_GOAL_TEMPLATE.format(**{
                    "segment_id": segment_id,
                    "track_id": track_id,
                    "input_topic": input_topic,
                    "output_topic": next_segments[0] + "-in",
                    "seg_id": segment_id,
                })
            elif seg_type == "bottleneck":
                # Generate Output-Topics as list
                output_topics_list = [ns + "-in" for ns in next_segments]
                # Since we need a list in Python code, we convert to e.g. JSON:
                template_filled = BOTTLENECK_TEMPLATE.format(**{
                    "segment_id": segment_id,
                    "track_id": track_id,
                    "input_topics": [input_topic],
                    "output_topics": output_topics_list,
                })
            elif seg_type == "caesar":
                output_topics_list = [ns + "-in" for ns in next_segments]
                template_filled = CAESAR_TEMPLATE.format(**{
                    "segment_id": segment_id,
                    "track_id": track_id,
                    "input_topics": [input_topic],
                    "output_topics": output_topics_list,
                })
            else:
                # normal
                template_filled = NORMAL_TEMPLATE.format(**{
                    "segment_id": segment_id,
                    "track_id": track_id, 
                    "input_topic": input_topic,
                    "output_topic": output_topic,
                })


            # Write Python file
            filename = f"{segment_id}.py"
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "w", encoding="utf-8") as sf:
                sf.write(template_filled)
            # Make executable (optional, Linux/Mac)
            os.chmod(filepath, 0o755)

    print(f"Done! Segment scripts were generated in '{out_dir}'")


if __name__ == "__main__":
    main()
