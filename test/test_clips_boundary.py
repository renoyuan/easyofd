#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: easyofd/test
#CREATE_TIME: 2026-10-22
#AUTHOR: Kissshot-2003
#note:  裁剪路径缺少 Boundary 时，文本对象解析不应中断（issue #90）

import os
import sys

import xmltodict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easyofd.parser_ofd.file_content_parser import ContentFileParser

# issue #90 里的脱敏最小结构：Path 有 AbbreviatedData，但没有 @Boundary
XML_WITHOUT_BOUNDARY = """<?xml version="1.0" encoding="UTF-8"?>
<ofd:TextObject ID="10" Boundary="10 10 120 20" Font="1" Size="5"
    xmlns:ofd="http://www.ofdspec.org/2016">
  <ofd:Clips>
    <ofd:Clip>
      <ofd:Area>
        <ofd:Path Stroke="false" Fill="true">
          <ofd:AbbreviatedData>
            S 0 290 L 210 290 L 210 0 L 0 0 C
          </ofd:AbbreviatedData>
        </ofd:Path>
      </ofd:Area>
    </ofd:Clip>
  </ofd:Clips>
  <ofd:TextCode X="0" Y="0">Sample text</ofd:TextCode>
</ofd:TextObject>
"""

# 同样的结构，但 Path 带了 @Boundary，用来确认修复没有把正常的裁剪路径也一起放过
XML_WITH_BOUNDARY = """<?xml version="1.0" encoding="UTF-8"?>
<ofd:TextObject ID="11" Boundary="10 10 120 20" Font="1" Size="5"
    xmlns:ofd="http://www.ofdspec.org/2016">
  <ofd:Clips>
    <ofd:Clip>
      <ofd:Area>
        <ofd:Path Stroke="false" Fill="true" Boundary="0 0 210 290">
          <ofd:AbbreviatedData>
            S 0 290 L 210 290 L 210 0 L 0 0 C
          </ofd:AbbreviatedData>
        </ofd:Path>
      </ofd:Area>
    </ofd:Clip>
  </ofd:Clips>
  <ofd:TextCode X="0" Y="0">Sample text</ofd:TextCode>
</ofd:TextObject>
"""


def fetch(xml):
    doc = xmltodict.parse(xml)
    row = doc["ofd:TextObject"]
    parser = ContentFileParser(row)
    return parser.fetch_cell_info(row, row["ofd:TextCode"])


if __name__ == "__main__":
    # 缺少 Boundary：解析要继续，只是拿不到裁剪区域
    cell = fetch(XML_WITHOUT_BOUNDARY)
    assert cell["text"] == "Sample text", cell
    assert cell["pos"] == [10.0, 10.0, 120.0, 20.0], cell
    assert "clips_pos" not in cell, cell
    print("OK  clip path without Boundary is skipped, the text object still parses")

    # 带着 Boundary：裁剪区域照常解析出来
    cell = fetch(XML_WITH_BOUNDARY)
    assert cell["clips_pos"] == [0.0, 0.0, 210.0, 290.0], cell
    print("OK  clip path with Boundary still parses")

    print("all checks passed")
