## Python网络爬虫Scrapy框架研究

### Scrapy1.0教程

* [Scrapy笔记（1）- 入门篇](https://www.xncoding.com/2016/03/08/scrapy-01.html)
* [Scrapy笔记（2）- 完整示例](https://www.xncoding.com/2016/03/10/scrapy-02.html)
* [Scrapy笔记（3）- Spider详解](https://www.xncoding.com/2016/03/12/scrapy-03.html)
* [Scrapy笔记（4）- Selector详解](https://www.xncoding.com/2016/03/14/scrapy-04.html)
* [Scrapy笔记（5）- Item详解](https://www.xncoding.com/2016/03/16/scrapy-05.html)
* [Scrapy笔记（6）- Item Pipeline](https://www.xncoding.com/2016/03/18/scrapy-06.html)
* [Scrapy笔记（7）- 内置服务](https://www.xncoding.com/2016/03/19/scrapy-07.html)
* [Scrapy笔记（8）- 文件与图片](https://www.xncoding.com/2016/03/20/scrapy-08.html)
* [Scrapy笔记（9）- 部署](https://www.xncoding.com/2016/03/21/scrapy-09.html)
* [Scrapy笔记（10）- 动态配置爬虫](https://www.xncoding.com/2016/04/10/scrapy-10.html)
* [Scrapy笔记（11）- 模拟登录](https://www.xncoding.com/2016/04/12/scrapy-11.html)
* [Scrapy笔记（12）- 抓取动态网站](https://www.xncoding.com/2016/04/15/scrapy-12.html)

### Wiki
Scrapy是Python开发的一个快速,高层次的屏幕抓取和web抓取框架，用于抓取web站点并从页面中提取结构化的数据。
Scrapy用途广泛，可以用于数据挖掘、监测和自动化测试。

Scrapy吸引人的地方在于它是一个框架，任何人都可以根据需求方便的修改。它也提供了多种类型爬虫的基类，
如BaseSpider、sitemap爬虫等，还有对web2.0爬虫的支持。

Scrach是抓取的意思，这个Python的爬虫框架叫Scrapy，大概也是这个意思吧，就叫它：小刮刮吧。

基于最新的Scrapy 1.0编写

------------------------------------------

### 对多个内容网站的采集，主要功能实现如下：

  * 最新文章列表的爬取
  * 采集的数据放入MySQL数据库中，并且包含标题，发布日期，文章来源，链接地址等等信息
  * URL去重复，程序保证对于同一个链接不会爬取两次
  * 防止封IP策略，如果抓取太频繁了，就被被封IP，目前采用三种策略保证不会被封：

     * 策略1：设置download_delay下载延迟，数字设置为5秒，越大越安全
     * 策略2：禁止Cookie，某些网站会通过Cookie识别用户身份，禁用后使得服务器无法识别爬虫轨迹
     * 策略3：使用user agent池。也就是每次发送的时候随机从池中选择不一样的浏览器头信息，防止暴露爬虫身份
     * 策略4：使用IP池，这个需要大量的IP资源，貌似还达不到这个要求
     * 策略5：分布式爬取，这个是针对大型爬虫系统的，对目前而言我们还用不到。

  * 模拟登录后的爬取
  * 针对RSS源的爬取
  * 对于每个新的爬取目标网站，或者原来的网站格式有变动的时候，需要做到可配置，
    只修改配置文件即可，而不是修改源文件，增加一段爬虫代码，主要是用xpath配置爬取规则
  * 定时爬取，设置定时任务周期性爬取
  * 与微信公共平台的结合，给大量的订阅号随机分配最新的订阅文章。
  * 利用scrapy-splash执行页面javascript后的内容爬取

------------------------------------------

## 贡献代码

1. Fork
1. 创建您的特性分支 git checkout -b my-new-feature
1. 提交您的改动 git commit -am 'Added some feature'
1. 将您的修改记录提交到远程 git 仓库 git push origin my-new-feature
1. 然后到 github 网站的该 git 远程仓库的 my-new-feature 分支下发起 Pull Request

## 许可证
Copyright (c) 2014-2016 [Xiong Neng](https://www.xncoding.com/)

基于 MIT 协议发布: <http://www.opensource.org/licenses/MIT>

