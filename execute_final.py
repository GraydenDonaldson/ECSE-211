from traceback import print_exc
from final_robot import FinalRobot
from utils.brick import reset_brick


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
    suzuki.map.map_street()
except KeyboardInterrupt:
    print("Manualluy Interupted")
except suzuki.TaskCompleted:
    print("Successfully completed goal, terminated")
except Exception:
    print_exc()
finally:
    suzuki.simple(0,0)
    reset_brick()