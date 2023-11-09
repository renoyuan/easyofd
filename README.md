# easyofd
#### 关于这个库：

鉴于目前python解析ofd没有啥好用的库所以决定自己整一个。

已实现功能 ：

1 解析ofd 

2 ofd转pdf 

3 ofd转图片

4 pdf转ofd-暂不支持电子解析

5 添加gui 工具实现上述功能

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
```python
#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-18 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  use demo
import sys
import os
project_dir = os.path.join(os.path.dirname(os.getcwd()),"easyofd")
pkg_dir = os.path.dirname(os.getcwd())
sys.path.insert(0,project_dir)
sys.path.insert(0,pkg_dir)
import base64
from PIL import Image

import numpy as np

from easyofd.ofd import OFD

if __name__ == "__main__":
    with open(r"增值税电子专票5.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    ofd = OFD()
    ofd.read(ofdb64) # 读取ofd
    # print(ofd.data)
    pdf_bytes = ofd.to_pdf() # 转pdf
    img_np = ofd.to_jpg() # 转图片
    ofd.del_data()
    with open(r"test.pdf","wb") as f:
        f.write(pdf_bytes)
    for idx, img in enumerate(img_np):
        im = Image.fromarray(img)
        im.save(f"test_img{idx}.jpg")
       
```



ps:

1 本库尚不完善使用需要谨慎，欢迎提各种Issue.

2 目前ofd 文件使用尚未普及，作者接触的文件也不多，遇到无法解析的文件，可以发我邮箱(renoyuan@foxmail.com)，有时间会去优化版本.



版本规划:

1.0 计划重点在ofd 解析模块的完善 及ofd文档格式的转换 ofd2pdf ofd2img 等

2.0 计划完成ofdd文件绘制 以及其他文档转ofd pdf2ofd txt2ofd 等 

