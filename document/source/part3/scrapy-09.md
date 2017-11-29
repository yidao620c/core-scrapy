# Scrapy教程09- 部署

本篇主要介绍两种部署爬虫的方案。如果仅仅在开发调试的时候在本地部署跑起来是很容易的，不过要是生产环境，爬虫任务量大，并且持续时间长，那么还是建议使用专业的部署方法。主要是两种方案：

* [Scrapyd](http://doc.scrapy.org/en/1.0/topics/deploy.html#deploy-scrapyd) 开源方案
* [Scrapy Cloud](http://doc.scrapy.org/en/1.0/topics/deploy.html#deploy-scrapy-cloud) 云方案


## 部署到Scrapyd
[Scrapyd](http://doc.scrapy.org/en/1.0/topics/deploy.html#deploy-scrapyd)是一个开源软件，用来运行蜘蛛爬虫。它提供了HTTP API的服务器，还能运行和监控Scrapy的蜘蛛

要部署爬虫到Scrapyd，需要使用到[scrapyd-client](https://github.com/scrapy/scrapyd-client)部署工具集，下面我演示下部署的步骤

Scrapyd通常以守护进程daemon形式运行，监听spider的请求，然后为每个spider创建一个进程执行`scrapy crawl myspider`,同时Scrapyd还能以多进程方式启动，通过配置`max_proc`和`max_proc_per_cpu`选项

### 安装
使用pip安装
``` bash
pip install scrapyd
```
在ubuntu系统上面
``` bash
apt-get install scrapyd
```

### 配置
配置文件地址，优先级从低到高

* /etc/scrapyd/scrapyd.conf (Unix)
* /etc/scrapyd/conf.d/* (in alphabetical order, Unix)
* scrapyd.conf
* ~/.scrapyd.conf (users home directory)

具体参数参考[scrapyd配置](http://scrapyd.readthedocs.org/en/latest/config.html)

简单的例子
```
[scrapyd]
eggs_dir    = eggs
logs_dir    = logs
items_dir   =
jobs_to_keep = 5
dbs_dir     = dbs
max_proc    = 0
max_proc_per_cpu = 4
finished_to_keep = 100
poll_interval = 5
bind_address = 0.0.0.0
http_port   = 6800
debug       = off
runner      = scrapyd.runner
application = scrapyd.app.application
launcher    = scrapyd.launcher.Launcher
webroot     = scrapyd.website.Root

[services]
schedule.json     = scrapyd.webservice.Schedule
cancel.json       = scrapyd.webservice.Cancel
addversion.json   = scrapyd.webservice.AddVersion
listprojects.json = scrapyd.webservice.ListProjects
listversions.json = scrapyd.webservice.ListVersions
listspiders.json  = scrapyd.webservice.ListSpiders
delproject.json   = scrapyd.webservice.DeleteProject
delversion.json   = scrapyd.webservice.DeleteVersion
listjobs.json     = scrapyd.webservice.ListJobs
daemonstatus.json = scrapyd.webservice.DaemonStatus
```

### 部署
使用[scrapyd-client](https://github.com/scrapy/scrapyd-client)最方便，
Scrapyd-client是[scrapyd](https://github.com/scrapy/scrapyd)的一个客户端，它提供了`scrapyd-deploy`工具将工程部署到Scrapyd服务器上面

通常将你的工程部署到Scrapyd需要两个步骤：

1. 将工程打包成python蛋，你需要安装[setuptools](http://pypi.python.org/pypi/setuptools)
1. 通过[addversion.json](https://scrapyd.readthedocs.org/en/latest/api.html#addversion-json)终端将蟒蛇蛋上传至Scrapd服务器

你可以在你的工程配置文件`scrapy.cfg`定义Scrapyd目标
```
[deploy:example]
url = http://scrapyd.example.com/api/scrapyd
username = scrapy
password = secret
```
列出所有可用目标使用命令
```
scrapyd-deploy -l
```
列出某个目标上面所有可运行的工程，执行命令
```
scrapyd-deploy -L example
```
先`cd`到工程根目录，然后使用如下命令来部署：
```
scrapyd-deploy <target> -p <project>
```
你还可以定义默认的target和project，省的你每次都去敲代码
```
[deploy]
url = http://scrapyd.example.com/api/scrapyd
username = scrapy
password = secret
project = yourproject
```
这样你就直接取执行
```
scrapyd-deploy
```
如果你有多个target，那么可以使用下面命令将project部署到多个target服务器上面
```
scrapyd-deploy -a -p <project>
```

## 部署到Scrapy Cloud
[Scrapy Cloud](http://scrapinghub.com/scrapy-cloud/)是一个托管的云服务器，由Scrapy背后的公司[Scrapinghub](http://scrapinghub.com/)维护

它免除了安装和监控服务器的需要，并提供了非常美观的UI来管理各个Spider，还能查看被抓取的Item，日志和状态等。

你可以使用[shub](http://doc.scrapinghub.com/shub.html)命令行工具来讲spider部署到Scrapy Cloud。更多请参考[官方文档](http://doc.scrapinghub.com/scrapy-cloud.html)

Scrapy Cloud和Scrapyd是兼容的，你可以根据需要在两者之前切换，配置文件也是`scrapy.cfg`，跟`scrapyd-deploy`读取的是一样的。
