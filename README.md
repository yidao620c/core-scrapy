## Python网络爬虫Scrapy框架研究

### 实现功能：

#### 对多个医药网站的新闻文章的采集，主要功能实现如下：

  * 只采集最新的新闻文章
  * 采集的数据放入postgreSQL数据库中，并且包含标题，发布日期，文章来源，链接地址等等信息
  * URL去重复，程序保证对于同一个链接不会爬取两次
  * 防止封IP策略，如果抓取太频繁了，就被被封IP，目前采用三种策略保证不会被封：

     * 策略1：设置download_delay下载延迟，数字设置为5秒，越大越安全
     * 策略2： 禁止Cookie，某些网站会通过Cookie识别用户身份，禁用后使得服务器无法识别爬虫轨迹
     * 策略3： 使用user agent池。也就是每次发送的时候随机从池中选择不一样的浏览器头信息，防止暴露爬虫身份
     * 策略4：使用IP池，这个需要大量的IP资源，貌似还达不到这个要求
     * 策略5：分布式爬取，这个是针对大型爬虫系统的，对目前而言我们还用不到。

  * 针对RSS源的爬取
  * 对于每个新的爬取目标网站，或者原来的网站格式有变动的时候，需要做到可配置，
    只修改配置文件即可，而不是修改源文件，增加一段爬虫代码，主要是用xpath配置爬取规则
  * 定时爬取，设置定时任务周期性爬取
  * 与微信公共平台的结合，给大量的订阅号随机分配最新的订阅文章。

------------------------------------------

### 作者的话
Scrapy，Python开发的一个快速,高层次的屏幕抓取和web抓取框架，用于抓取web站点并从页面中提取结构化的数据。
Scrapy用途广泛，可以用于数据挖掘、监测和自动化测试。
Scrapy吸引人的地方在于它是一个框架，任何人都可以根据需求方便的修改。它也提供了多种类型爬虫的基类，
如BaseSpider、sitemap爬虫等，最新版本又提供了web2.0爬虫的支持。
Scrach，是抓取的意思，这个Python的爬虫框架叫Scrapy，大概也是这个意思吧，就叫它：小刮刮吧。

------------------------------------------


一个人毕竟精力有限，期待在GitHub上面找到合作者共同完善这个系统。可以fork这个工程然后提交Pull Requests。

## How to Contribute

You are welcome to contribute to core-scrapy as follow

* add/edit wiki
* report/fix issue
* code review
* commit new feature
* add testcase

Meanwhile you'd better follow the rules below

* It's *NOT* recommended to submit a pull request directly to `master` branch. `develop` branch is more appropriate
* Follow common Python coding conventions
* Add the following [license](#license) in each source file

## License

(The Apache License)

Copyright (c) 2011-2015 [WinHong, Inc.](http://www.winhong.com/) and other contributors

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, 
software distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and limitations under the License.
