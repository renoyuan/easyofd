# pyofdpaerser
安装
pip install pyofdpaerser

项目链接： https://github.com/renoyuan/pyofdpaerser

解析ofd 文件

1 输出坐标和文本信息图片解析
    文本信息包括字体，字号，颜色
    坐标信息包括文本块坐标和其偏移量
    
2 ofd 转pdf

3 新增对内嵌字体的转换 

demo
```
from pyofdpaerser,ofdpaser import OfdParser
# 转pdf输出
pdfbytes = OfdParser(ofdb64).ofd2pdf()

# print(data_dict)
# print(pdfbytes)
with open(f"pdfs/{name}.pdf","wb") as f:
    f.write(pdfbytes)
```



