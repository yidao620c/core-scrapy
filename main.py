#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
    Topic: sample
    Desc : 
"""
import sys, os

class MM(object):
    def __init__(self):
        self.name = u"\u4e60\u8fd1\u5e73\u66fe\u4e0b\u4e617\u5e74 \u4f4f\u7a91\u6d1e"
        self.age = 123

def to_utf8(item):
    for each_attr, each_val in item.__dict__.items():
        if isinstance(each_val, unicode):
            setattr(item, each_attr, each_val.encode('utf-8'))
        elif hasattr(each_val, '__iter__'):
            setattr(item, each_attr, [v.encode('utf-8') for v in each_val])

if __name__ == '__main__':
    unicodeString = u"hello Unicode world!中文"
    utf8String = unicodeString.encode("UTF-8")
    print(unicodeString)
    print(utf8String)

    aa = u"\u4e60\u8fd1\u5e73\u66fe\u4e0b\u4e617\u5e74 \u4f4f\u7a91\u6d1e"
    print(aa.encode('UTF-8'))

    mm = MM()
    to_utf8(mm)
    print(mm.name)

    from urlparse import urljoin
    print(urljoin('http://www.wingarden.net/', '/News/products.html'))



