#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
    Topic: sample
    Desc : 
"""
import sys, os, re, io
from scrapydemo.utils import filter_tags
import uuid


class MM(object):
    def __init__(self):
        self.name = u"中文"
        self.age = 123


class Nth(object):
    """
    如果 sub 函数的第二个参数是个函数，则每次匹配到的时候都会执行这个函数。
    函数接受匹配到的那个 match object 作为参数，返回用来替换的字符串。
    利用这个特性就可以只在第 N 次匹配的时候返回要替换成的字符串，其他时候原样返回不做替换即可。
    """

    def __init__(self, nth, replacement):
        self.nth = nth
        self.replacement = replacement
        self.calls = 0

    def __call__(self, matchobj):
        self.calls += 1
        if self.calls == self.nth:
            return matchobj.group(1) + self.replacement
        return matchobj.group(0)

if __name__ == '__main__':
    aa = """
    <div class="art_con" id="contentText">
    """
    pat1 = re.compile(r'<div class="hzh_botleft">(?:.|\n)*?</div>')
    pat2 = re.compile(r'<script (?:.|\n)*?</script>')
    aa = pat1.sub('', aa)
    aa = pat2.sub('', aa)
    aa = '\n'.join(s for s in aa.split('\n') if len(s.strip()) != 0)
    print(type(uuid.uuid4().hex))
    print(uuid.uuid4().hex)
    uuids = ['{0:02d}{1:s}'.format(k, uuid.uuid4().hex) for k in range(1, 4)]
    print(uuids)
    with io.open('data.txt', encoding='utf-8') as dtf:
        dt = dtf.read()
    # 特殊构造，不作为分组
    # (?=...)之后的字符串需要匹配表达式才能成功匹配
    # (?<=...)之前的字符串需要匹配表达式才能成功匹配
    pat_img = re.compile(r'(<img (?:.|\n)*?src=")(.|\n)*?(?=")')
    for indx, val in enumerate(uuids):
        dt = pat_img.sub(Nth(indx + 1, val), dt)
    print(dt)

    print(os.path.basename('http://i2.sinaimg.cn/ty/2014/1017/U8567P6DT20141017003130.jpg').split('.')[-1])



