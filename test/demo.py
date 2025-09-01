#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: F:\code\easyofd\test
# CREATE_TIME: 2023-10-18
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# note:  use demo
import base64
import os
import sys

from PIL import Image
from PIL.Image import Image as ImageClass

project_dir = os.path.join(os.path.dirname(os.getcwd()), "easyofd")
pkg_dir = os.path.dirname(os.getcwd())
print(project_dir)
print(pkg_dir)
sys.path.insert(0, project_dir)
sys.path.insert(0, pkg_dir)

from easyofd.ofd import OFD


# 
def test_img2(dir_path):
    """
    jpg2ofd 
    jpg2pfd
    """
    # img_path = os.path.join(".", r"test\Doc_0\Res") # 多页排序问题
    imgs_p = os.listdir(dir_path)
    imgs = []
    for img_p in imgs_p:
        imgs.append(Image.open(os.path.join(dir_path, img_p)))  # 传入改为pil
    ofdbytes = OFD().jpg2ofd(imgs)
    pdfbytes = OFD().jpg2pfd(imgs)
    with open(r"img2test.pdf", "wb") as f:
        f.write(pdfbytes)
    with open(r"img2test.ofd", "wb") as f:
        f.write(ofdbytes)


def test_ofd2(file_path):
    """
    ofd2pdf
    ofd2img
    """
    # with open(r"0e7ff724-1011-4544-8464-ea6c025f6ade.ofd","rb") as f:

    file_prefix = os.path.splitext(os.path.split(file_path)[1])[0]
    with open(file_path, "rb") as f:
        ofdb64 = str(base64.b64encode(f.read()), "utf-8")
    ofd = OFD()  # 初始化OFD 工具类
    ofd.read(ofdb64, save_xml=True, xml_name=f"{file_prefix}_xml")  # 读取ofdb64
    # print("ofd.data", ofd.data) # ofd.data 为程序解析结果
    pdf_bytes = ofd.to_pdf()  # 转pdf
    img_np = ofd.to_jpg()  # 转图片
    ofd.del_data()

    with open(f"{file_prefix}.pdf", "wb") as f:
        f.write(pdf_bytes)

    for idx, img in enumerate(img_np):
        # im = Image.fromarray(img)
        img.save(f"{file_prefix}_{idx}.jpg")


def test_pdf2(file_path):
    """
    pdf2ofd
    pdf2img
    """
    file_prefix = os.path.splitext(os.path.split(file_path)[1])[0]
    with open(file_path, "rb") as f:
        pdfb64 = f.read()
    ofd = OFD()
    ofd_bytes = ofd.pdf2ofd(pdfb64, optional_text=False)  # 转ofd # optional_text 生成可操作文本 True 输入也需要可编辑pdf
    img_np = ofd.pdf2img(pdfb64)
    ofd.del_data()
    with open(f"{file_prefix}.ofd", "wb") as f:
        f.write(ofd_bytes)
    for idx, img in enumerate(img_np):
        img.save(f"{file_prefix}_{idx}.jpg")


if __name__ == "__main__":

    file_path = rf"F:\opensource\easyofd\test\data\滴滴电子发票C.ofd"
    # file_path = r"data/2.ofd"
    if sys.argv[1] == "ofd2":
        test_ofd2(file_path)
    elif sys.argv[1] == "pdf2":
        test_pdf2(file_path)
    elif sys.argv[1] == "img2":
        test_img2(file_path)
    else:
        test_ofd2(file_path)

    # data = ofd.data
    # json.dump(data,open("data.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
    # print(ofd.data)
