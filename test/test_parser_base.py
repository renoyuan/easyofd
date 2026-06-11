"""
测试 FileParserBase 基础解析功能
"""
import pytest
from easyofd.parser_ofd.file_parser_base import FileParserBase
from easyofd.parser_ofd.parameter_parser import ParameterParser


class TestFileParserBase:
    """测试基础解析器"""

    def test_init_with_none_raises(self):
        """传入 None 应抛 ValueError"""
        import easyofd.parser_ofd.file_parser_base as fpb
        with pytest.raises(ValueError, match="xml_obj 不能为 None"):
            fpb.FileParserBase(None)

    def test_init_with_empty_dict(self):
        """传入空字典"""
        parser = FileParserBase({})
        assert parser.xml_obj == {}

    def test_recursion_ext_dict_key(self, sample_xml_obj):
        """递归抽取指定 key 的值（dict 类型）"""
        parser = FileParserBase(sample_xml_obj)
        result = []
        parser.recursion_ext(sample_xml_obj, result, "ofd:PublicRes")
        assert result == ["PublicRes.xml"]

    def test_recursion_ext_list_key(self, sample_xml_obj):
        """递归抽取指定 key 的值（list 类型）"""
        parser = FileParserBase(sample_xml_obj)
        result = []
        parser.recursion_ext(sample_xml_obj, result, "ofd:Page")
        assert len(result) == 2
        assert result[0]["@BaseLoc"] == "Pages/Page_1/Content.xml"

    def test_recursion_ext_nonexistent_key(self, sample_xml_obj):
        """不存在的 key 应返回空列表"""
        parser = FileParserBase(sample_xml_obj)
        result = []
        parser.recursion_ext(sample_xml_obj, result, "ofd:NonExistent")
        assert result == []

    def test_recursion_ext_nested_dict(self):
        """多层嵌套 dict 的抽取"""
        xml = {
            "root": {
                "level1": {
                    "level2": {
                        "target": "found_it"
                    }
                }
            }
        }
        parser = FileParserBase(xml)
        result = []
        parser.recursion_ext(xml, result, "target")
        assert result == ["found_it"]

    def test_recursion_ext_mixed_list_dict(self):
        """混合 list/dict 结构的抽取"""
        xml = {
            "root": {
                "items": [
                    {"name": "a", "value": 1},
                    {"name": "b", "value": 2},
                ]
            }
        }
        parser = FileParserBase(xml)
        result = []
        parser.recursion_ext(xml, result, "name")
        assert result == ["a", "b"]


class TestParameterParser:
    """测试参数解析器"""

    def test_parse_ctm(self):
        parser = ParameterParser()
        # 单位矩阵
        result = parser.parse_CTM("1 0 0 1 0 0")
        assert result == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    def test_parse_ctm_empty(self):
        parser = ParameterParser()
        result = parser.parse_CTM("")
        assert result == [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    def test_parse_boundary(self):
        parser = ParameterParser()
        result = parser.parse_Boundary("0 0 595 842")
        assert result == [0.0, 0.0, 595.0, 842.0]

    def test_parse_boundary_empty(self):
        parser = ParameterParser()
        result = parser.parse_Boundary("")
        assert result == []

    def test_parse_color(self):
        parser = ParameterParser()
        result = parser.parse_Color({"Value": "255 0 0"})
        assert result == (255, 0, 0)

    def test_parse_color_none(self):
        parser = ParameterParser()
        result = parser.parse_Color(None)
        assert result is None
