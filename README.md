# easyofd
#### 关于这个库：

鉴于目前python解析ofd没有啥好用的库所以决定自己整一个。

已实现功能 ：

1 解析ofd 

2 ofd转pdf 

3 ofd转图片

4 pdf转ofd-暂不支持电子解析

5 添加gui 工具实现上述功能

6 jpg2ofd jpg2pfd

关于 jb2格式图片解析 
使用了第三方库 jbig2dec 去读取jb2格式图片 参考下面链接安装使用jbig2dec 
https://github.com/rillian/jbig2dec 



​	

:hand:[实现参考文档](https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=3AF6682D939116B6F5EED53D01A9DB5D )

项目链接： https://github.com/renoyuan/easyofd



### 安装

```shell
pip install easyofd
```

ofd2pdf demo

test\demo.py

ps:

1 本库尚不完善使用需要谨慎，欢迎提各种Issue.

2 目前ofd 文件使用尚未普及，作者接触的文件也不多，遇到无法解析的文件，可以发我邮箱(renoyuan@foxmail.com)，有时间会去优化版本.


版本规划:

1.0 计划重点在ofd 解析模块的完善 及ofd文档格式的转换 ofd2pdf ofd2img 等

2.0 计划完成ofdd文件绘制 以及其他文档转ofd pdf2ofd txt2ofd 等 
