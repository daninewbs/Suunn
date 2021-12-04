from machine import Pin
import time

A_BUTTON = Pin(15, Pin.IN)
B_BUTTON = Pin(32, Pin.IN)
C_BUTTON = Pin(14, Pin.IN)


class Buttons:
    long_press = False
    a = False
    b = False
    c = False
    edit_mode = False

    def __init__(self) -> None:

        self.__set_interrupts()

    def __set_interrupts(self):
        # attach the interrupts
        C_BUTTON.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.callback)
        # A_BUTTON.irq(trigger=Pin.IRQ_FALLING, handler=button_down)

    def callback(self, pin):
        if not pin.value():
            self.first_press = time.time_ns()
        else:
            if time.time_ns() - self.first_press > 1 * pow(10, 9):
                self.long_press = True
                self.toggle_edit()

    def edit(self, a_press=None, b_press=None, c_press=None):
        # use polling
        # use edit functions
        self.edit_mode = True
        while self.edit_mode:
            if not A_BUTTON.value():
                time.sleep(0.05)
                # A pressed
                a_press()
            elif not B_BUTTON.value():
                # B pressed
                b_press()
            elif not C_BUTTON.value():
                # C pressed
                c_press()

    def toggle_edit(self):
        self.edit_mode = not self.edit_mode
