#!usr/bin/env python
#-*- coding:utf-8 -*-

import hashlib


def hash_code(s, salt='young'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()