from robot import Robot
from math import atan2, degrees
from time import sleep

suzuki = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=1, right_light_sensor_id=3)

ERROR = 5

suzuki.x_pos = 0
suzuki.y_pos = 0

suzuki.line_update = False

way_points = []

for i in range (4):
    x = int(input("X coordinate: "))
    y = int(input("Y coordinate: "))
    way_points.append((x, y))


def distance_to(target_x, target_y):
    a = target_x - suzuki.x_pos
    b = target_y - suzuki.y_pos
    return (a**2 + b**2)**0.5

def face_toward(target_x, target_y):
    a = target_x - suzuki.x_pos
    b = target_y - suzuki.y_pos
    suzuki.face_angle(degrees(atan2(a, b)) % 360)

def go_toward(target_x, target_y):
    suzuki.go_distance(distance_to(target_x, target_y))

def head():
    pass

def body():
    for waypoint in way_points:
        target_x, target_y = waypoint
        target_x = suzuki.convert_block_to_coordinates(target_x)
        target_y = suzuki.convert_block_to_coordinates(target_y)
        print(target_x, target_y)

        if distance_to(target_x, target_y) > ERROR:
            face_toward(target_x, target_y)
            go_toward(target_x, target_y)

    sleep(0.5)

    raise suzuki.TaskCompleted

suzuki.execute(head, body)
