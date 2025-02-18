#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd read_seal_img
# CREATE_TIME: 2024/5/28 14:13
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 根据 ASN.1 解析签章 拿到 签章图片
import io
import base64

from PIL import Image, UnidentifiedImageError
from loguru import logger
from pyasn1.codec.der.decoder import decode
from pyasn1.type import univ
from pyasn1.error import PyAsn1Error



class SealExtract(object):
    def __init__(self,):
        pass
    def read_signed_value(self, path="", b64=""):
        # 读取二进制文件
        if b64:
            binary_data = base64.b64decode(b64)
        elif path:
            # print("seal_path",path)
            with open(path, 'rb') as file:
                binary_data = file.read()
        else:
            return
        # 尝试解码为通用的 ASN.1 结构
        try:
            decoded_data, _ = decode(binary_data)
        except (PyAsn1Error,) as e:
            logger.warning(f"Decoding failed: {e}")
            decoded_data = None
        except (AttributeError,) as e:
            logger.warning(f"AttributeError failed: {e}")
            decoded_data = None
        finally:
           return  decoded_data


    def find_octet_strings(self, asn1_data,octet_strings:list):

        # 递归查找所有的 OctetString 实例

        if isinstance(asn1_data, univ.OctetString):

            octet_strings.append(asn1_data)
        elif isinstance(asn1_data, univ.Sequence) or isinstance(asn1_data, univ.Set):
            for component in asn1_data:
                self.find_octet_strings(asn1_data[f"{component}"], octet_strings)
        elif isinstance(asn1_data, univ.Choice):
            self.find_octet_strings(asn1_data.getComponent(), octet_strings)
        elif isinstance(asn1_data, univ.Any):
            try:
                sub_data, _ = decode(asn1_data.asOctets())
                self.find_octet_strings(sub_data, octet_strings)
            except PyAsn1Error:
                pass


    def hex_to_image(self, hex_data, image_format='PNG',inx=0):
        """
        将16进制数据转换为图片并保存。

        :param hex_data: 图片的16进制数据字符串
        :param image_format: 图片的格式，默认为'PNG'
        """
        # 将16进制数据转换为二进制数据

        binary_data = bytes.fromhex(hex_data)

        # 创建BytesIO对象以读取二进制数据
        image_stream = io.BytesIO(binary_data)

        # 使用Pillow打开图像数据并保存
        try:
            image = Image.open(image_stream)
            # image.save(f'{inx}_image.{image_format}', format=image_format)
            # print(f"图片已保存为'image.{image_format}'")
            return image
        except UnidentifiedImageError:
            logger.info("not img ")

    def __call__(self, path="", b64=""):

        decoded_data = self.read_signed_value(path=path, b64=b64)
        octet_strings = []
        img_list = []  # 目前是只有一个的，若存在多个的话关联后面考虑
        if decoded_data:
            self.find_octet_strings(decoded_data, octet_strings)

            for i, octet_string in enumerate(octet_strings):
                # logger.info(f"octet_string{octet_string}")
                if str(octet_string.prettyPrint()).startswith("0x"):

                    img = self.hex_to_image(str(octet_string.prettyPrint())[2:],inx= i)
                    if img:
                        logger.info("ASN.1 data found.")
                        img_list.append(img)
        else:
            logger.info("No valid ASN.1 data found.")

        return  img_list

if __name__=="__main__":
    print(SealExtract()(r"F:\code\easyofd\test\1111_xml\Doc_0\Signs\Sign_0\SignedValue.dat" ))

