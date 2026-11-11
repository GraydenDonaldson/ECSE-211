from traceback import print_exc
from final_robot import FinalRobot
from utils.brick import reset_brick


def parsed_input(title):
    return map(int, input().replace("(", "").replace(")", "").split(", "))

x_entrance, y_entrance = parsed_input("Coordinates of street entrance (x, y): ")
x_exit, y_exit = parsed_input("Coordinates of street exit (x, y): ")

suzuki = FinalRobot(
    left_motor_id= " ADD ID HERE ",
    right_motor_id= " ADD ID HERE ",
    conveyer_motor_id= " ADD ID HERE ",
    storage_motor_id=  " ADD ID HERE ",
    left_color_sensor_id=  " ADD ID HERE ",
    right_color_sensor_id=  " ADD ID HERE ",
    ultrasonic_sensor_id=  " ADD ID HERE "
)

try:
    suzuki.safest_to_point(x_entrance, y_entrance)
    suzuki.map.map_street(x_exit, y_exit)
    
except KeyboardInterrupt:
    print("Manualluy Interupted")
except suzuki.TaskCompleted:
    print("Successfully completed goal, terminated")
except Exception:
    print_exc()
finally:
    suzuki.simple(0, 0)
    reset_brick()