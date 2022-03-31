#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import Callable, Optional
from .utils import call_maybe_async
from datetime import datetime


class BaseAsyncTimer:
    def __init__(self):
        self._timer: asyncio.Task = None

    def is_running(self) -> bool:
        return self._timer is not None and not self._timer.done()

    def _start(self, coro) -> None:
        if not self.is_running():
            self._timer = asyncio.create_task(coro)
        else:
            coro.close()

    def stop(self) -> None:
        """Stop the timer if it is not already running."""
        if self.is_running():
            self._timer.cancel()
        self._timer = None


class AsyncTimer(BaseAsyncTimer):
    """A timer that calls a callback after a specified time."""
    def start(self, callback: Callable, time_seconds: float) -> None:
        """Start the timer if it is not already running.

        Args:
            callback:
                The callback to call when the timer expires.
            time_seconds:
                The time in seconds to wait before calling the callback.
        """
        self._start(self._timer_callback(callback, time_seconds))

    @staticmethod
    async def _timer_callback(callback: Callable, time_seconds: float) -> None:
        await asyncio.sleep(time_seconds)
        await call_maybe_async(callback)


class AsyncRepeatingTimer(BaseAsyncTimer):
    """A timer that calls a callback repeatedly in a specified interval, optionally after waiting for a given date."""
    def start(self, callback: Callable, interval_seconds: float, start_date: Optional[datetime] = None) -> None:
        """Start the timer if it is not already running.

        Args:
            callback:
                The callback to call when the timer expires.
            interval_seconds:
                The repeat interval in seconds.
            start_date (optional):
                Date to wait for before starting the timer. Upon reaching the
                date, `callback` will be called immediately, then the timer
                loop starts.
                If `start_date` is `None`, the timer loop starts immediately,
                without calling `callback`.
                If `start_date` is in the past, the function acts as if the
                timer has been repeated since then and waits for the next
                expected interval. That means, it is safe to specify any date
                regardless if it is in the past.

        `start_date` is useful when you want to run a timer always at a specific date or time.
        For example, the following will run `callback` every day at 12:10:00.

            AsyncRepeatingTimer().start(callback, 24 * 60 * 60, datetime.now().replace(hour=12, minute=10, second=0))

        """
        self._start(self._timer_callback(callback, interval_seconds, start_date))

    @staticmethod
    async def _timer_callback(callback: Callable, interval_seconds: float, start_date: Optional[datetime]) -> None:
        if start_date is not None:
            delta = (start_date - datetime.now()).total_seconds()

            if delta < 0:
                # Assuming we started at start_date and repeated the timer since
                # then, how much do we need to wait for the next tick?
                # Python's wrap-around module comes in handy here.
                delta = int(delta) % interval_seconds

            await asyncio.sleep(delta)
            await call_maybe_async(callback)

        while True:
            await asyncio.sleep(interval_seconds)
            await call_maybe_async(callback)
