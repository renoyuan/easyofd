#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd read_seal_img
# CREATE_TIME: 2024/5/28 14:13
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from pyasn1.codec.der.decoder import decode
from pyasn1.type import univ, namedtype
# 定义一个通用的 SEQUENCE 结构
class UnknownSequence(univ.Sequence):
    componentType = namedtype.NamedTypes()
class sealSequence(univ.Sequence):
    componentType = namedtype.NamedTypes()

# 读取二进制文件
with open(r'F:\code\easyofd\test\1111_xml\Doc_0\Signs\Sign_0\SignedValue.dat', 'rb') as file:
    binary_data = file.read()

# 尝试解码为通用的 SEQUENCE 结构
try:
    decoded_data, _ = decode(binary_data, asn1Spec=UnknownSequence())
    # print(decoded_data.prettyPrint())
    print(dir(decoded_data))
    # print(decoded_data.isNoValue() )
    # print(decoded_data.values )
    # print(decoded_data.subtypeSpec )
    print(decoded_data.items )
except Exception as e:
    print(f"Decoding failed: {e}")