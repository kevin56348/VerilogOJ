# param1 is thr path to exe
import sys
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import base64
import wavedrom
import json
from lxml import etree
import re

import config as glo
from file_transition import *
from format_transition import *


def deal_wave(lastErr):
    # 打开文件
    datas = []
    datas.append(open("/home/ojfiles/point"+str(lastErr)+"/teacher_result"))
    datas.append(open("/home/ojfiles/point"+str(lastErr)+"/student_result"))

    # 信号的值
    [signallist_monitor, signallist_display,
        state, message] = splitdatas(datas)

    if(state != 0):
        message += "   信号读取失败"
        return ["", "", state, message]

    jsonStr = ""
    svg_string = ""
    if(glo.showWave):
        # 信号的名称
        signalname_monitor = getnames(glo.moni_first_line)

        # 各个信号的类型
        signaltype_monitor = gettypes(signallist_monitor)

        # clk_fold=True表示clk可用p.....表示
        # clk_fold=False表示clk不可用p.....表示
        clk_fold = clk_change(signallist_monitor, signalname_monitor)

        # 转换为signal形式
        jsonStr = data_format(signallist_monitor, signalname_monitor, signaltype_monitor,
                              glo.waveType, glo.NoInputSignal, glo.combineSize, glo.hscale, clk_fold)

        svg = wavedrom.render(jsonStr)
        svg_string = svg.tostring()

    # 如果要显示分数，则返回结果分数
    grade = 0
    state = 0
    if(glo.display_flag):
        try:
            # signalname_display = getnames(glo.disp_first_line)
            grade = getgrade(signallist_display)
        except Exception as e:
            print(e)

    return [svg_string, int(grade), state, ""]
