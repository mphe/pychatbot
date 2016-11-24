# -*- coding: utf-8 -*-

import os
import errno


def mkdir(path):
    try:
        os.mkdir(path)
    except OSError as e:
        if not(e.errno == errno.EEXIST and os.path.isdir(path)):
            raise

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if not(e.errno == errno.EEXIST and os.path.isdir(path)):
            raise

