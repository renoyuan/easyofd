#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试注释解析器 AnnotationsParser & AnnotationFileParser"""

import pytest
from easyofd.parser_ofd.file_annotation_parser import (
    AnnotationsParser,
    AnnotationFileParser,
)


class TestAnnotationsParser:
    """测试 AnnotationsParser（注释入口文件解析）"""

    def test_empty_xml(self):
        """空 xml 应返回空字典"""
        parser = AnnotationsParser({"ofd:Annotations": {}})
        result = parser()
        assert result == {}

    def test_single_annotation(self):
        """单个注释入口解析"""
        xml_obj = {
            "ofd:Annotations": {
                "ofd:Page": {
                    "@PageID": "1",
                    "ofd:FileLoc": "Doc_0/Pages/Page_0/Content.xml",
                }
            }
        }
        parser = AnnotationsParser(xml_obj)
        result = parser()
        assert "1" in result
        assert result["1"]["pageNo"] == 0
        assert result["1"]["FileLoc"] == "Doc_0/Pages/Page_0/Content.xml"

    def test_multiple_annotations(self):
        """多个注释入口解析"""
        xml_obj = {
            "ofd:Annotations": {
                "ofd:Page": [
                    {
                        "@PageID": "1",
                        "ofd:FileLoc": "Doc_0/Pages/Page_0/Content.xml",
                    },
                    {
                        "@PageID": "2",
                        "ofd:FileLoc": "Doc_0/Pages/Page_1/Content.xml",
                    },
                ]
            }
        }
        parser = AnnotationsParser(xml_obj)
        result = parser()
        assert len(result) == 2
        assert result["1"]["pageNo"] == 0
        assert result["2"]["pageNo"] == 1

    def test_missing_page_id(self):
        """缺失 PageID 的条目应跳过"""
        xml_obj = {
            "ofd:Annotations": {
                "ofd:Page": [
                    {"ofd:FileLoc": "Doc_0/Pages/Page_0/Content.xml"},
                    {"@PageID": "2", "ofd:FileLoc": "Doc_0/Pages/Page_1/Content.xml"},
                ]
            }
        }
        parser = AnnotationsParser(xml_obj)
        result = parser()
        assert "2" in result
        assert len(result) == 1

    def test_missing_file_loc(self):
        """缺失 FileLoc 的条目应跳过"""
        xml_obj = {
            "ofd:Annotations": {
                "ofd:Page": {
                    "@PageID": "1",
                }
            }
        }
        parser = AnnotationsParser(xml_obj)
        result = parser()
        assert result == {}


class TestAnnotationFileParser:
    """测试 AnnotationFileParser（单注释文件解析）"""

    def test_empty_annotation(self):
        """空注释文件返回空字典"""
        parser = AnnotationFileParser({"ofd:Annotation": {}})
        result = parser()
        assert result == {}

    def test_stamp_annotation(self):
        """签章注释解析"""
        xml_obj = {
            "ofd:Annot": {
                "@ID": "177",
                "@Type": "Stamp",
                "ofd:Appearance": {
                    "@Boundary": "87.50 8.50 30 20",
                    "@CTM": "",
                    "ofd:ImageObject": {
                        "@ID": "177",
                        "@ResourceID": "176",
                        "@Boundary": "0 0 30 20",
                        "@CTM": "30 0 0 20 0 0",
                    },
                },
                "ofd:Content": {"@Text": ""},
            }
        }
        parser = AnnotationFileParser(xml_obj)
        result = parser()
        assert "177" in result
        assert result["177"]["AnnoType"]["type"] == "Stamp"
        assert result["177"]["Appearance"]["Boundary"] == "87.50 8.50 30 20"
        assert result["177"]["ImageObject"]["ResourceID"] == "176"

    def test_watermark_annotation(self):
        """水印注释解析"""
        xml_obj = {
            "ofd:Annot": {
                "@ID": "1",
                "@Type": "Watermark",
                "ofd:Appearance": {
                    "@Boundary": "0 0 595 842",
                    "ofd:TextObject": {"@Text": "SAMPLE WATERMARK"},
                },
                "ofd:Content": {"@Text": "watermark"},
            }
        }
        parser = AnnotationFileParser(xml_obj)
        result = parser()
        assert "1" in result
        assert result["1"]["AnnoType"]["type"] == "Watermark"
        assert result["1"]["Content"] == "watermark"

    def test_link_annotation(self):
        """链接注释解析"""
        xml_obj = {
            "ofd:Annot": {
                "@ID": "2",
                "@Type": "Link",
                "ofd:Appearance": {"@Boundary": "0 0 100 20"},
                "ofd:Content": {"@Text": "https://example.com"},
            }
        }
        parser = AnnotationFileParser(xml_obj)
        result = parser()
        assert "2" in result
        assert result["2"]["AnnoType"]["type"] == "Link"

    def test_unknown_annotation_type(self):
        """未知注释类型应标记为 unknown"""
        xml_obj = {
            "ofd:Annot": {
                "@ID": "3",
                "@Type": "UnknownType",
                "ofd:Appearance": {"@Boundary": "0 0 100 100"},
            }
        }
        parser = AnnotationFileParser(xml_obj)
        result = parser()
        assert result["3"]["AnnoType"] == "unknown"

    def test_multiple_annotations(self):
        """多个注释解析"""
        xml_obj = {
            "ofd:Annot": [
                {
                    "@ID": "1",
                    "@Type": "Stamp",
                    "ofd:Appearance": {"@Boundary": "0 0 30 20"},
                    "ofd:Content": {"@Text": ""},
                },
                {
                    "@ID": "2",
                    "@Type": "Watermark",
                    "ofd:Appearance": {"@Boundary": "0 0 595 842"},
                    "ofd:Content": {"@Text": "watermark"},
                },
            ]
        }
        parser = AnnotationFileParser(xml_obj)
        result = parser()
        assert len(result) == 2
        assert result["1"]["AnnoType"]["type"] == "Stamp"
        assert result["2"]["AnnoType"]["type"] == "Watermark"

    def test_text_object_in_annotation(self):
        """注释中的 TextObject 应正确解析"""
        xml_obj = {
            "ofd:Annot": {
                "@ID": "1",
                "@Type": "Stamp",
                "ofd:Appearance": {
                    "@Boundary": "0 0 100 50",
                    "ofd:TextObject": {
                        "@Text": "Signature",
                        "@Font": "SimSun",
                        "@Size": "12",
                    },
                },
                "ofd:Content": {"@Text": ""},
            }
        }
        parser = AnnotationFileParser(xml_obj)
        result = parser()
        assert "1" in result
        assert result["1"]["TextObject"] is not None
