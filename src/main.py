import time
import os

from machine import Pin
from screen import screen
from rotary_irq_rp2 import RotaryIRQ
import json
from ad9833 import AD9833

SIGTYPE = ["Sin", "Square", "Triangle"]
STEPS = [1, 10, 100, 1000, 10000, 100000, 1000000]
MAX_FREQ = 12_500_000


def save_cfg(scr):
    with open('config.json', 'wt') as fd:
        json.dump({'freq': scr.freq, 'step': scr.step, 'sigtype': scr.sigtype}, fd)


def load_cfg(scr, r):
    if 'config.json' in os.listdir('/'):
        with open('config.json', 'rt') as fd:
            cfg = json.load(fd)
            if 'step' in cfg and cfg['step'] in STEPS:
                scr.step = cfg['step']

            if 'freq' in cfg:
                scr.freq = cfg['freq']
                r.set(value=scr.freq, incr=scr.step, max_val=MAX_FREQ)

            if 'sigtype' in cfg and cfg['sigtype'] in SIGTYPE:
                scr.sigtype = cfg['sigtype']
    else:
        save_cfg(scr)


def main():
    
    r = RotaryIRQ(pin_num_clk=16,
                  pin_num_dt=17,
                  min_val=0,
                  max_val=MAX_FREQ,
                  reverse=False,
                  pull_up=True,
                  range_mode=RotaryIRQ.RANGE_WRAP)
    pwg = AD9833(sdo=3, clk=2, cs = 1)
    scr = screen()
    load_cfg(scr, r)
    pwg.set_frequency(scr.freq, 0)
    pwg.set_mode(scr.sigtype.upper())

    lock_irq = 0

    def on_btn(s):
        nonlocal scr, r, lock_irq
        if time.ticks_ms() > lock_irq:
            scr.selection += 1
            if scr.selection > 2:
                scr.selection = 0

            if scr.selection == 0:
                r.set(value=scr.freq, incr=scr.step, max_val=MAX_FREQ)
            elif scr.selection == 1:
                r.set(value=SIGTYPE.index(scr.sigtype), incr=1, max_val=len(SIGTYPE))
            elif scr.selection == 2:
                r.set(value=STEPS.index(scr.step), incr=1, max_val=len(STEPS))

            print('Selection: ', scr.selection)
            lock_irq = time.ticks_ms() + 500

    btn = Pin(18, Pin.IN, Pin.PULL_UP)
    btn.irq(on_btn, Pin.IRQ_FALLING)

    val_old = r.value()
    scr.update()
    upd_tmr = time.ticks_ms()
    while True:
        val_new = r.value()

        if val_old != val_new:
            val_old = val_new
            print('Rotary value: ', val_new)
            if scr.selection == 0:
                scr.freq = val_old
                pwg.set_frequency(scr.freq, 0)
            elif scr.selection == 1:
                scr.sigtype = SIGTYPE[val_old % len(SIGTYPE)]
                pwg.set_mode(scr.sigtype.upper())
            elif scr.selection == 2:
                scr.step = STEPS[val_old % len(STEPS)]
            scr.update()
            save_cfg(scr)

        if time.ticks_ms() > upd_tmr:
            scr.update()
            upd_tmr = time.ticks_ms() + 250


if __name__ == '__main__':
    main()
