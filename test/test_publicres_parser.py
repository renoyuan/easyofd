#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 PublicResFileParser（公共资源解析-字体/DrawParam）"""

import pytest
from easyofd.parser_ofd.file_publicres_parser import PublicResFileParser


class TestPublicResFileParser:
    """测试 PublicResFileParser"""

    def test_empty_xml(self):
        """空 xml 应返回含空子字典的字典"""
        parser = PublicResFileParser({"ofd:PublicRes": {}})
        result = parser()
        assert isinstance(result, dict)
        assert "font" in result
        assert "drawparams" in result
        assert result["font"] == {}
        assert result["drawparams"] == {}

    def test_single_font(self):
        """单个字体解析"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:Font": {
                    "@ID": "font0",
                    "@FontName": "SimSun",
                    "@FamilyName": "宋体",
                    "@Bold": "false",
                    "ofd:FontFile": "Doc_0/Res/font_0.ttf",
                }
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert "font0" in result["font"]
        font = result["font"]["font0"]
        assert font["FontName"] == "SimSun"
        assert font["FontNameORI"] == "SimSun"
        assert font["FontFile"] == "Doc_0/Res/font_0.ttf"
        assert font["Bold"] == "false"

    def test_multiple_fonts(self):
        """多个字体解析"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:Font": [
                    {
                        "@ID": "font0",
                        "@FontName": "SimSun",
                        "@FamilyName": "宋体",
                        "ofd:FontFile": "Doc_0/Res/font_0.ttf",
                    },
                    {
                        "@ID": "font1",
                        "@FontName": "KaiTi",
                        "@FamilyName": "楷体",
                        "ofd:FontFile": "Doc_0/Res/font_1.ttf",
                    },
                ]
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert len(result["font"]) == 2
        assert result["font"]["font0"]["FontName"] == "SimSun"
        assert result["font"]["font1"]["FontName"] == "KaiTi"

    def test_font_normalize_name(self):
        """字体名规范化"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:Font": {
                    "@ID": "font0",
                    "@FontName": "Times New Roman Bold",
                    "@FamilyName": "Times New Roman",
                }
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert result["font"]["font0"]["FontName"] == "TimesNewRoman-Bold"
        # FamilyName 也被 normalize，"Times New Roman" -> "TimesNewRoman" -> "Times-Roman"
        assert result["font"]["font0"]["FamilyName"] == "Times-Roman"

    def test_font_times_new_roman(self):
        """TimesNewRoman 特殊处理"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:Font": {
                    "@ID": "font0",
                    "@FontName": "TimesNewRoman",
                    "@FamilyName": "TimesNewRoman",
                }
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert result["font"]["font0"]["FontName"] == "Times-Roman"

    def test_draw_params(self):
        """DrawParam 解析"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:DrawParam": {
                    "@ID": "dp0",
                    "@LineWidth": "1.5",
                    "ofd:StrokeColor": {
                        "@Value": "0 0 0",
                        "@ColorSpace": "0",
                    },
                    "ofd:FillColor": {
                        "@Value": "255 0 0",
                        "@ColorSpace": "0",
                    },
                }
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert "dp0" in result["drawparams"]
        dp = result["drawparams"]["dp0"]
        assert dp["LineWidth"] == "1.5"
        assert dp["StrokeColor"]["value"] == ["0", "0", "0"]
        assert dp["FillColor"]["value"] == ["255", "0", "0"]

    def test_multiple_draw_params(self):
        """多个 DrawParam 解析"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:DrawParam": [
                    {
                        "@ID": "dp0",
                        "@LineWidth": "1.0",
                        "ofd:StrokeColor": {"@Value": "0 0 0", "@ColorSpace": "0"},
                        "ofd:FillColor": {"@Value": "0 0 0", "@ColorSpace": "0"},
                    },
                    {
                        "@ID": "dp1",
                        "@LineWidth": "2.0",
                        "ofd:StrokeColor": {"@Value": "255 0 0", "@ColorSpace": "0"},
                        "ofd:FillColor": {"@Value": "0 255 0", "@ColorSpace": "0"},
                    },
                ]
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert len(result["drawparams"]) == 2
        assert result["drawparams"]["dp0"]["LineWidth"] == "1.0"
        assert result["drawparams"]["dp1"]["LineWidth"] == "2.0"

    def test_font_non_string_name(self):
        """非字符串字体名的处理"""
        xml_obj = {
            "ofd:PublicRes": {
                "ofd:Font": {
                    "@ID": "font0",
                    "@FontName": None,
                }
            }
        }
        parser = PublicResFileParser(xml_obj)
        result = parser()
        assert result["font"]["font0"]["FontName"] == ""
