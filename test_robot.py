import final_robot

if __name__ == "__main__":
    suzuki = final_robot.FinalRobot("A", "B", "C", "D", 1, 2, 3, 4)
    suzuki.update_odometer()
    suzuki.correct_odometer()