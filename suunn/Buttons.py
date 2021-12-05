from machine import Pin
import time

A_BUTTON = Pin(15, Pin.IN)
B_BUTTON = Pin(32, Pin.IN)
C_BUTTON = Pin(14, Pin.IN)


class Buttons:
    long_press = False
    pressed_map = {"Pin(15)": False, "Pin(32)": False, "Pin(14)": False}

    def __init__(self) -> None:
        self.on_a = None
        self.on_b = None
        self.on_c = None

        self.__set_interrupts()

    def __set_interrupts(self):
        # attach the interrupts

        # LONG PRESS
        C_BUTTON.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.LONG_PRESS_ISR
        )

        # normal push button ISRs
        A_BUTTON.irq(trigger=Pin.IRQ_FALLING, handler=self.BDOWN_ISR)
        B_BUTTON.irq(trigger=Pin.IRQ_FALLING, handler=self.BDOWN_ISR)

    def LONG_PRESS_ISR(self, pin):
        if not pin.value():
            self.first_press = time.time_ns()
        else:
            if time.time_ns() - self.first_press > 1 * pow(10, 9):
                self.long_press = not self.long_press
                print("LONG PRESS")

    def BDOWN_ISR(self, pin):
        for k in [A_BUTTON, B_BUTTON, C_BUTTON]:
            if pin == k:
                self.pressed_map[f"{k}"] = True

    def check_for_input(self):
        if self.pressed_map["Pin(15)"]:
            # A pressed
            time.sleep(0.05)
            self.on_a()
            self.pressed_map["Pin(15)"] = False
        elif self.pressed_map["Pin(32)"]:
            # B pressed
            time.sleep(0.05)
            self.on_b()
            self.pressed_map["Pin(32)"] = False

