# Scrapy教程12- 抓取动态网站

前面我们介绍的都是去抓取静态的网站页面，也就是说我们打开某个链接，它的内容全部呈现出来。
但是如今的互联网大部分的web页面都是动态的，经常逛的网站例如京东、淘宝等，商品列表都是js，并有Ajax渲染，
下载某个链接得到的页面里面含有异步加载的内容，这样再使用之前的方式我们根本获取不到异步加载的这些网页内容。

使用Javascript渲染和处理网页是种非常常见的做法，如何处理一个大量使用Javascript的页面是Scrapy爬虫开发中一个常见的问题，
这篇文章将说明如何在Scrapy爬虫中使用[scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash)来处理页面中得Javascript。

### scrapy-splash简介
scrapy-splash利用[Splash](https://github.com/scrapy/scrapy)将javascript和Scrapy集成起来，使得Scrapy可以抓取动态网页。

Splash是一个javascript渲染服务，是实现了HTTP API的轻量级浏览器，底层基于Twisted和QT框架，Python语言编写。所以首先你得安装Splash实例

### 安装docker
官网建议使用docker容器安装方式Splash。那么首先你得先安装docker

参考[官方安装文档](https://docs.docker.com/engine/installation/linux/ubuntulinux/)，这里我选择Ubuntu 12.04 LTS版本安装

升级内核版本，docker需要3.13内核
``` bash
$ sudo apt-get update
$ sudo apt-get install linux-image-generic-lts-trusty
$ sudo reboot
```

安装`CA`认证
``` bash
$ sudo apt-get install apt-transport-https ca-certificates
```

增加新的`GPG`key
``` bash
$ sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
```

打开`/etc/apt/sources.list.d/docker.list`，如果没有就创建一个，然后删除任何已存在的内容，再增加下面一句
```
deb https://apt.dockerproject.org/repo ubuntu-precise main
```

更新APT
``` bash
$ sudo apt-get update
$ sudo apt-get purge lxc-docker
$ apt-cache policy docker-engine
```

安装
``` bash
$ sudo apt-get install docker-engine
```

启动docker服务
``` bash
$ sudo service docker start
```

验证是否启动成功
``` bash
$ sudo docker run hello-world
```
上面这条命令会下载一个测试镜像并在容器中运行它，它会打印一个消息，然后退出。


### 安装Splash
拉取镜像下来
``` bash
$ sudo docker pull scrapinghub/splash
```

启动容器
``` bash
$ sudo docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
```

现在可以通过0.0.0.0:8050(http),8051(https),5023 (telnet)来访问Splash了。

### 安装scrapy-splash
使用pip安装
``` bash
$ pip install scrapy-splash
```

### 配置scrapy-splash
在你的scrapy工程的配置文件`settings.py`中添加
``` python
SPLASH_URL = 'http://192.168.203.92:8050'
```

添加Splash中间件，还是在`settings.py`中通过`DOWNLOADER_MIDDLEWARES`指定，并且修改`HttpCompressionMiddleware`的优先级
``` python
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
```
默认情况下，HttpProxyMiddleware的优先级是750，要把它放在Splash中间件后面

设置Splash自己的去重过滤器
``` python
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
```

如果你使用Splash的Http缓存，那么还要指定一个自定义的缓存后台存储介质，scrapy-splash提供了一个`scrapy.contrib.httpcache.FilesystemCacheStorage`的子类
``` python
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
```
如果你要使用其他的缓存存储，那么需要继承这个类并且将所有的`scrapy.util.request.request_fingerprint`调用替换成`scrapy_splash.splash_request_fingerprint`

### 使用scrapy-splash

#### SplashRequest
最简单的渲染请求的方式是使用`scrapy_splash.SplashRequest`，通常你应该选择使用这个
``` python
yield SplashRequest(url, self.parse_result,
    args={
        # optional; parameters passed to Splash HTTP API
        'wait': 0.5,

        # 'url' is prefilled from request url
        # 'http_method' is set to 'POST' for POST requests
        # 'body' is set to request body for POST requests
    },
    endpoint='render.json', # optional; default is render.html
    splash_url='<url>',     # optional; overrides SPLASH_URL
    slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
)
```

另外，你还可以在普通的scrapy请求中传递`splash`请求meta关键字达到同样的效果
``` python
yield scrapy.Request(url, self.parse_result, meta={
    'splash': {
        'args': {
            # set rendering arguments here
            'html': 1,
            'png': 1,

            # 'url' is prefilled from request url
            # 'http_method' is set to 'POST' for POST requests
            # 'body' is set to request body for POST requests
        },

        # optional parameters
        'endpoint': 'render.json',  # optional; default is render.json
        'splash_url': '<url>',      # optional; overrides SPLASH_URL
        'slot_policy': scrapy_splash.SlotPolicy.PER_DOMAIN,
        'splash_headers': {},       # optional; a dict with headers sent to Splash
        'dont_process_response': True, # optional, default is False
        'dont_send_headers': True,  # optional, default is False
        'magic_response': False,    # optional, default is True
    }
})
```

Splash API说明，使用`SplashRequest`是一个非常便利的工具来填充`request.meta['splash']`里的数据

* meta['splash']['args'] 包含了发往Splash的参数。
* meta['splash']['endpoint'] 指定了Splash所使用的endpoint，默认是[render.html](http://splash.readthedocs.org/en/latest/api.html#render-html)
* meta['splash']['splash_url'] 覆盖了`settings.py`文件中配置的Splash URL
* meta['splash']['splash_headers'] 运行你增加或修改发往Splash服务器的HTTP头部信息，注意这个不是修改发往远程web站点的HTTP头部
* meta['splash']['dont_send_headers'] 如果你不想传递headers给Splash，将它设置成True
* meta['splash']['slot_policy'] 让你自定义Splash请求的同步设置
* meta['splash']['dont_process_response'] 当你设置成True后，`SplashMiddleware`不会修改默认的`scrapy.Response`请求。默认是会返回`SplashResponse`子类响应比如`SplashTextResponse`
* meta['splash']['magic_response'] 默认为True，Splash会自动设置Response的一些属性，比如`response.headers`,`response.body`等

如果你想通过Splash来提交Form请求，可以使用`scrapy_splash.SplashFormRequest`，它跟`SplashRequest`使用是一样的。

#### Responses
对于不同的Splash请求，scrapy-splash返回不同的Response子类

* SplashResponse 二进制响应，比如对/render.png的响应
* SplashTextResponse 文本响应，比如对/render.html的响应
* SplashJsonResponse JSON响应，比如对/render.json或使用Lua脚本的/execute的响应

如果你只想使用标准的Response对象，就设置`meta['splash']['dont_process_response']=True`

所有这些Response会把`response.url`设置成原始请求URL(也就是你要渲染的页面URL)，而不是Splash endpoint的URL地址。实际地址通过`response.real_url`得到

#### Session的处理
Splash本身是无状态的，那么为了支持scrapy-splash的session必须编写Lua脚本，使用`/execute`
``` lua
function main(splash)
    splash:init_cookies(splash.args.cookies)

    -- ... your script

    return {
        cookies = splash:get_cookies(),
        -- ... other results, e.g. html
    }
end
```
而标准的scrapy session参数可以使用`SplashRequest`将cookie添加到当前Splash cookiejar中

### 使用实例
接下来我通过一个实际的例子来演示怎样使用，我选择爬取[京东网](http://www.jd.com/)首页的异步加载内容。

京东网打开首页的时候只会将导航菜单加载出来，其他具体首页内容都是异步加载的，下面有个"猜你喜欢"这个内容也是异步加载的，
我现在就通过爬取这个"猜你喜欢"这四个字来说明下普通的Scrapy爬取和通过使用了Splash加载异步内容的区别。

首先我们写个简单的测试Spider，不使用splash：
``` python
class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["jd.com"]
    start_urls = [
        "http://www.jd.com/"
    ]

    def parse(self, response):
        logging.info(u'---------我这个是简单的直接获取京东网首页测试---------')
        guessyou = response.xpath('//div[@id="guessyou"]/div[1]/h2/text()').extract_first()
        logging.info(u"find：%s" % guessyou)
        logging.info(u'---------------success----------------')
```
然后运行结果：
```
2016-04-18 14:42:44 test_spider.py[line:20] INFO ---------我这个是简单的直接获取京东网首页测试---------
2016-04-18 14:42:44 test_spider.py[line:22] INFO find：None
2016-04-18 14:42:44 test_spider.py[line:23] INFO ---------------success----------------
```
我找不到那个"猜你喜欢"这四个字

接下来我使用splash来爬取
``` python
import scrapy
from scrapy_splash import SplashRequest


class JsSpider(scrapy.Spider):
    name = "jd"
    allowed_domains = ["jd.com"]
    start_urls = [
        "http://www.jd.com/"
    ]

    def start_requests(self):
        splash_args = {
            'wait': 0.5,
        }
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_result, endpoint='render.html',
                                args=splash_args)

    def parse_result(self, response):
        logging.info(u'----------使用splash爬取京东网首页异步加载内容-----------')
        guessyou = response.xpath('//div[@id="guessyou"]/div[1]/h2/text()').extract_first()
        logging.info(u"find：%s" % guessyou)
        logging.info(u'---------------success----------------')
```
运行结果：
```
2016-04-18 14:42:51 js_spider.py[line:36] INFO ----------使用splash爬取京东网首页异步加载内容-----------
2016-04-18 14:42:51 js_spider.py[line:38] INFO find：猜你喜欢
2016-04-18 14:42:51 js_spider.py[line:39] INFO ---------------success----------------
```
可以看出结果里面已经找到了这个"猜你喜欢"，说明异步加载内容爬取成功！

