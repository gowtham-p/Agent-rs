
import pandas as pd
import json

# === File Paths (Update as needed) ===
signal_file_path = "/Users/gowtham/Downloads/tactics_data_ne_corp_7_days_11_to_18_june/InitialAccess/Userloginsuccessful.csv"
historical_user_path = "/Users/gowtham/Downloads/Signal Agent files/Historical record/User_last_180_days_dump_ne_corp.csv"
entity_mapping_path = "/Users/gowtham/Downloads/Signal Agent files/entity_primary_identifiers.json"
output_path = "/Users/gowtham/Downloads/Relevant_Historical_Signal_Matches.csv"

# === Load Data ===
signals_df = pd.read_csv(signal_file_path)
with open(entity_mapping_path, "r") as f:
    entity_field_map = json.load(f)
historical_user_df = pd.read_csv(historical_user_path)

# === Extract User Entity Fields ===
user_entity_fields = entity_field_map.get("User", [])
present_user_fields = [field for field in user_entity_fields if field in signals_df.columns]
unique_user_entities = set()
for field in present_user_fields:
    unique_user_entities.update(signals_df[field].dropna().unique())

# === Filter Historical Records ===
filtered_historical_df = pd.DataFrame()
for field in present_user_fields:
    if field in historical_user_df.columns:
        matches = historical_user_df[historical_user_df[field].isin(unique_user_entities)]
        filtered_historical_df = pd.concat([filtered_historical_df, matches], ignore_index=True)
filtered_historical_df = filtered_historical_df.drop_duplicates()

# === Convert Timestamps ===
signals_df["security.events.metadata.eventTimestamp"] = pd.to_datetime(
    signals_df["security.events.metadata.eventTimestamp"], errors='coerce'
)
filtered_historical_df["security.events.metadata.eventTimestamp"] = pd.to_datetime(
    filtered_historical_df["security.events.metadata.eventTimestamp"], errors='coerce'
)

# === Define Relevant Columns ===
current_signals = signals_df[[
    "alertId", "security.events.metadata.eventTimestamp",
    "security.events.securityResult.summary", "alertCategory",
    "security.events.target.user.userid", "security.events.target.user.emailAddresses"
]].rename(columns={
    "alertId": "current_alertId",
    "security.events.metadata.eventTimestamp": "current_eventTimestamp",
    "security.events.securityResult.summary": "current_summary",
    "alertCategory": "current_tactic",
    "security.events.target.user.userid": "current_userid",
    "security.events.target.user.emailAddresses": "current_email"
})

historical_signals = filtered_historical_df[[
    "alertId", "security.events.metadata.eventTimestamp",
    "security.events.securityResult.summary", "alertCategory",
    "security.events.target.user.userid", "security.events.target.user.emailAddresses"
]].rename(columns={
    "alertId": "historical_alertId",
    "security.events.metadata.eventTimestamp": "historical_eventTimestamp",
    "security.events.securityResult.summary": "historical_summary",
    "alertCategory": "historical_tactic",
    "security.events.target.user.userid": "historical_userid",
    "security.events.target.user.emailAddresses": "historical_email"
})

# === Tactic Chains for Relevance ===
tactic_chains = [
    ("Initial Access", "Execution"), ("Persistence", "Lateral Movement"),
    ("Credential Access", "Defense Evasion"), ("Initial Access", "Lateral Movement"),
    ("Execution", "Command and Control"), ("Command and Control", "Exfiltration"),
    ("Privilege Escalation", "Credential Access"), ("Credential Access", "Exfiltration"),
    ("Persistence", "Command and Control"), ("Execution", "Exfiltration"),
    ("Exfiltration", "Impact")
]

# === User Key & Chunked Processing ===
current_signals["user_key"] = current_signals["current_userid"].fillna(current_signals["current_email"])
historical_signals["user_key"] = historical_signals["historical_userid"].fillna(historical_signals["historical_email"])

chunk_size = 500
results = []
for i in range(0, len(current_signals), chunk_size):
    chunk = current_signals.iloc[i:i+chunk_size]
    merged_df = pd.merge(chunk, historical_signals, on="user_key", suffixes=("_cur", "_hist"))
    merged_df = merged_df[merged_df["historical_eventTimestamp"] < merged_df["current_eventTimestamp"]]

    merged_df["relevance_reason"] = merged_df.apply(
        lambda row: f"Tactic sequence match: {row['historical_tactic']} → {row['current_tactic']}"
        if (row["historical_tactic"], row["current_tactic"]) in tactic_chains
        else ("Same tactic category over time" if row["historical_tactic"] == row["current_tactic"] else None),
        axis=1
    )

    relevant_chunk = merged_df[merged_df["relevance_reason"].notnull()][[
        "current_alertId", "current_tactic", "current_summary",
        "historical_alertId", "historical_tactic", "historical_summary",
        "relevance_reason", "user_key"
    ]]
    results.append(relevant_chunk)

# === Export Result ===
final_relevance_df = pd.concat(results, ignore_index=True)
final_relevance_df.to_csv(output_path, index=False)
print(f"Done. Output saved to: {output_path}")
