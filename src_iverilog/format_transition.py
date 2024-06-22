import json
import pickle

# import config as glo

class wave:
    # wave类
    def __init__(self, name, wave, data=""):
        # print("-----\n%s\n %s\n %s\n-------\n" % (name, wave, data))
        self.wave = {}
        self.wave["name"] = name
        self.wave["wave"] = wave
        if (data != "" and data != ['']):
            self.wave["data"] = data


def to_wave(name, signal, data, signaltype, clk_fold=False):
    if signaltype:
        if name == 'clk' and clk_fold:
            # 时钟用p.......的方式做优化
            len_datalist = len(signal)
            signal = ['.'] * len_datalist
            signal[0] = 'p'
        temp = wave(name, ''.join(signal))
    else:
        temp = wave(name, ''.join(data), signal)
    return temp


def getmismatch(signallist, signalname, mismatch):
    '''把每个信号分别对比得到mismatch，之后根据不同的输出方式选择不同的输出方式'''
    len_input = len(signalname[0])
    len_output = len(signalname[1])

    # 给mismatch赋值
    for i in range(len_output):
        len_datalist = len(signallist[0][i+len_input])
        for j in range(len_datalist):
            # 保证
            if j >= len(signallist[1][i + len_input]):
                mismatch[i + len_input][j] = '1'
                continue
            if signallist[0][i + len_input][j] == signallist[1][i + len_input][j]:
                mismatch[i + len_input][j] = '0'
            else:
                mismatch[i + len_input][j] = '1'


def makewave(signallist, signalname, signaltype, signalwavedata, mismatch, NoInputSignal, is_together, clk_fold):
    '''拼接需要的json字符串'''
    len_input = len(signalname[0])
    len_output = len(signalname[1])
    len_datalist = len(signallist[0][len_input])

    signal = []

    if NoInputSignal == False:
        # print("有输入")
        # print(signalname)
        waves = []
        waves.append("Input")
        for i, name in enumerate(signalname[0]):
            temp = to_wave(
                name, signallist[0][i], signalwavedata[0][i], signaltype[0][i], clk_fold)

            waves.append(temp.wave)
        signal.append(waves)
        signal.append({})
    if is_together:
        # 老师的和学生的共同对比显示，
        # print("没有输入")
        for i, name in enumerate(signalname[1]):
            waves = []
            waves.append(name)
            for p in range(2):
                name = "YOURS" if p == 1 else "REF"
                temp = to_wave(
                    name, signallist[p][i+len_input], signalwavedata[p][i + len_input], signaltype[p][i + len_input])

                waves.append(temp.wave)
            signal.append(waves)
            data_change(mismatch[i+len_input], '', True)
            temp = wave('mismatch', ''.join(mismatch[i+len_input]))
            signal.append(temp.wave)
            signal.append({})
    else:
        # 老师的学生的分开显示
        # print("没有输入")
        for p in range(2):
            name = "YOURS" if p == 1 else "REF"
            waves = []
            waves.append(name)
            for i, name in enumerate(signalname[1]):
                temp = to_wave(name, signallist[p][i + len_input],
                               signalwavedata[p][i + len_input], signaltype[p][i + len_input])

                waves.append(temp.wave)
            signal.append(waves)
            signal.append({})
        mismatch2 = []
        len_mismatch = len(mismatch[len_input])
        for i in range(len_mismatch):
            flag = '0'
            for j in range(len_output):
                if mismatch[j+len_input][i] == '1':
                    flag = '1'
                    break
                if mismatch[j + len_input][i] == '|':
                    flag = '|'
                    break
            if flag:
                mismatch2.append(flag)
            else:
                mismatch2.append(flag)

        data_change(mismatch2, [], True)
        temp = wave('mismatch', ''.join(mismatch2))
        signal.append(temp.wave)
        signal.append({})
    return signal


def data_change(signal, data, signaltype):
    '''此函数作用是去除毛刺'''
    # 把连续的不能压缩的地方用'.'代替，起到去除毛刺的效果
    # print(signal)
    # print(data)
    # print(signaltype)
    if signaltype:
        len_datalist = len(signal)
        for i in range(len_datalist-1, 0, -1):
            if (signal[i] == signal[i - 1] and signal[i] != '|') or (signal[i] != '|' and signal[i - 1] == '|'):
                signal[i] = '.'
    else:
        len_datalist = len(signal)
        for i in range(len_datalist - 1, 0, -1):
            if (signal[i] == signal[i - 1] and data[i] != '|'):
                data[i] = '.'
    # print(signal)
    # print(data)


def data_delete(signal, data, signaltype):
    """此函数作用是去掉多余的'|'"""

    if signaltype:
        len_datalist = len(signal)
        for i in range(len_datalist - 1, 0, -1):
            if (signal[i] == signal[i - 1] and signal[i] == '|'):
                del signal[i]
    else:
        len_datalist = len(signal)
        for i in range(len_datalist - 1, 0, -1):
            if (data[i] in ['|', '.']):
                del signal[i]
                if data[i] == '|' and data[i - 1] == '|':
                    del data[i]
    pass


