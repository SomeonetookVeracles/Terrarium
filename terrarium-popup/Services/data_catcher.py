# data_catcher.py
import json
from pathlib import Path

CONFIG_PATH = Path("config.json")


def get_metric_names():
    return ["pet_happiness", "pet_nourishment", "pet_recreation"]


def get_metric_values():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            game_data = config.get("GAME", {})
            return {
                "pet_happiness": int(game_data.get("pet_happiness", 0)),
                "pet_nourishment": int(game_data.get("pet_nourishment", 0)),
                "pet_recreation": int(game_data.get("pet_recreation", 0))
            }
    else:
        return {
            "pet_happiness": 0,
            "pet_nourishment": 0,
            "pet_recreation": 0
        }


def deteriorate_metrics():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    else:
        config = {}

    game_data = config.get("GAME", {})

    for key in ["pet_happiness", "pet_nourishment", "pet_recreation"]:
        game_data[key] = max(0, int(game_data.get(key, 0)) - 1)

    config["GAME"] = game_data

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
