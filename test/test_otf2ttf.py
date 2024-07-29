#!/usr/bin/env python3

from fontTools.ttLib import TTFont

# 输入和输出文件的路径
input_otf_file = r"F:\code\easyofd\test\2_xml\Doc_0\Res\font_1.woff"
output_ttf_file = "font_1.ttf"

# 加载 OTF 字体文件
font = TTFont(input_otf_file)
print(font.keys())
# 转换 OTF 到 TTF
font.saveXML("temp.xml")  # 保存为 XML，用于转换
font.flavor = "woff"     # 更改 flavor 以触发转换
font.importXML("temp.xml")
# font.flavor = "ttf"      # 设置最终输出的格式为 TTF

# if 'CFF ' in font:
#     del font['CFF ']
# 保存为 TTF 字体文件
font.save(output_ttf_file)

# 清理临时文件
import os
# os.remove("temp.xml")

