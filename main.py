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
    aa = """
    <div class="art_con" id="contentText">
            	<p>　　过去几年中，2013年是生物技术IPO市场最为繁荣的一年，有超过45家生物技术<a href="http://yqk.39.net/lz/yaochang/69dc9.html" target="_blank" keycmd="null">公司</a>进行IPO，募得资金总额超过30亿美元，用于支持管线中的药物。</p> <p>　　跨入2014年，生物技术IPO继续引爆资本市场，仅第一季度，就有29家生命科学公司上市，共募得21亿美元，而到了年中，便已经证明2014年比以往任何年份更加有利可图。不过，并不是所有公司都能顺利募集到预期资金。今年第二季度，有关一些生物技术巨头的药品定价问题及相关监管障碍所引发的市场忧虑，给整个行业带来了波动，这种恐慌情绪已迫使一些生物技术公司下调IPO价格及募集金额，同时也导致许多公司推迟IPO计划。</p><p>　　FierceBiotech对2014年IPO的生物技术公司进行了统计分析，根据募集资金总额及IPO后股价表现，评选出了2014年IPO最成功的10家生物技术公司。榜单如下：</p><p><strong>　　1、Ultragenyx Pharmaceutical ($RARE)</strong></p><p>　　总部：美国加州Novato；</p><p>　　IPO发行价：21美元；</p><p>　　9月30日收盘价：56.60美元；</p><p>　　变化：涨170%；</p><p>　　募集资金：1.22亿美元</p><p>　<strong>　2、ZS Pharma ($ZSPH)</strong></p><p>　　总部：美国德州Coppell；</p><p>　　IPO发行价：18美元；</p><p>　　9月30日收盘价：39.23美元；</p><p>　　变化：张118%；</p><p>　　募集资金：1.07亿美元</p><p>　<strong>　3、Auspex Pharmaceuticals ($ASPX)</strong></p><p>　　总部：美国加州La Jolla；</p><p>　　IPO发行价：12美元；</p><p>　　9月30日收盘价：25.67美元；</p><p>　　变化：涨114%；</p><p>　　募集资金：8400万美元</p><p>　　<strong>4、Avalanche Biotechnologies ($AAVL)</strong></p><p>　　总部：美国加州Menlo Park；</p><p>　　IPO发行价：17美元；</p><p>　　9月30日收盘价：34.19美元；</p><p>　　变化：涨101%；</p><p>　　募集资金：1.02亿美元</p><p>　<strong>　5、Sage Therapeutics ($SAGE)</strong></p><p>　　总部：美国马萨诸塞州Cambridge；</p><p>　　IPO发行价：18美元；</p><p>　　9月30日收盘价：31.50美元；</p><p>　　变化：涨75%；</p><p>　　募集资金：9000万美元</p><p>　<strong>　6、Kite Pharma（$KITE）</strong></p><p>　　总部：美国加州Cambridge；</p><p>　　IPO发行价：17美元；</p><p>　　9月30日收盘价：28.50美元；</p><p>　　变化：涨68%；</p><p>　　募集资金：1.28亿美元</p><p>　<strong>　7、Otonomy ($OTIC)</strong></p><p>　　总部：美国加州圣地亚哥San Diego；</p><p>　　IPO发行价：16美元；</p><p>　　9月30日收盘价：24美元；</p><p>　　变化：涨50%；</p><p>　　募集资金：1.00亿美元</p><p>　<strong>　8、Zafgen ($ZFGN)</strong></p><p>　　总部：美国加州圣地亚哥San Diego；</p><p>　　IPO发行价：16美元；</p><p>　　9月30日收盘价：19.65美元；</p><p>　　变化：涨23%；</p><p>　　募集资金：9600万美元</p><p>　<strong>　9、ProQR Therapeutics ($PRQR)</strong></p><p>　　总部：荷兰Leiden；</p><p>　　IPO发行价：13美元；</p><p>　　9月30日收盘价：17.19美元；</p><p>　　变化：涨32%；</p><p>　　募集资金：9800万美元</p><p><strong>　　10、Radius Health ($RDUS)</strong></p><p>　　总部：美国马萨诸塞州Waltham；</p><p>　　IPO发行价：8美元；</p><div class="hzh_botleft">
<!-- AFP Control Code/Caption.左下竖幅-->
<iframe src="http://dpvc.39.net/adpolestar/door/;ap=AA17FA45_6995_495D_8708_F89A733C753F;ct=if;pu=san9;/?" name="adFrame_AA17FA45_6995_495D_8708_F89A733C753F" width="200" height="300" frameborder="no" border="0" marginwidth="0" marginheight="0" scrolling="no">
&lt;SCRIPT LANGUAGE="JavaScript1.1"&gt;
var browVersion = parseInt(navigator.appVersion);
if (navigator.appName==\"Netscape\" &amp;&amp; browVersion&lt;=4) document.write("&lt;SCR"+"IPT LANGUAGE=\"Javascript1.1\" SRC=\"http://dpvc.39.net/adpolestar/door/;ap=AA17FA45_6995_495D_8708_F89A733C753F;ct=js;pu=san9;/?\"&gt;&lt;\/SCR"+"IPT&gt;");
&lt;/SCRIPT&gt;
</iframe>
<!-- AFP Control Code End/No.200-->
</div><p>　　9月30日收盘价：21美元；</p><p>　　变化：涨163%；</p><p>　　募集资金：5200万美元</p>
<script language="javascript">
if (!window.jQuery)
  document.write("<script language='javascript' src='http://image.39.net/hits/jquery-1.4.2.min.js'><\/script>");
</script>
<script language="javascript" src="http://image.39.net/js/linkTip.js"></script>
<script language="javascript">
   jQuery('a[keycmd]').art_ContentEvent({keycmd:'keycmd'});
</script>
</div>
    """
    pat1 = re.compile(r'<div class="hzh_botleft">(?:.|\n)*?</div>')
    pat2 = re.compile(r'<script (?:.|\n)*?</script>')
    aa = pat1.sub('', aa)
    aa = pat2.sub('', aa)
    aa = '\n'.join(s for s in aa.split('\n') if len(s.strip()) != 0)
    print(aa)


