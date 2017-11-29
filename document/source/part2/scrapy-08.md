# Scrapy教程08- 文件与图片

Scrapy为我们提供了可重用的[item pipelines](http://doc.scrapy.org/en/1.0/topics/item-pipeline.html)为某个特定的Item去下载文件。
通常来说你会选择使用Files Pipeline或Images Pipeline。

这两个管道都实现了：

* 避免重复下载
* 可以指定下载后保存的地方(文件系统目录中,Amazon S3中)

Images Pipeline为处理图片提供了额外的功能：

* 将所有下载的图片格式转换成普通的JPG并使用RGB颜色模式
* 生成缩略图
* 检查图片的宽度和高度确保它们满足最小的尺寸限制

管道同时会在内部保存一个被调度下载的URL列表，然后将包含相同媒体的相应关联到这个队列上来，从而防止了多个item共享这个媒体时重复下载。

## 使用Files Pipeline
一般我们会按照下面的步骤来使用文件管道：

1. 在某个Spider中，你爬取一个item后，将相应的文件URL放入`file_urls`字段中
1. item被返回之后就会转交给item pipeline
1. 当这个item到达`FilesPipeline`时，在`file_urls`字段中的URL列表会通过标准的Scrapy调度器和下载器来调度下载，并且优先级很高，在抓取其他页面前就被处理。而这个`item`会一直在这个pipeline中被锁定，直到所有的文件下载完成。
1. 当文件被下载完之后，结果会被赋值给另一个`files`字段。这个字段包含一个关于下载文件新的字典列表，比如下载路径，源地址，文件校验码。`files`里面的顺序和`file_url`顺序是一致的。要是某个写文件下载出错就不会出现在这个`files`中了。

## 使用Images Pipeline
`ImagesPipeline`跟`FilesPipeline`的使用差不多，不过使用的字段名不一样，`image_urls`保存图片URL地址，`images`保存下载后的图片信息。

使用`ImagesPipeline`的好处是你可以通过配置来提供额外的功能，比如生成文件缩略图，通过图片大小过滤需要下载的图片等。

`ImagesPipeline`使用[Pillow](https://github.com/python-pillow/Pillow)来生成缩略图以及转换成标准的JPEG/RGB格式。因此你需要安装这个包，我们建议你使用Pillow而不是PIL。

## 使用例子
要使用媒体管道，请先在配置文件中打开它
``` python
# 同时使用图片和文件管道
ITEM_PIPELINES = {
                  'scrapy.pipelines.images.ImagesPipeline': 1,
                  'scrapy.pipelines.files.FilesPipeline': 2,
                 }
FILES_STORE = '/path/to/valid/dir'  # 文件存储路径
IMAGES_STORE = '/path/to/valid/dir' # 图片存储路径
# 90 days of delay for files expiration
FILES_EXPIRES = 90
# 30 days of delay for images expiration
IMAGES_EXPIRES = 30
# 图片缩略图
IMAGES_THUMBS = {
    'small': (50, 50),
    'big': (270, 270),
}
# 图片过滤器，最小高度和宽度
IMAGES_MIN_HEIGHT = 110
IMAGES_MIN_WIDTH = 110
```
一个使用了缩略图的下载例子会生成如下图片：
```
<IMAGES_STORE>/full/63bbfea82b8880ed33cdb762aa11fab722a90a24.jpg
<IMAGES_STORE>/thumbs/small/63bbfea82b8880ed33cdb762aa11fab722a90a24.jpg
<IMAGES_STORE>/thumbs/big/63bbfea82b8880ed33cdb762aa11fab722a90a24.jpg
```

然后，某个Item返回时，有`file_urls`或`image_urls`，并且存在相应的`files`或`images`字段

``` python
import scrapy

class MyItem(scrapy.Item):

    # ... other item fields ...
    image_urls = scrapy.Field()
    images = scrapy.Field()
```

## 自定义媒体管道
如果你还需要更加复杂的功能，想自定义下载媒体逻辑，请参考[扩展媒体管道](http://doc.scrapy.org/en/1.0/topics/media-pipeline.html#topics-media-pipeline-override)

不管是扩展`FilesPipeline`还是`ImagesPipeline`,都只需重写下面两个方法

* `get_media_requests(self, item, info)`,返回一个`Request`对象
* `item_completed(self, results, item, info)`,当上门的Request下载完成后回调这个方法，然后填充`files`或`images`字段

下面是一个扩展`ImagesPipeline`的例子，我只取path信息，并将它赋给`image_paths`字段，而不是默认的`images`
``` python
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item
```

