#Danielle Newberry &  Ben Allan-Rahill
#code to power sunrise lamo using esp32 feather huzzah


from machine import Pin, PWM, RTC
import esp 
import machine, neopixel
import time

#constant colors
BLUE =(100,149,237)
PINK = (220,20,60)
YELLOW = (255,215,0)
GREEN = (0,255,0)
PURPLE = (255,105,180)
ORANGE = (205,55,0)
RED = (205,0,0)

LIGHTS = 24
BUZZER_PIN = 25
NEO_PIN = 26

# Set to false to disable testing/tracing code
TESTING = True

t = rtc.datetime #global time tracker

"""takes as input number of minutes it takes for strip to fade from min to max """
def sunrise(light_minutes):
    np = neopixel.NeoPixel(Pin(NEO_PIN), LIGHTS) #using 24 pixel ring
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

    for i in range(light_minutes - 1):
            
            for j in range(LIGHTS):  
                np[j] = (i,i//2,0) 
                np.write()
            
            if TESTING:
                time.sleep(.5)
            else:
                time.sleep(60) # 60 for once per min
           
        

    #When lights reach full brightness (at alarm time buzzer goes off)


def alarm():
    #buzzer code adapted from: https://micropython-on-wemos-d1-mini.readthedocs.io/en/latest/basics.html#beepers
            
    beeper = PWM(Pin(BUZZER_PIN), freq=440, duty=512)

    tempo = 5
    tones = {
        'c': 262,
        'd': 294,
        'e': 330,
        'f': 349,
        'g': 392,
        'a': 440,
        'b': 494,
        'C': 523,
        ' ': 0,
    }

    melody = 'cdefgabC'
    rhythm = [8, 8, 8, 8, 8, 8, 8, 8]

    for tone, length in zip(melody, rhythm):
        beeper.freq(tones[tone])
        time.sleep(tempo/length)

    beeper.deinit() #TODO: signal this when button pressed
    

"""uses RTC and checks if it is 30 min before wake up time"""
def wakeup(hour, min):
    if (t.tm_hour == hour and
        t.tm_min == min-30 and
        t.tm_sec == 60):
        return True
    
#create FSM
""" modes:
WAKEUP (sunrise sequence)
    trigger 30 min before wakeup time
IDLE (display time light off)
    trigger off button pressed
ON (display time light on -> cycle though colors with each time button pressed changing color)
    trigger color/light button pressed (must be diff than off button)
"""
    
if TESTING:
    sunrise(10) #30 when not testing
else:
    sunrise(30)
#repeat until user presses off button
alarm()
