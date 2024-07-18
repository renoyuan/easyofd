#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd img_deal
# CREATE_TIME: 2024/7/18 11:20
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: img 操作
from io import BytesIO
class DealImg(object):
    def __init__(self):
        pass
    def resize(self):
        """resize img"""
        pass
    def pil2bytes(self, image):
        """pil2bytes"""
        # 创建一个 BytesIO 对象
        img_bytesio = BytesIO()
        # 将图像保存到 BytesIO 对象
        image.save(img_bytesio, format='PNG')  # 你可以根据需要选择其他图像格式
        # 获取 BytesIO 对象中的字节
        img_bytes = img_bytesio.getvalue()
        # 关闭 BytesIO 对象
        img_bytesio.close()
        return img_bytes
    def pil2bytes_io(self, image):
        """pil2bytes_io"""
        # 创建一个 BytesIO 对象
        img_bytesio = BytesIO()
        # 将图像保存到 BytesIO 对象
        image.save(img_bytesio, format='PNG')  # 你可以根据需要选择其他图像格式
        return img_bytesio