def data_transition(signallist, signalname, signaltype, signalwavedata, mismatch):
    '''把所有压缩后的数据进行优化处理'''

    len_input = len(signalname[0])
    len_output = len(signalname[1])
    len_datalist = len(signallist[0][len_input])

    for p in range(2):
        for i in range(len_input+len_output):
            try:
                if signalname[0][0] == 'clk' and i == 0:
                    continue
            except Exception:
                pass
            if signaltype[p][i]:
                data_change(signallist[p][i], [], True)
            else:
                data_change(signallist[p][i], signalwavedata[p][i], False)
    for j in range(len_output):
        data_delete(mismatch[j+len_input], [], True)
    for p in range(2):
        for j in range(len_output + len_input):
            if signaltype[p][j]:
                data_delete(signallist[p][j], [], True)
            else:
                data_delete(signallist[p][j], signalwavedata[p][j], False)


def data_fold(signallist, signalname, signaltype, signalwavedata, mismatch, count_list, NoInputSignal, combineSize):
    '''压缩数据'''
    # print(signallist)
    # print(signalwavedata)

    len_input = len(signalname[0])
    len_output = len(signalname[1])
    len_datalist = len(signallist[0][len_input])
    rangej = []
    if NoInputSignal:
        # 处理无输入信号
        rangej = range(len_input, len_input + len_output)
    else:
        # 处理有输入信号
        rangej = range(0, len_input + len_output)

    len_same = 0
    for i in range(len_datalist):
        flag = True
        for j in rangej:
            # 时钟信号变化在压缩时可忽略
            if j == 0 and signalname[0][j] == 'clk':
                continue
            if (i != 0 and
                    signallist[0][j][i] != signallist[0][j][i - 1]):
                flag = False
                break
            if i >= len(signallist[1][j]):
                flag = False
                break
            if (i != 0 and
                    signallist[1][j][i] != signallist[1][j][i - 1]):
                flag = False
                break
        if flag:
            len_same += 1
        else:
            # print(len_same)
            # print(i)
            if len_same >= combineSize:
                # 压缩刚循环过的连续的一段，把可以压缩的部分全部先用‘|’代替
                for p in range(2):
                    for j in rangej:
                        mismatch[j][i - len_same +
                                    1: i-1] = ['|'] * (len_same - 2)

                        if signaltype[p][j]:
                            signallist[p][j][i - len_same +
                                             1: i-1] = ['|'] * (len_same - 2)
                        else:
                            signalwavedata[p][j][i - len_same +
                                                 1: i-1] = ['|'] * (len_same - 2)
                count_list[i-len_same+1: i-1] = ['|']*(len_same-2)

            len_same = 0
    else:
        # 处理循环结束后，最后一段可以压缩的情况
        # print(len_same)
        # print(i)
        if len_same >= combineSize:
            for p in range(2):
                for j in rangej:
                    mismatch[j][i - len_same + 2: i] = ['|']*(len_same-2)
                    if signaltype[p][j]:
                        signallist[p][j][i - len_same +
                                         2: i] = ['|']*(len_same-2)
                    else:
                        signalwavedata[p][j][i - len_same +
                                             2: i] = ['|'] * (len_same - 2)
            count_list[i-len_same+2:i] = ['|']*(len_same-2)
        len_same = 0
    # print(signallist)
    # print(signalwavedata)
    pass


def data_format_0(signallist, signalname, signaltype, signalwavedata, mismatch, NoInputSignal, clk_fold):
    '''老师和学生的输出信号单独对比，'''
    data_transition(signallist, signalname, signaltype,
                    signalwavedata, mismatch)

    signal = makewave(signallist, signalname, signaltype,
                      signalwavedata, mismatch, NoInputSignal, True, clk_fold)
    return signal


def data_format_1(signallist, signalname, signaltype, signalwavedata, mismatch, NoInputSignal, clk_fold):
    '''老师和学生的输出信号整体对比'''
    data_transition(signallist, signalname, signaltype,
                    signalwavedata, mismatch)
    signal = makewave(signallist, signalname, signaltype,
                      signalwavedata, mismatch, NoInputSignal, False, clk_fold)
    return signal


def data_format_2(signallist, signalname, signaltype, signalwavedata, mismatch, count_list, NoInputSignal, combineSize,  clk_fold):
    '''加入输入和输出放一起进行压缩后的整体对比'''
    len_input = len(signalname[0])
    len_output = len(signalname[1])
    len_datalist = len(signallist[0][len_input])

    # print(signallist)

    data_fold(signallist, signalname, signaltype, signalwavedata,
              mismatch, count_list, NoInputSignal, combineSize)

    # print(signallist)
    # print(signalwavedata)
    data_transition(signallist, signalname, signaltype,
                    signalwavedata, mismatch)

    data_delete(count_list, '', True)
    for i, name in enumerate(count_list):
        if name == '|':
            count_list[i] = '...'
    # print(signallist)
    # print(signalwavedata)
    signal = makewave(signallist, signalname, signaltype,
                      signalwavedata, mismatch, NoInputSignal, False, clk_fold)

    return signal


