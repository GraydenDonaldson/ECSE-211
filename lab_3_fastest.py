from robot import Robot

suzuki = Robot(left_motor_id = "A", right_motor_id = "B", left_light_sensor_id=4, right_light_sensor_id=3)

# We always start at 0,0 so update position
suzuki.x_pos = 0
suzuki.y_pos = 0

# Disable line detection
suzuki.line_update = False

