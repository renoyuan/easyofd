#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-27 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  解析ofd xml 所有 文件下可能的节点 子节点 和属性
import xmltodict
ofdjson = {
    "ofd:OFD": {
        "@xmlns:ofd": "http://www.ofdspec.org/2016",
        "@Version": "1.1",
        "@DocType": "OFD",
        "ofd:DocBody": {
            "ofd:DocInfo": {
                "ofd:DocID": "0C1D4F7159954EEEDE517F7285E84DC4",
                "ofd:Creator": "HTFoxit",
                "ofd:CreatorVersion": "1.0",
                "ofd:CreationDate": "2023-10-27"
            },
            "ofd:DocRoot": ["Doc_0/Document.xml"]
        }
    }
}

xml_data = xmltodict.unparse(ofdjson, pretty=True)
print(xml_data)