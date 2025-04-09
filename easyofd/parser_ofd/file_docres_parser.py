#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_docres_parser.py
# CREATE_TIME: 2025/3/28 11:48
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 解析 DocumentRes

import os

from .file_parser_base import FileParserBase

class DocumentResFileParser(FileParserBase):
    """
    Parser DocumentRes 抽取里面图片信息
    /xml_dir/Doc_0/DocumentRes.xml
    """

    def __call__(self):
        info = {}
        muti_media: list = []
        muti_media_key = "ofd:MultiMedia"
        self.recursion_ext(self.xml_obj, muti_media, muti_media_key)
        if muti_media:
            for media in muti_media:
                name = media.get("ofd:MediaFile", "")
                info[media.get("@ID")] = {
                    "format": media.get("@Format", ""),
                    "wrap_pos": media.get("@wrap_pos", ""),
                    # "Boundary": media.get("@Boundary", ""),
                    "type": media.get("@Type", ""),
                    "suffix": os.path.splitext(name)[-1].replace(".", ""),  # 文件后缀名
                    "fileName": name,
                }
        return info