#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
    Topic: sample
    Desc : 
"""
import sys, os, re
from scrapydemo.utils import filter_tags


class MM(object):
    def __init__(self):
        self.name = u"中文"
        self.age = 123


if __name__ == '__main__':
    aa = u'PhRMA\uff1a2013\u5e74\u65b0\u836f\u7814\u53d1\u6295\u8d44\u8d85511\u4ebf\u7f8e\u5143'
    print(aa.encode('utf-8'))

    a = {'a': 1}
    print(dict(a))
    print('aa b'.split(' ')[1])


