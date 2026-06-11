"""
pytest 共享 fixture
"""
import os
import base64
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent


def load_ofd_b64(filename: str) -> str:
    """从 test/fixtures 目录加载 ofd 文件并转为 base64"""
    fixture_path = PROJECT_DIR / "test" / "fixtures" / filename
    if not fixture_path.exists():
        pytest.skip(f"缺少测试文件: {fixture_path}")
    with open(fixture_path, "rb") as f:
        return str(base64.b64encode(f.read()), "utf-8")


# ==========================
#  Fixtures
# ==========================

@pytest.fixture
def ofd_parser():
    """返回一个可用的 OFDParser 实例"""
    from easyofd.parser_ofd.ofd_parser import OFDParser
    return OFDParser


@pytest.fixture
def simple_ofd_b64():
    """简单的 ofd 文件（仅用于结构解析测试）"""
    return load_ofd_b64("simple.ofd")


@pytest.fixture
def sample_xml_obj():
    """简单的 xml 字典对象，用于 parser base 测试"""
    return {
        "ofd:Document": {
            "ofd:Page": [
                {"@ID": "1", "@BaseLoc": "Pages/Page_1/Content.xml"},
                {"@ID": "2", "@BaseLoc": "Pages/Page_2/Content.xml"},
            ],
            "ofd:PublicRes": "PublicRes.xml",
            "ofd:DocumentRes": "DocumentRes.xml",
        }
    }
