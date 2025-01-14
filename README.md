# easyofd


## 关于这个库：

鉴于目前python解析ofd没有啥好用的库所以决定自己整一个。

若本库对你有所帮助可以star 支持一下开源作者，欢迎fork，欢迎issues。



### 更新
20250114 - v0.4.2 对绘制部分做了优化，换了新的绘制方式，解决了一些绘制不全的问题，对于一些特殊的ofd文件可能会有绘制不全的问题，后续会继续优化。
20241204 - v0.4.1.99 对文件内相对路径做了处理，新增了对tif 和gif 格式文件处理
  目前ofd2pdf支持图片的格式有jpg jpeg png jb2 bmp tif gif 均转为jpg 展示

20240911 - v0.4.0 新增参数校验器 parameter_parser.py 中的参数需要在后续版本中完善。
20240909- v0.3.6 兼容更多text格式.

v0.3.5 兼容 ofd 文件 page size 不一的情况。 



v0.3.4.99 从该版本开始会增加对低版本python版本的兼容(最低3.8.18) ， 带有99 标识的版本代表发布前对python 3.8 有做兼容性验证。

  

v0.3.3 解决了一些bug ，去除了对opencv的依赖 环境体积减少50M左右，后续可能会尝试把一些依赖改为选装按需安装。


### 常见问题

目前一些常见使用问题包括 easyofd库如何下载怎么使用， linux系统缺少字体包怎么处理等常见问题后续会放到下面链接遇到后可以先看这个：

https://github.com/renoyuan/easyofd/wiki/FAQ



### 版本规划

1 环境，后续可能会尝试减少一些第三包的依赖压缩环境体积 -- 主要是opencv 和numpy

2 功能上 对于pfd2ofd 和 ofd 生成 可能会有一些优化

3 需求收集，若有其他相关easyofd 的需求和建议可以git 上给我提，有意思的需求我会考虑尝试。



### 关于提问-重要


:hand: 有疑问或者建议需求等等，优先看看FAQ文档和demo代码，没有的请提交issues，不要直接发邮件，不要直接发邮件。

:hand: 有啥问题在 github 上提 issues，有空的时候会尽力解答以及优化。邮箱只接受问题文件不做回复。

:hand: 解析错误的ofd文件请发我邮箱，github 不支持上传ofd文件。需要分析问题的，ofd文件很重要。 





## 已实现功能 ：

1 解析ofd 

2 ofd转pdf  转图片

3 pdf转ofd   转图片 

4 jpg2ofd jpg2pfd

5 添加gui 工具实现上述功能










## 使用 

### 安装

```shell
pip install easyofd
```



### 使用 



参考 test\demo.py 文件 目前所有功能在这个里面都有体现



### ps:

0 代码使用有问题，可以先看 test\demo.py 文件

1 对于使用有任何疑问，欢迎提各种Issue.

2 目前ofd 文件使用尚未普及，作者接触的文件也不多，遇到无法解析的文件，可以发我邮箱(renoyuan@foxmail.com)，有时间会去优化版本.

3 本库对你有所帮助可以star 支持一下作者，或者fork。

:hand:[参考文档实现](https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=3AF6682D939116B6F5EED53D01A9DB5D )

项目链接： https://github.com/renoyuan/easyofd





