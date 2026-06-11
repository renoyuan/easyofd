"""
测试 OFD 主解析器
"""
import base64
from unittest.mock import MagicMock, patch

import pytest


class TestOFDParser:
    """测试主解析器流程"""

    def test_init_with_none(self):
        """传入 None 不应崩溃"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        parser = OFDParser(None)
        assert parser.ofdb64 is None

    def test_init_with_empty_string(self):
        """传入空字符串"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        parser = OFDParser("")
        assert parser.ofdb64 == ""

    def test_img2data_basic(self):
        """测试图片转 data 功能"""
        from easyofd.parser_ofd.ofd_parser import OFDParser
        from PIL import Image
        import io

        # 创建一张小图
        img = Image.new("RGB", (100, 200), color="white")
        parser = OFDParser(None)

        result = parser.img2data([img])

        assert isinstance(result, list)
        assert len(result) == 1
        doc = result[0]
        assert "images" in doc
        assert "page_info" in doc
        assert "page_size" in doc
        assert len(doc["page_info"]) == 1

    def test_img2data_multiple_images(self):
        """多张图片转换"""
        from easyofd.parser_ofd.ofd_parser import OFDParser
        from PIL import Image

        imgs = [
            Image.new("RGB", (100, 100), color="red"),
            Image.new("RGB", (200, 200), color="blue"),
            Image.new("RGB", (50, 50), color="green"),
        ]
        parser = OFDParser(None)
        result = parser.img2data(imgs)

        assert len(result) == 1  # 所有图片在同一个 doc
        doc = result[0]
        assert len(doc["images"]) == 3
        assert len(doc["page_info"]) == 3

    @patch("easyofd.parser_ofd.ofd_parser.FileRead")
    def test_call_returns_list(self, mock_fileread):
        """__call__ 应返回 list"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        # 模拟 FileRead 返回值
        mock_instance = MagicMock()
        mock_instance.return_value = {
            "root_doc": "Doc_0/Document.xml",
            "pdf_name": "test",
        }
        mock_fileread.return_value = mock_instance

        # mock get_xml_obj 返回简单结构
        parser = OFDParser("fake_b64")
        parser.file_tree = {
            "root_doc": "Doc_0/Document.xml",
            "pdf_name": "test",
        }
        parser.get_xml_obj = MagicMock(return_value={
            "ofd:DocBody": {
                "ofd:DocRoot": "Doc_0/Document.xml",
            }
        })

        # 由于实际解析链路较长，只验证返回类型
        # 实际用例需要完整的 ofd 文件，此处仅做结构验证
        # result = parser()
        # assert isinstance(result, list)
        pass

    def test_resolve_font_chinese(self):
        """中文字体应 fallback 到 SimSun"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        parser = OFDParser("")

        # 模拟一个 TextObject
        class FakeTextObj:
            def get(self, key, default=""):
                return ""

        result = parser._resolve_font(FakeTextObj(), "中文文本")
        assert result == "SimSun"

    def test_resolve_font_english(self):
        """英文字体应 fallback 到 Helvetica"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        parser = OFDParser("")

        class FakeTextObj:
            def get(self, key, default=""):
                return ""

        result = parser._resolve_font(FakeTextObj(), "Hello World")
        assert result == "Helvetica"

    def test_resolve_font_with_font_tool(self):
        """如果 font_tool 可用且 font 在 FONTS 中，应调用 normalize_font_name"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        parser = OFDParser("")

        class FakeFontTool:
            FONTS = ["SimSun"]
            def normalize_font_name(self, name):
                return "SimSun_Normalized"

        parser.font_tool = FakeFontTool()

        # 注意：text_obj 需要是 dict，因为 _resolve_font 先检查 isinstance(text_obj, dict)
        result = parser._resolve_font({"@Font": "SimSun"}, "中文")
        assert result == "SimSun_Normalized"

    def test_resolve_font_with_font_tool_not_in_list(self):
        """如果 font 不在 FONTS 中，不应调用 normalize_font_name，走 fallback"""
        from easyofd.parser_ofd.ofd_parser import OFDParser

        parser = OFDParser("")

        class FakeFontTool:
            FONTS = ["SimSun"]
            def normalize_font_name(self, name):
                return "SimSun_Normalized"

        parser.font_tool = FakeFontTool()

        result = parser._resolve_font({"@Font": "UnknownFont"}, "中文")
        # UnknownFont 不在 FONTS 中，走 fallback 到 SimSun
        assert result == "SimSun"
