# -*- coding: utf-8 -*-

import chatbot.api as api
from threading import Timer


class TestAPI(api.APIBase):
    def __init__(self):
        super(TestAPI, self).__init__()
        # Fires a message received event every second
        self._timer = None

    def attach(self):
        self._start_timer()

    def detach(self):
        self._timer.cancel()

    def version(self):
        return "42.0"

    def api_name(self):
        return "Test API"

    def _timer_func(self):
        self._start_timer()
        msg = TestingMessage("TestAPI", "Test message")
        self._trigger(api.APIEvents.Message, msg)

    def _start_timer(self):
        self._timer = Timer(1, self._timer_func)
        self._timer.start()



class TestingMessage(api.ChatMessage):
    def __init__(self, author, text):
        self._text = text
        self._author = author

    def get_text(self):
        return self._text

    def get_author(self):
        return self._author

    def is_editable():
        return False

    def edit(self, newstr):
        raise NotImplementedError
