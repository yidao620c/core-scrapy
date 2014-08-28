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


if __name__ == '__main__':
    unicodeString = u"hello Unicode world!中文"
    utf8String = unicodeString.encode("UTF-8")
    print(unicodeString)
    print(utf8String)

    aa = u"\u4e60\u8fd1\u5e73\u66fe\u4e0b\u4e617\u5e74 \u4f4f\u7a91\u6d1e"
    print(aa.encode('UTF-8'))

    s = "关于百度" # 整个文件是UTF-8编码，所以这里的字符串也是UTF-8
    u = s.decode("utf-8") # 将utf-8的str转换为unicode
    print(u)
    g = u.encode('gb2312') # 将unicode转换为str，编码为GBK
    print(g)
    gg = g.decode('gb2312')  #将GBK的str转换为unicode
    print(gg)
    ggg = gg.encode('utf-8')
    print(ggg)



