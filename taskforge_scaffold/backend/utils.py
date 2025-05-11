import sqlite3
import json

PRIORITY_CLR = {"High":"B31337","Medium":"B5A72E","Low":"3DB14A"}
STATUS_CLR = {"Stuck":"B31337","Working on it":"F0A43D","Waiting for review":"3D7FF0","Done":"3DB14A"}

def parse_json(s: str) -> list:
    return json.loads(s)

def sanitize_tasks(raw: list) -> list:
    # Deduplicate, infer dates/priorities
    return raw

def load_prompt_template() -> str:
    # Load from file or env
    return "You are an EA. Extract action items..."

def group_by_owner(tasks: list) -> dict:
    groups = {}
    for t in tasks:
        owner = t.get("Assignee", "Unassigned")
        groups.setdefault(owner, []).append(t)
    return groups
