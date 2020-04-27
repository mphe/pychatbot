#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from context import util

x = 0
y = 0
z = 0
stopped = True


class Foobar:
    def __init__(self, ev):
        self.handle = ev.register(self.foobar)

    async def foobar(self, e):
        e.unregister(self.handle)


async def foobar2(e):
    global z
    z = 42


async def foobar3(e):
    global x
    x = 5


async def foobar4(e):
    e.unregister(hnd_foobar3)


async def foobar5(e):
    global y
    y += 5


async def foobar6(e):
    global y
    assert y == 0


async def foobar7(e):
    global x, y
    assert z != 0 and y != 0
    return util.event.EVENT_HANDLED


async def foobar8(e):
    global stopped
    stopped = False


ev = util.event.Event()

hnd_post = ev.register(foobar7, util.event.EVENT_POST)
Foobar(ev)
Foobar(ev)
ev.register(foobar2)
hnd_foobar4 = ev.register(foobar4)
ev.register(foobar2)
Foobar(ev)
hnd_foobar5 = ev.register(foobar5)
ev.register(foobar2)
hnd_foobar3 = ev.register(foobar3)
ev.register(foobar2)
Foobar(ev)
Foobar(ev)
hnd_pre = ev.register(foobar6, util.event.EVENT_PRE)
ev.register(foobar8, util.event.EVENT_POST + 10)

asyncio.run(ev.trigger(ev))

assert x == 0
assert y == 5
assert stopped

hnd_post.unregister()
hnd_pre.unregister()

for i in ev._handlers:
    if i:
        assert i._callback == foobar2 or i._callback == foobar4 or \
            i._callback == foobar5 or i._callback == foobar8

hnd_foobar5.unregister()
ev.unregister(hnd_foobar4)

asyncio.run(ev.trigger(ev))

assert y == 5
