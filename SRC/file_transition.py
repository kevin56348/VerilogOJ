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


def getdatas(datas, datatype):
    # 定义输入输出列表
    signallist = [[] for i in range(2)]
    # 输入信号和输出信号的数量
    rowlenth = 0
    # 遍历data中的每一行，拿到所有信号
    for num in range(2):
        data_len = 0
        firstflag = True
        for eachline in datas[num]:
            data_len += 1
            if(data_len > glo.MAX_DATA and datatype == 0 and glo.waveType != 3):
                break

            if(firstflag):
                if (num == 0):
                    if datatype == 0:
                        glo.moni_first_line = eachline
                    else:
                        glo.disp_first_line = eachline
                # 先按逗号和冒号分割
                temp = re.split(',|:', eachline)
                if(num == 0):
                    rowlenth = len(temp)
                elif(rowlenth != len(temp)):
                    raise Exception
                # 再将按等号分割
                for each in temp:
                    listtem = each.split("=")
                    temp_signal = []
                    listtem[1] = listtem[1].replace(' ', '')
                    listtem[1] = listtem[1].replace('\n', '')
                    temp_signal.append(listtem[1])
                    signallist[num].append(temp_signal)
                firstflag = False

            else:
                temp = re.split(',|:', eachline)
                if(rowlenth != len(temp)):
                    raise Exception
                i = 0
                for each in temp:
                    listtem = each.split("=")
                    listtem[1] = listtem[1].replace(' ', '')
                    listtem[1] = listtem[1].replace('\n', '')
                    signallist[num][i].append(listtem[1])
                    i = i + 1
    return signallist


def splitdatas(datas):
    """得到信号的值的列表"""

    signallist_monitor = [[] for i in range(2)]
    signallist_display = [[] for i in range(2)]
    signallist_initial = [[] for i in range(2)]

    monitor = 'monitor'
    display = 'display'
    initial = 'initial'
    state = 0
    message = ""

    # 遍历data中的每一行，拿到所有信号
    try:
        for num in range(2):
            for eachline in datas[num]:
                p = eachline.find(monitor)
                if p == 0:
                    st = eachline.replace(monitor, '')
                    signallist_monitor[num].append(st)
                else:
                    p = eachline.find(initial)
                    if p == 0:
                        st = eachline.replace(initial, '')
                        signallist_initial[num].append(st)
                    else:
                        p = eachline.find(display)
                        if p == 0:
                            st = eachline.replace(display, '')
                            signallist_display[num].append(st)
                        else:
                            if(glo.display_flag):
                                raise Exception
        try:
            signallist_monitor = getdatas(signallist_monitor, 0)
        except Exception as e:
            state = 1
            message = "monitor 信号有误  " + str(e)
        # try:
        #     signallist_display = getdatas(
        #         signallist_display, 1) if glo.display_flag else []
        # except Exception as e:
        #     state = 1
        #     message = "display 信号有误" + str(e)
    except Exception as e:
        state = 1
        message = "信号解析有误" + str(e)
    if(glo.display_flag):
        if len(signallist_display[0]) == 0:
            state = 1
            message = "沒有display信號，無法評測"

    if(signallist_initial[0]):
        if(signallist_initial[0] != signallist_initial[1]):
            state = 1
            message = "未按要求进行模块初始化"

    return [signallist_monitor, signallist_display, state, message]


def getnames(names):
    """得到信号的名称列表"""
    signalname = [[] for i in range(2)]
    if names == '':
        return signalname
    type_temp = names.split(':')
    if(len(type_temp) == 1):
        glo.NoInputSignal = True
    i = 1 if glo.NoInputSignal else 0
    for each in type_temp:
        inlist = each.split(',')
        for each_inlist in inlist:
            name_temp = each_inlist.split('=')
            name = name_temp[0].replace(' ', '')
            name = name.replace('\n', '')
            signalname[i].append(name)
        i += 1
    return signalname


def gettypes(signallist):
    """得到信号类型，判断喜好是否是一位， false为多位， true为一位"""
    signaltype = [[] for i in range(2)]
    for i in range(2):
        j = 0
        for datalist in signallist[i]:
            signaltype[i].append(True)
            for each in datalist:
                if(each not in ['0', '1', 'x', 'z']):
                    signaltype[i][j] = False
                    break
            j += 1
    return signaltype
