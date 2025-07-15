import json
import yaml
from datetime import datetime
from collections import defaultdict

# === CONFIG ===
INPUT_CASE_FILES = [
    "/Users/gowtham/Downloads/Signal Agent files/entity tb/NE_Corp_03_Jun_to_10_Jun_part_2.json",
    "/Users/gowtham/Downloads/Signal Agent files/entity tb/NE_Corp_10_Jun_to_18_Jun_part_3.json",
    "/Users/gowtham/Downloads/Signal Agent files/entity tb/NE_Corp_18_Jun_to_26_Jun_part_4.json",
    "/Users/gowtham/Downloads/Signal Agent files/entity tb/NE_Corp_26_May_to_03_Jun_part_1.json"
]
ENTITY_MAP_FILE = "/Users/gowtham/Downloads/Signal Agent files/entity identifier/entity_primary_identifiers.json"
OUTPUT_FILE = "/Users/gowtham/Downloads/entity_tribal_knowledge.yaml"

# === LOAD ENTITY FIELD MAPPING ===
with open(ENTITY_MAP_FILE, "r") as f:
    entity_field_map = json.load(f)

field_to_entity_type = {}
for entity_type, fields in entity_field_map.items():
    for field in fields:
        field_to_entity_type[field] = entity_type

# === LOAD CASES ===
cases = []
for file in INPUT_CASE_FILES:
    with open(file, "r") as f:
        cases.extend(json.load(f))

# === PROCESS ===
entity_context = defaultdict(lambda: {
    "entity_type": None,
    "signal_stats": {},
    "source_tickets": set(),
    "behavioral_patterns": set()
})

for case in cases:
    ticket_id = case.get("ticket_id")
    closure_reason = (case.get("closure_reason") or "").strip().lower()
    notes = case.get("notes", [])
    resolution_notes = [n.get("note_text", "").strip() for n in notes if n.get("note_text")]

    for signal in case.get("correlated_signals", []):
        sig_name = signal.get("signal_name")
        tactic = signal.get("mitre_tactic")
        technique = signal.get("mitre_technique")
        summary = signal.get("securityResult.summary", [None])[0] if isinstance(signal.get("securityResult.summary"), list) else signal.get("securityResult.summary")
        event_time = signal.get("signal_createdTime")

        # Standardize full ISO format
        try:
#           event_time_formatted = datetime.fromisoformat(event_time.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%SZ") if event_time else None
#            event_time_formatted = event_time if event_time else None
            event_time_formatted = datetime.fromisoformat(event_time.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S")

        except Exception:
            event_time_formatted = event_time

        likelihood = signal.get("score_likelihood")
        confidence = signal.get("score_confidence")
        impact = signal.get("score_impact")

        for field, values in signal.get("associated_signal_entities", {}).items():
            if not values:
                continue
            role = field.split(".")[0]
            entity_type = field_to_entity_type.get(field, "unknown")

            for val in values:
                entity_id = val.strip().lower()
                ctx = entity_context[entity_id]
                ctx["entity_type"] = entity_type
                ctx["source_tickets"].add(ticket_id)
                ctx["behavioral_patterns"].update(resolution_notes)

                sig_key = f"{sig_name}|{role}"
                if sig_key not in ctx["signal_stats"]:
                    ctx["signal_stats"][sig_key] = {
                        "tactic": tactic,
                        "technique": technique,
                        "summary": summary,
#                        "event_times": [],
                        "signal_events": [],
                        "total_seen_count": 0,
                        "benign_count": 0,
                        "likelihoods": [],
                        "confidences": [],
                        "impacts": []
                    }

                sig_ctx = ctx["signal_stats"][sig_key]
                sig_ctx["total_seen_count"] += 1
                if closure_reason == "benign":
                    sig_ctx["benign_count"] += 1
#                if event_time_formatted:
#                    sig_ctx["event_times"].append(event_time_formatted)
                if event_time_formatted and isinstance(signal.get("signal_id"), int):
                    sig_ctx.setdefault("signal_events", [])
                    sig_ctx["signal_events"].append({
                        "signal_id": signal["signal_id"],
                        "event_time": event_time_formatted})            
                if isinstance(likelihood, (int, float)):
                    sig_ctx["likelihoods"].append(likelihood)
                if isinstance(confidence, (int, float)):
                    sig_ctx["confidences"].append(confidence)
                if isinstance(impact, (int, float)):
                    sig_ctx["impacts"].append(impact)

# === CONVERT TO YAML STRUCTURE ===
output_yaml = []
for entity_id, data in entity_context.items():
    signals = []
    for sig_with_role, val in data["signal_stats"].items():
        sig_name, role = sig_with_role.split("|", 1)
        signals.append({
            "signal_name": sig_name,
            "role": role,
            "tactic": val["tactic"],
            "technique": val["technique"],
            "security_summary": val["summary"],
#            "event_times": [str(t) for t in val["event_times"]],
            "signal_events": val.get("signal_events", []),
            "total_seen_count": val["total_seen_count"],
            "benign_count": val["benign_count"],
            "benign_ratio": round(val["benign_count"] / val["total_seen_count"], 2),
            "avg_likelihood": round(sum(val["likelihoods"]) / len(val["likelihoods"]), 2) if val["likelihoods"] else None,
            "avg_confidence": round(sum(val["confidences"]) / len(val["confidences"]), 2) if val["confidences"] else None,
            "avg_impact_score": round(sum(val["impacts"]) / len(val["impacts"]), 2) if val["impacts"] else None
        })

    output_yaml.append({
        "entity_id": entity_id,
        "entity_type": data["entity_type"],
        "source_tickets": sorted(data["source_tickets"]),
        "signal_stats": signals,
        "summary_insights": {
            "behavioral_patterns": [],
            "analyst_consensus": ""
        },
        "policy_instructions": [
            {
            "policy_directive": "",
            "created_by": "",
            "created_at": ""
        }
        ]
    })

# === SAVE YAML ===
with open(OUTPUT_FILE, "w") as f:
    yaml.dump(output_yaml, f, sort_keys=False, allow_unicode=True)

print(f"✅ Tribal knowledge YAML written to: {OUTPUT_FILE}")
