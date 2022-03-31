#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Identifiable:
    @property
    def id(self) -> str:
        """Returns a unique ID."""
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        return False
