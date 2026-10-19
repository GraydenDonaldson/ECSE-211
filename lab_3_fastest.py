from robot import Robot

suzuki = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=4, right_light_sensor_id=3)

# We always start at 0,0 so update position
suzuki.x_pos = 0
suzuki.y_pos = 0

# Disable line detection
suzuki.line_update = False

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
        
    def face_toward(self, target_x, target_y):
        a = target_x - self.x_pos
        b = target_y - self.y_pos
        angle = atan(a/b) % 360
        if angle < 0:
            self.turn_left_angle(abs(angle))
        self.turn_right_angle(angle)


    def go_toward(self, target_x, target_y):
        a = target_x - self.x_pos
        b = target_y - self.y_pos
        d = (((a^2)+(b^2))^(0.5))
        self.go_distance(d)
