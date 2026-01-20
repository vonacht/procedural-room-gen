import json
import math
import logging
import random
import argparse
import numpy as np
from dataclasses import dataclass
from more_itertools import flatten
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


@dataclass
class Point:
    center: tuple
    radius: int
    height: int
    angle: int


def generate_room(settings: dict) -> list:

    current_room = Point((0, 0, 0), 600, 600, 0)
    rooms = [[current_room]]
    current_line = 0
    for room in range(settings["num_rooms"]):
        for _ in range(random.randrange(settings["num_features"])):
            angle = (
                random.randint(10, 50)
                if random.randint(1, 100) >= (100 - settings["angle_percent"])
                else 0
            )
            next_feature = Point(
                (
                    random.choice([1, -1])
                    * int(
                        np.random.normal(
                            current_room.center[0] + current_room.radius, 50, 1
                        )[0]
                    ),
                    random.choice([1, -1])
                    * int(
                        np.random.normal(
                            current_room.center[1] + current_room.radius, 50, 1
                        )[0]
                    ),
                    int(
                        np.random.uniform(
                            -current_room.height + current_room.center[2],
                            current_room.height + current_room.center[2],
                            1,
                        )[0]
                    ),
                ),
                int(
                    np.random.normal(
                        settings["avg_feature_size"],
                        settings["feature_size_variance"],
                        1,
                    )[0]
                ),
                int(
                    np.random.normal(
                        settings["avg_feature_height"],
                        settings["feature_size_variance"],
                        1,
                    )[0]
                ),
                angle,
            )
            rooms[current_line].append(next_feature)
        # Advance line:
        angle = (
            random.randint(10, 50)
            if random.randint(1, 100) >= (100 - settings["angle_percent"])
            else 0
        )
        new_direction = random.randint(0, 180)
        sign = 1 if new_direction <= 90 else -1
        new_direction = new_direction if new_direction <= 90 else (180 - new_direction)
        new_direction = math.radians(new_direction)


        next_room = Point(
            (
                int(
                    current_room.center[0] + 
                    math.sin(new_direction) * np.random.uniform(
                        current_room.radius,
                        current_room.radius + settings["next_room_offset"],
                        1
                    )[0]
                ),
                int(
                    current_room.center[1] + 
                    sign * 
                    math.cos(new_direction) * 
                    np.random.uniform(
                        current_room.radius,
                        current_room.radius + settings["next_room_offset"],
                        1,
                    )[0]
                ),
                int(
                    np.random.uniform(
                        -settings["room_verticality"] + current_room.center[2],
                        current_room.center[2],
                        1,
                    )[0]
                ),
            ),
            int(
                np.random.normal(
                    settings["avg_room_size"], settings["room_size_variance"], 1
                )[0]
            ),
            int(
                np.random.normal(
                    settings["avg_room_height"], settings["room_size_variance"], 1
                )[0]
            ),
            angle,
        )
        rooms[current_line].append(next_room)
        # advance_room = False if random.randint(1, 10) >= 4 else True
        advance_room = True
        if advance_room and room != settings["num_rooms"] - 1:
            current_line += 1
            current_room = next_room
            rooms.append([next_room])
        else:
            current_room = next_room

    return rooms


def generate_entrances(points: list) -> list:
    # entrance_rooms = (len(points) + 1) // 2
    # exit_rooms = len(points) - entrance_rooms
    def generate_e(idx, t):
        idx_max, max_y = max(
            [
                (ii, point.center[1] + point.radius)
                for ii, point in enumerate(points[idx])
            ],
            key=lambda x: x[1],
        )
        idx_min, min_y = min(
            [
                (ii, point.center[1] - point.radius)
                for ii, point in enumerate(points[idx])
            ],
            key=lambda x: x[1],
        )
        angle = -90 if t == "Entrance" else 90
        if t == "Exit" and idx_max == 0:
            first_entrance = []
        else:
            first_entrance = [
                points[idx][idx_max].center[0],
                max_y,
                points[idx][idx_max].center[2] + 150,
                0,
                0,
                angle,
                t,
            ]
        angle = 90 if t == "Entrance" else -90
        if t == "Exit" and idx_min == 0:
            second_entrance = []
        else:
            second_entrance = [
                points[idx][idx_min].center[0],
                min_y,
                points[idx][idx_min].center[2] + 150,
                0,
                0,
                angle,
                t,
            ]
        return [entrance for entrance in [first_entrance, second_entrance] if entrance]

    return [generate_e(i, p) for i, p in zip([0, -1], ["Entrance", "Exit"])]


def build_json(
        points: list, entrances: list, room_num: int, key: str, settings: dict
) -> dict:

    result = {"FloodFillLines": {}}
    for ii, line in enumerate(points):
        lines = {"Points": []}
        for point in line:
            lines["Points"].append(
                {
                    "Location": {
                        "X": point.center[0],
                        "Y": point.center[1],
                        "Z": point.center[2],
                    },
                    "HRange": point.radius,
                    "VRange": point.height,
                    "FloorAngle": point.angle,
                }
            )
        result["FloodFillLines"][f"FFill_{ii}"] = lines

    result["Entrances"] = {}
    for ii, entrance in enumerate(flatten(entrances)):
        result["Entrances"].update(
            {
                f"Entrance_{ii}": {
                    "Location": {
                        "X": entrance[0],
                        "Y": entrance[1],
                        "Z": entrance[2],
                    },
                    "Type": entrance[-1],
                    "Direction": {
                        "Roll": entrance[3],
                        "Pitch": entrance[4],
                        "Yaw": entrance[5],
                    },
                }
            }
        )

    result["Name"] = f"RMA_ICGEN_{key}{room_num}"
    result["Bounds"] = settings["bounds"]
    result["Tags"] = settings["tags"]

    return result


def main():

    parser = argparse.ArgumentParser(description="Procedural generation of DRG rooms.")
    parser.add_argument(
        "-c",
        "--config_path",
        nargs="?",
        default="settings/settings.json",
        help="Path to the user configuration file. If not defined defaults to config/config.json.",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        nargs="?",
        default=Path("generated"),
        help="Path where the room JSONs will be written to. If not specified defaults to generated/.",
    )
    parser.add_argument(
        "-k",
        "--keys",
        nargs="+",
        default=None,
        help="List of keys from the settings file that will be used for the generation.",
    )
    parser.add_argument("-n", "--number", type=int, default=20, help="Number of rooms for each key, defaults to 20.")
    args = parser.parse_args()

    try:
        with open(args.config_path, "r") as f:
            user_settings = json.load(f)
    except Exception as e:
        logging.error(f"Error opening configuration file {args.config_path}: {e}")

    if args.keys is not None:
        keys = args.keys
    else:
        keys = list(user_settings.keys())

    for key in keys:
        settings = user_settings[key]
        for ii in range(args.number):
            points = generate_room(settings)
            entrances = generate_entrances(points)
            generated_room = build_json(points, entrances, ii, key, settings)
            try:
                name = f"RMA_ICGEN_{key}{ii}.json" 
                with open(Path(args.output_path) / name, "w") as f:
                    json.dump(generated_room, f, indent=4)
                logging.info(f"Writing file: {Path(args.output_path) / name}.")
            except Exception as e:
                logging.error(f"Error when writing the JSON file: {e}")


if __name__ == "__main__":
    main()
