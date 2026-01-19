import json
import random
import numpy as np
from dataclasses import dataclass
from more_itertools import flatten


@dataclass
class Point:
    center: tuple
    radius: int
    height: int
    angle: int


def generate_room(num_rooms: int, max_num_features: int) -> list:

    current_room = Point((0, 0, 0), 600, 600, 0)
    rooms = [[current_room]]
    current_line = 0
    for room in range(num_rooms):
        for _ in range(random.randrange(max_num_features)):
            angle = random.randint(0, 50) if random.randint(1, 10) >= 8 else 0
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
                int(np.random.normal(1100, 100, 1)[0]),
                int(np.random.normal(1100, 100, 1)[0]),
                angle,
            )
            rooms[current_line].append(next_feature)
        # Advance line:
        angle = random.randint(0, 50) if random.randint(1, 10) >= 8 else 0
        next_room = Point(
            (
                int(
                    np.random.normal(
                        current_room.center[0] + current_room.radius + 300, 50, 1
                    )[0]
                ),
                random.choice([1, -1])
                * int(
                    np.random.normal(
                        current_room.center[1] + current_room.radius + 300, 50, 1
                    )[0]
                ),
                int(
                    np.random.uniform(
                        -2000 + current_room.center[2], 2000 + current_room.center[2], 1
                    )[0]
                ),
            ),
            int(np.random.normal(1100, 100, 1)[0]),
            int(np.random.normal(1100, 100, 1)[0]),
            angle,
        )
        rooms[current_line].append(next_room)
        # advance_room = False if random.randint(1, 10) >= 4 else True
        advance_room = True
        if advance_room and room != num_rooms - 1:
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


def main():

    for room in range(20):

        result = {"FloodFillLines": {}}
        points = generate_room(4, 5)
        entrances = generate_entrances(points)
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

        """
        result["Entrances"] = {"Entrance_0": {
            "Location": {
                "X": 0, 
                "Y": 0, 
                "Z": 0,
                },
            "Direction": {
                "Roll": 0,
                "Pitch": 0,
                "Yaw": 0 
                },
            "Type": "Entrance"
            }} 
        """
        result["Name"] = f"RMA_ICGEN_BIG{room}"
        result["Bounds"] = 4500
        result["Tags"] = ["Rooms.Linear.CustomBig"]
        with open(f"generated/RMA_ICGEN_BIG{room}.json", "w") as f:
            json.dump(result, f, indent=4)


if __name__ == "__main__":
    main()
