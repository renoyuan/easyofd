#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_annotation_parser.py
# CREATE_TIME: 2025/3/28 14:12
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 注释解析

from .file_parser_base import FileParserBase

class AnnotationFileParser(FileParserBase):
    """
    Parser Annotation
    签名 注释 信息 水印
    """
    AnnoType = {
        "Watermark":{
            "name":"水印",
            "type":"Watermark"
        },
        "Link": {
            "name": "链接",
            "type": "Link"
        }
        ,
        "Path": {
            "name": "路径",
            "type": "Path"
        },
        "Highlight": {
            "name": "高亮",
            "type": "Highlight"
        },
        "Stamp": {
            "name": "签章",
            "type": "Highlight"
        }
    }

    def __call__(self):
        info = {}
        public_res: list = []
        public_res_key = "ofd:Font"
        self.recursion_ext(self.xml_obj, public_res, public_res_key)

        if public_res:
            for i in public_res:
                info[i.get("@ID")] = {
                    "FontName": self.normalize_font_name(i.get("@FontName")),
                    "FontNameORI": i.get("@FontName"),
                    "FamilyName": self.normalize_font_name(i.get("@FamilyName")),
                    "FamilyNameORI": i.get("@FamilyName"),
                    "Bold": i.get("@Bold"),
                    "Serif": i.get("@Serif"),
                    "FixedWidth": i.get("@FixedWidth"),
                    "FontFile": i.get("ofd:FontFile"),
                }
        return info

