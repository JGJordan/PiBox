from sense_hat import SenseHat
sense = SenseHat()

#Assign RGB
GREEN = (0, 255, 0)
RED = (255, 0 , 0)
BLUE = (0, 0, 255)

temp = sense.get_temperature()
humidity = sense.get_humidity()
gyro = sense.get_orientation()
acceleration = sense.get_accelerometer_raw()
mag = sense.get_compass()

sense.clear(BLUE)

