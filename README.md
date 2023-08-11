# easyofd
#### 关于这个库：

鉴于目前python解析ofd没有啥好用的库所以决定自己整一个。

目前版本 0.0.9 已实现功能 ：

​	1 解析ofd 

​		已支持 

​			1 文本解析 

​			2 图片解析

​		暂不支持

​			其他

​	2 ofd转pdf 

:hand:[实现参考文档](https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=3AF6682D939116B6F5EED53D01A9DB5D )

项目链接： https://github.com/renoyuan/easyofd

### 安装

```shell
pip install easyofd
```



ofd2pdf demo
```python
import sys
import os
import base64

project_dir = os.path.join(os.path.dirname(os.getcwd()),"easyofd")
sys.path.insert(0,project_dir)
print(project_dir)
from main import OFD2PDF

if __name__ == "__main__":
    with open(r"增值税电子专票5.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    pdf_bytes = OFD2PDF()(ofdb64)
    with open(r"test.pdf","wb") as f:
        ofdb64 = f.write(pdf_bytes)
       
```



ps:

1 本库尚不完善使用需要谨慎，欢迎提各种Issue.

2 目前ofd 文件使用尚未普及，作者接触的文件也不多，遇到无法解析的文件，可以发我邮箱(renoyuan@foxmail.com)，有时间会去优化版本.



版本规划:

1.0 计划重点在ofd 解析模块的完善 及ofd文档格式的转换 ofd2pdf ofd2img 等

2.0 计划完成ofdd文件绘制 以及其他文档转ofd pdf2ofd txt2ofd 等 

