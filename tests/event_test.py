#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from context import *

def foobar(e):
    e.del_handler(foobar)

def foobar2(e):
    pass

def foobar3(e):
    global x
    x = 5

def foobar4(e):
    e.del_handler(foobar3)

def foobar5(e):
    global y
    y += 5

x = 0
y = 0
ev = util.Event.Event()
ev.add_handler(foobar)
ev.add_handler(foobar)
ev.add_handler(foobar2)
ev.add_handler(foobar4)
ev.add_handler(foobar2)
ev.add_handler(foobar)
h = ev.add_handler(foobar5)
ev.add_handler(foobar2)
ev.add_handler(foobar3)
ev.add_handler(foobar2)
ev.add_handler(foobar)
ev.add_handler(foobar)

ev.trigger(ev)

assert x == 0
assert y == 5

for i in ev._handlers:
    assert i._callback == foobar2 or i._callback == foobar4 or i._callback == foobar5

h.unregister()
ev.del_handler(foobar4)

ev.trigger(ev)

assert y == 5

print("Test passed.")
