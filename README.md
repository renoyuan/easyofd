# easyofd


## 关于这个库：

鉴于目前python解析ofd没有啥好用的库所以决定自己整一个。

若本库对你有所帮助可以star 支持一下开源作者，欢迎fork，欢迎issues。



### 更新

v0.3.3 解决了一些bug ，去除了对opencv的依赖 环境体积减少50M左右，后续可能会尝试把一些依赖改为选装按需安装。


### 常见问题

目前一些常见使用问题包括 easyofd库如何下载怎么使用， linux系统缺少字体包怎么处理等常见问题后续会放到下面链接遇到后可以先看这个：

https://github.com/renoyuan/easyofd/wiki/FAQ



### 版本规划:

1 环境，后续可能会尝试减少一些第三包的依赖压缩环境体积 -- 主要是opencv 和numpy

2 功能上 对于pfd2ofd 和 ofd 生成 可能会有一些优化

3 需求收集，若有其他相关easyofd 的需求和建议可以git 上给我提，有意思的需求我会考虑尝试。



## 已实现功能 ：

1 解析ofd 

2 ofd转pdf  转图片

3 pdf转ofd   转图片 

4 jpg2ofd jpg2pfd

5 添加gui 工具实现上述功能






关于 jb2格式图片解析 
使用了第三方库 jbig2dec 去读取jb2格式图片 参考下面链接安装使用jbig2dec 
https://github.com/rillian/jbig2dec 


:hand: 有疑问或者建议需求等等，优先看看文档和demo代码，没有的请提交issues，不要直接发邮件，不要直接发邮件。

:hand: 有啥问题在 github 上提 issues，有空的时候会尽力解答以及优化。邮箱只接受问题文件不做回复。

​	

:hand:[参考文档实现](https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=3AF6682D939116B6F5EED53D01A9DB5D )

项目链接： https://github.com/renoyuan/easyofd

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








