from sense_hat import SenseHat
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
sense = SenseHat()
import time 
import json
import BlynkLib
connection_string = "INSERT_AZURE_AUTH"
BLYNK_TEMPLATE_ID = "TMPL4sVXjZnQO"
BLYNK_TEMPLATE_NAME = "PiBox"
BLYNK_AUTH_TOKEN = "INSERT_BLYNK_AUTH"
device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)

print("Connecting to Azure")
try:
    device_client.connect()
    print("Connected!")
except Exception as e:
    print(f"Error connecting to the IOT hub: {e}")

#Assign RGB
GREEN = (0, 255, 0)
RED = (255, 0 , 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
OFF = (0,0,0)

temp = sense.get_temperature()
humidity = sense.get_humidity()
mag = sense.get_compass()



#Define Threshold for detecting a 90-degree rotation
ROTATION_THRESHOLD = 45

#Set Initial Orientation
initial_orientation = sense.get_gyroscope()

sense.clear(BLUE)

#Function 1 - Brake Detection

brake_trigger = 1.5 #Set value for amount of movement required to trigger harsh break detection function

def brake_check():
    harshBrake = False
    acceleration = sense.get_accelerometer_raw()
    x = abs(acceleration['x'])
    y = abs(acceleration['y'])
    z = abs(acceleration['z'])

    if x > brake_trigger or y > brake_trigger or z > brake_trigger:
        harshBrake = True
        print("Harsh Brake!")
    return harshBrake


#Function 2 - Flip Detection - The idea of this function is to take gyroscope parameters. If these parameters above
#a certain threshold, the "detect_rotation" function triggers. This works individually but not on my main script?

def detect_rotation():
    orientation = sense.get_gyroscope()
    pitch = orientation['pitch']
    roll = orientation['roll']

    delta_pitch = abs(pitch - initial_orientation['pitch'])
    delta_roll = abs(roll - initial_orientation['roll'])

    if (ROTATION_THRESHOLD <= delta_pitch <= (ROTATION_THRESHOLD + 10) or
        ROTATION_THRESHOLD <= delta_roll <= (ROTATION_THRESHOLD + 10)):
        return True
    return False


#Function(s) 3 - Weather Warning Trigger

def weather_warning_cold():
    temp = sense.get_temperature()
    if (temp < 5):
        print("Temp below 5 degrees!")
        return True
    return False

def weather_warning_hot():
    temp = sense.get_temperature()
    if (temp > 40):
        print("Temp has surpassed 30 degrees!")
        return True
    return False

def warning_signal():
    sense.show_message("Slow Down!")
    sense.clear(YELLOW)
    time.sleep(2)
    sense.clear(BLUE)


@blynk.on("V1")
def warning_button_handler(value):
    if int(value[0]) == 1:
        warning_signal()


while True: 
    
    blynk.run()

    if weather_warning_cold():
        sense.show_message("Brr!", scroll_speed=0.05, text_colour=BLUE)
        sense.clear(BLUE)
        message = Message(json.dumps({ 'event' : 'weather_warning_cold'}))
        device_client.send_message(message)
        #blynk.notify("Car is very cold!")
        time.sleep(3)

    if weather_warning_hot():
        sense.show_message("It's Hot!", scroll_speed=0.05)
        sense.clear(RED)
        message = Message(json.dumps({ 'event' : 'weather_warning_hot'}))
        device_client.send_message(message)
        #blynk.notify("Car is very hot!")
        time.sleep(3)

    if brake_check():
        sense.clear(RED)
        time.sleep(0.5)
        sense.clear(OFF)
        time.sleep(0.5)
        sense.clear(RED)
        time.sleep(0.5)
        sense.clear(BLUE)
        message = Message(json.dumps({ 'event' : 'harsh_brake'}))
        device_client.send_message(message)
        #blynk.notify("Harsh movement detected!")
        time.sleep(0.5)


    elif detect_rotation():
        print("Car has flipped!")
        sense.clear(RED)
        time.sleep(1.5)
        sense.clear(BLUE)
        message = Message(json.dumps({ 'event' : 'rotation_detected'}))
        device_client.send_message(message)
        #blynk.notify("Car has flipped!")
    time.sleep(0.5)

