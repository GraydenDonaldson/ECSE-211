# ECSE-211
Tracking for ECSE-211 Robot 

## Executing the final project
Execute the file "execute_final.py"
```BASH 
python3 execute_final.py 
```

## Using the robot class

### Setup 
Call the FinalRobot class with all port IDs specified

```python
suzuki = FinalRobot(
    left_motor_id= " ADD ID HERE ",
    right_motor_id= " ADD ID HERE ",
    conveyer_motor_id= " ADD ID HERE ",
    storage_motor_id=  " ADD ID HERE ",
    left_color_sensor_id=  " ADD ID HERE ",
    right_color_sensor_id=  " ADD ID HERE ",
    ultrasonic_sensor_id=  " ADD ID HERE "
)
```

### Movement Functions
* Moving set disance (x : float):
    ```python
        suzuki.go_distance(x)
    ```
* Moving to a specific point (x : int, y : int) (the x and y blocks)
    ```
        suzuki.safest_to_point(x, y)
    ```
* Turning left by a specific angle (theta : float):
    ```python 
        suzuki.turn_left_angle(theta)
    ```
* Turning right by a specific angle (theta : float):
    ```python 
        suzuki.turn_right_angle(theta)
    ```
* Turning to face a specific angle, from any starting angle (theta : float)
    ```python
        suzuki.face_angle(theta)
    ```

## Odometer functions
* Getting current x position
    ```python
        suzuki.x_pos()
    ```
* Getting current y position
    ```python
        suzuki.y_pos()
    ```
* Getting current filtered ultrasonic sensor reading
    ```python
        suzuki.ultrasonic_sensor_distance()
    ```
* Getting current angle
    ```python
        suzuki.theta()
    ```

## Mapping functions:
* Mapping the street from the street entrance
    ```python
        suzuki.map.map_street(x_exit, y_exit)
    ```
* Replacying the mapped street from the street entrance
    ```python
        suzuki.map.replay_map()
    ```