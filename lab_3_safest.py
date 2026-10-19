from robot import Robot
from time import sleep

suzuki = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=4, right_light_sensor_id=3)

# We always start at 0,0 so update position
suzuki.x_pos = 0
suzuki.y_pos = 0

# Take waypoints from terminal
way_points = []

for i in range (4):
    x = int(input("X coordinate: "))
    y = int(input("Y coordinate: "))
    way_points.append((x, y))

def body():
    for waypoint in way_points:
        target_x, target_y = waypoint
        target_x = suzuki.convert_block_to_coordinates(target_x)
        target_y = suzuki.convert_block_to_coordinates(target_y)

        if target_x > suzuki.x_pos:
            suzuki.face_angle(90)
            suzuki.go_distance(target_x-suzuki.x_pos)
        else:
            suzuki.face_angle(270)
            suzuki.go_distance(suzuki.x_pos-target_x)

        if target_y > suzuki.y_pos:
            suzuki.face_angle(0)
            suzuki.go_distance(target_y-suzuki.y_pos)
        else:
            suzuki.face_angle(180)
            suzuki.go_distance(suzuki.y_pos-target_y)
    
    sleep(0.5)

    raise suzuki.TaskCompleted