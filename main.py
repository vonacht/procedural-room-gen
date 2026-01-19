import json
import random
import numpy as np
from dataclasses import dataclass

@dataclass
class Point:
    center: tuple
    radius: int
    height: int 
    angle: int 

def generate_room(num_rooms: int) -> list:

    current_room = Point((0, 0, 0), 600, 600, 0)
    rooms = [[current_room]]
    current_line = 0
    for room in range(num_rooms):
        angle = random.randint(0, 50) if random.randint(1, 10) >= 8 else 0
        next_room = Point((random.choice([1, -1]) * int(np.random.normal(current_room.center[0] + current_room.radius + 300, 50, 1)[0]),
                           random.choice([1, -1]) * int(np.random.normal(current_room.center[1] + current_room.radius + 300, 50, 1)[0]),
                           int(np.random.uniform(-2000 + current_room.center[2], 2000 + current_room.center[2], 1)[0])),
                           int(np.random.normal(800, 50, 1)[0]),
                           int(np.random.normal(800, 50, 1)[0]),
                           angle)
        rooms[current_line].append(next_room)
        #advance_room = False if random.randint(1, 10) >= 4 else True 
        advance_room = False
        if advance_room:
            new_line = random.randrange(len(rooms))
            current_room = rooms[new_line][random.randrange(len(rooms[new_line]))]
            rooms.append([current_room])
            current_line = len(rooms) - 1
        else:
            current_room = next_room

    return rooms
            
def main():
    
    result = {
            "FloodFillLines": {}
            }
    points = generate_room(4)
    for ii, line in enumerate(points):
        lines = {"Points": []}
        for point in line:
            lines["Points"].append({"Location": {
                "X": point.center[0],
                "Y": point.center[1],
                "Z": point.center[2]
                },
                          "HRange": point.radius,
                          "VRange": point.height,
                          "FloorAngle": point.angle})
        result["FloodFillLines"][f"FFill_{ii}"] = lines


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

    result["Name"] = "test room"
    result["Bounds"] = 3500
    result["Tags"] = ["Rooms.Linear.Test"]
    print(result)
    with open("test.json", 'w') as f:
        json.dump(result, f, indent=4)



if __name__ == "__main__":
    main()
