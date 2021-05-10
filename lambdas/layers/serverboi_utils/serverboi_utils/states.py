import json
import os
from typing import Tuple


def translate_state(service: str, state: str) -> Tuple[str, str]:
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "states.json")

    with open(file_path) as states_data:
        states = json.load(states_data)

    for state_entry in states[service]:
        if state.lower() == state_entry["state"]:
            sb_state = state_entry["sb_state"]
            emoji = state_entry["emoji"]

    return sb_state, emoji