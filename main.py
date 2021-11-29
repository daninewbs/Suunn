
from machine import Pin
import esp 
import machine, neopixel
import time



####################################################
#light code

#constant colors
BLUE =(100,149,237)
PINK = (220,20,60)
YELLOW = (255,215,0)
GREEN = (0,255,0)
PURPLE = (255,105,180)
ORANGE = (205,55,0)
RED = (205,0,0)

LIGHTS = 24



np = neopixel.NeoPixel(Pin(26), LIGHTS) #using 24 pixel ring
esp.osdebug(None) #disable debugging

#TODO: (later) check server see what color other light is at and (if diff) set this light to that color
#TODO: press putton on LCD Screen to cycle though color selection

#set all neopixels to same color
"""color = RED
for i in range(LIGHTS):  
    np[i] = color 
np.write()


# clear
for i in range(LIGHTS):
    np[i] = (0, 0, 0)
np.write()
"""

# https://learn.adafruit.com/pyportal-wake-up-light?view=all


#TODO: check RTC to see if 7AM
default_wake_up = "7:30A"

# number of minutes it takes for strip to fade from min to max
light_minutes = 30


for i in range(light_minutes - 1):
        
        for j in range(LIGHTS):  
            np[j] = (i,i//2,0) 
            np.write()
        
        time.sleep(60) # 60 for once per min
        #light_minutes -= light_minutes
    

#When user presses button lights off


####################################################
#buzzer code
