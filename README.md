# easyofd
### 关于这个库：

鉴于目前python解析ofd没有啥好用的库所以决定自己整一个。

### 已实现功能 ：

1 解析ofd 

2 ofd转pdf 

3 ofd转图片

4 pdf转ofd  -暂不使用电子解析版本

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



### 使用 



参考 test\demo.py 文件 目前所有功能在这个里面都有体现



### ps:

0 代码使用有问题，可以先看 test\demo.py 文件

1 对于使用有任何疑问，欢迎提各种Issue.

2 目前ofd 文件使用尚未普及，作者接触的文件也不多，遇到无法解析的文件，可以发我邮箱(renoyuan@foxmail.com)，有时间会去优化版本.

3 本库对你有所帮助可以star 支持一下作者，或者fork。



### 版本规划:

1.0 计划提高解析的通用性，如果有解析失败的文件可以提供给作者优化这个工具库

1.1 pdf 转ofd 的电子解析版本优化，目前存在一些生成ofd电子版本 wps 无法正常解析的情况（图片版本不存在） ，有熟悉wps的同学希望也能提供一些建议

1.2 完善gui