def cut(signallist, signalname, signaltype):
    '''将错误部分的前后15个拿出来单独处理'''
    len_input = len(signalname[0])
    len_output = len(signalname[1])
    len_datalist = len(signallist[0][len_input])
    for i in range(len_datalist):
        flag = True
        for j in range(len_input, len_input+len_output):
            if signallist[0][j][i] != signallist[1][j][i]:
                flag = False
                break
        if flag == False:
            l = i - 15 if i - 15 >= 0 else 0
            # r = i+15 if i+15 <= len_datalist else len_datalist
            for j in range(len_input + len_output):
                r = i+15 if i + \
                    15 <= len(signallist[0][j]) else len(signallist[0][j])
                del signallist[0][j][0:l]
                del signallist[0][j][r:len_datalist]
                r = i+15 if i + \
                    15 <= len(signallist[1][j]) else len(signallist[1][j])
                del signallist[1][j][0:l]
                del signallist[1][j][r:len_datalist]
            break


def data_format(signallist, signalname, signaltype,  wavetype, NoInputSignal, combineSize, hscale, clk_fold):
    """将信号值进行优化处理"""

    if wavetype == 3:
        cut(signallist, signalname, signaltype)
        wavetype = 2

    mismatch = []
    signalwavedata = [[] for i in range(2)]
    for i in range(2):
        # print(glo.signallist)
        for datalist in signallist[i]:
            len_datalist = len(datalist)
            mismatch.append(['0']*len_datalist)
            signalwavedata[i].append(['='] * len_datalist)
    count_list = []
    for i in range(1, len_datalist+1):
        count_list.append(str(i))

    getmismatch(signallist, signalname, mismatch)

    if wavetype == 0:
        signal = data_format_0(signallist, signalname,
                               signaltype, signalwavedata, mismatch, NoInputSignal, clk_fold)
    elif wavetype == 1:
        signal = data_format_1(signallist, signalname,
                               signaltype, signalwavedata, mismatch, NoInputSignal, clk_fold)
    else:
        signal = data_format_2(signallist, signalname,
                               signaltype, signalwavedata, mismatch, count_list, NoInputSignal, combineSize, clk_fold)
    python2json = {}

    python2json["signal"] = signal
    # 标出尾部序号
    counter = {}
    count = ' '.join(count_list)+' '
    counter["tock"] = count
    python2json["foot"] = counter

    # 调整波形宽度
    python2json["config"] = {"hscale": hscale}
    jsonStr = json.dumps(python2json)
    return jsonStr


def clk_change(signallist, signalname):
    len_input = len(signalname[0])
    len_output = len(signalname[1])
    len_datalist = len(signallist[0][len_input])
    signallist1 = signallist[:]
    if len_input != 0:
        if signalname[0][0] == 'clk':
            i = len_datalist - 1
            while i >= 0:
                # 为了确保每次比较时都是 i-1:clk=1 和 i:clk=0 的两组数据比较是否相同
                if signallist[0][0][i] == '1':
                    i -= 1
                    continue
                if i == 0 and signallist[0][0][i] == '0':
                    flag = True
                else:
                    flag = True
                    for p in range(2):
                        for j in range(1, len_input + len_output):
                            if i >= len(signallist[p][j]):
                                continue
                            if signallist[p][j][i] != signallist[p][j][i - 1]:
                                if signallist[p][0][i] == '0' and signallist[p][0][i - 1] == '1':
                                    flag = False
                                    break
                        if flag == False:
                            break
                if flag:
                    for p in range(2):
                        for j in range(0, len_input + len_output):
                            if i >= len(signallist[p][j]):
                                continue
                            del signallist[p][j][i]
                else:
                    signallist = signallist1
                    return False
                i -= 2
            return True
    return False


def getgrade(signallist):
    len_datalist = min(len(signallist[0]), len(signallist[1]))

    grade = 0
    for i in range(len_datalist):
        if signallist[0][i] == signallist[1][i]:
            grade += 1

    return grade * 100 / len(signallist[0])


# def getgrade(signallist, signalname):
# mismatch = []
# len_datalist = 0
# for i in range(2):
#     for datalist in signallist[i]:
#         len_datalist = len(datalist)
#         mismatch.append(['0'] * len_datalist)

# getmismatch(signallist, signalname, mismatch)

# grade = [0, 0]
# len_input = len(signalname[0])
# len_output = len(signalname[1])
# for i in range(len_datalist):
#     flag = True
#     grade[1] += 1
#     for j in range(len_input, len_input + len_output):
#         if mismatch[j][i] == '1':
#             flag = False
#             break
#     if flag:
#         grade[0] += 1
# return grade[0] * 100 / grade[1]
