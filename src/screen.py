import machine
import time
from ssd1306 import SSD1306_I2C
#from fonts.TitilliumWeb_Regular11 import TitilliumWeb_Regular11


class screen:
    FREQ_OFFSET = (10, 5)
    SIGTYPE_OFFSET = (10,24)
    STEP_OFFSET = (96,24)
    BLINK_TMR_TM = 500


    def __init__(self) -> None:
        self.i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=1_000_000)
        self.disp = SSD1306_I2C(128,32, self.i2c)
        #self.freq_fnt = TitilliumWeb_Regular11(self.disp)
        self.freq = 0
        self.step = 1
        self.sigtype = 'Sin'
        self.selection = 0
        self.blink_tmr = 0
        self.blink_state = False

    def __upd_freq(self):
        #self.freq_fnt.text(f'{self.freq:010,d}', 7, 5)
        self.disp.text(f'{self.freq:010,d} hz', 7, 5)
        
    def __upd_sigtype(self):
        self.disp.text(self.sigtype, 7, 24)
    
    def __upd_step(self):
        val = self.step
        if val >= 1_000_000:
            self.disp.text(f'{val/1_000_000}Mhz', 72, 24)
        elif val >= 1000:
            self.disp.text(f'{val/1000}Khz', 72, 24)
        else:
            self.disp.text(f'{val}hz', 72, 24)

    def blink(self, cb):
        if time.ticks_ms() > self.blink_tmr:
            self.blink_state = not self.blink_state
            self.blink_tmr = time.ticks_ms() + self.BLINK_TMR_TM
        if self.blink_state:
            cb()

    def update(self):
        self.disp.fill(0)
        
        if self.selection == 1:
            self.blink(self.__upd_sigtype)
            self.__upd_freq()
            self.__upd_step()
        elif self.selection == 2:
            self.blink(self.__upd_step)
            self.__upd_freq()
            self.__upd_sigtype()
        else:
            self.__upd_freq()
            self.__upd_sigtype()
            self.__upd_step()
            self.selection = 0
        self.disp.show()

