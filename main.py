#Danielle Newberry &  Ben Allan-Rahill
#code to power sunrise lamp using esp32 feather huzzah


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


def sunrise():
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

    # https://learn.adafruit.com/pyportal-wake-up-light?view=all


    #TODO: check RTC to see if 7AM
    default_wake_up = "7:30A"

    # number of minutes it takes for strip to fade from min to max
    light_minutes = 10 #30 mins


    for i in range(light_minutes - 1):
            
            for j in range(LIGHTS):  
                np[j] = (i,i//2,0) 
                np.write()
            
            time.sleep(.5) # 60 for once per min
            #light_minutes -= light_minutes
        

    #When ulights reach full brightness (at alarm time buzzer goes off)


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

    beeper.deinit()
    #repeat until user presses off button


sunrise()
alarm()
