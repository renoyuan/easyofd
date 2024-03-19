#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd bmp2jpg
# CREATE_TIME: 2024/3/19 11:57
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from PIL import Image

# 打开 BMP 图像
bmp_image = Image.open(r"F:\code\easyofd\test\testxml\Doc_0\Res\image_3.bmp")

# 将 BMP 图像保存为 JPG 格式
bmp_image.convert("RGB").save("output_image.jpg", "JPEG")

# 关闭图像
bmp_image.close()
