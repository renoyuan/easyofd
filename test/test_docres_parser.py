#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 DocumentResFileParser（文档资源解析）"""

import pytest
from easyofd.parser_ofd.file_docres_parser import DocumentResFileParser


class TestDocumentResFileParser:
    """测试 DocumentResFileParser"""

    def test_empty_xml(self):
        """空 xml 应返回空字典"""
        parser = DocumentResFileParser({"ofd:DocumentRes": {}})
        result = parser()
        assert result == {}

    def test_single_image(self):
        """单个图片资源解析"""
        xml_obj = {
            "ofd:DocumentRes": {
                "ofd:MultiMedia": {
                    "@ID": "img0",
                    "@Format": "jpg",
                    "@Type": "Image",
                    "ofd:MediaFile": "Doc_0/Res/image_0.jpg",
                }
            }
        }
        parser = DocumentResFileParser(xml_obj)
        result = parser()
        assert "img0" in result
        assert result["img0"]["format"] == "jpg"
        assert result["img0"]["type"] == "Image"
        assert result["img0"]["suffix"] == "jpg"
        assert result["img0"]["fileName"] == "Doc_0/Res/image_0.jpg"

    def test_multiple_images(self):
        """多个图片资源解析"""
        xml_obj = {
            "ofd:DocumentRes": {
                "ofd:MultiMedia": [
                    {
                        "@ID": "img0",
                        "@Format": "jpg",
                        "@Type": "Image",
                        "ofd:MediaFile": "Doc_0/Res/image_0.jpg",
                    },
                    {
                        "@ID": "img1",
                        "@Format": "png",
                        "@Type": "Image",
                        "ofd:MediaFile": "Doc_0/Res/image_1.png",
                    },
                ]
            }
        }
        parser = DocumentResFileParser(xml_obj)
        result = parser()
        assert len(result) == 2
        assert result["img0"]["suffix"] == "jpg"
        assert result["img1"]["suffix"] == "png"

    def test_image_with_different_suffix(self):
        """不同格式图片资源"""
        xml_obj = {
            "ofd:DocumentRes": {
                "ofd:MultiMedia": [
                    {
                        "@ID": "jb2img",
                        "@Format": "jb2",
                        "@Type": "Image",
                        "ofd:MediaFile": "Doc_0/Res/image_0.jb2",
                    },
                    {
                        "@ID": "bmpimg",
                        "@Format": "bmp",
                        "@Type": "Image",
                        "ofd:MediaFile": "Doc_0/Res/image_1.bmp",
                    },
                ]
            }
        }
        parser = DocumentResFileParser(xml_obj)
        result = parser()
        assert result["jb2img"]["suffix"] == "jb2"
        assert result["bmpimg"]["suffix"] == "bmp"

    def test_image_no_extension(self):
        """无后缀文件名的处理"""
        xml_obj = {
            "ofd:DocumentRes": {
                "ofd:MultiMedia": {
                    "@ID": "img0",
                    "@Format": "jpg",
                    "@Type": "Image",
                    "ofd:MediaFile": "Doc_0/Res/image_without_ext",
                }
            }
        }
        parser = DocumentResFileParser(xml_obj)
        result = parser()
        assert result["img0"]["suffix"] == ""
