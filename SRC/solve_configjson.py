import json
import config as glo
import re


def wavesize_fun(value):
    if value > 100 or value < 5:
        return False
    else:
        return True


def wavewidth_fun(value):
    if value not in range(1, 4):
        return False
    else:
        return True


def combinsize_fun(value):
    if value < 4:
        return False
    else:
        return True


def simulateTime_fun(value):
    if value not in range(1, 5):
        return False
    else:
        return True


def finishTime_fun(value):
    if value < 50:
        return False
    else:
        return True


def waveType_fun(value):
    if value not in range(4):
        return False
    else:
        return True


config_content = {
    "wavesize": 30,
    "wavewidth": 1,
    "display_flag": False,
    "combinsize": 4,
    "simulateTime": 2,
    "finishTime": 100,
    "showWave": True,
    "showResult": True,
    "waveType": 0
}


switch = {"wavesize": wavesize_fun,
          "wavewidth": wavewidth_fun, "combinsize": combinsize_fun,
          "simulateTime": simulateTime_fun, "finishTime": finishTime_fun, "waveType": waveType_fun}


def parse_json(filename):
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?', re.DOTALL | re.MULTILINE)
    try:
        with open(filename) as f:
            content = ''.join(f.readlines())
            # print(content)
            # Looking for comments
            match = comment_re.search(content)
            while match:
                # single line comment
                content = content[:match.start()] + content[match.end():]
                match = comment_re.search(content)

            fileJson = json.loads(content)

            return [fileJson, 0, ""]
    except FileNotFoundError:
        return [{}, 2, "no config.json file"]
    except Exception:
        return [{}, 1, "config.json file sync error"]


def resolveJson(path):
    [fileJson, state, message] = parse_json(path)
    if state == 1:
        return [1, message]

    for key in config_content:
        if key in fileJson.keys():
            try:
                if(not isinstance(fileJson[key], type(config_content[key]))):
                    raise Exception(key + " should be type of " +
                                    str(type(config_content[key])))
                if(not switch[key](config_content[key])):
                    raise Exception(key + " value not legal")
            except KeyError:
                pass
            except Exception as err:
                return [1, str(err)]
        else:
            fileJson[key] = config_content[key]

    glo.MAX_DATA = fileJson["wavesize"]
    glo.display_flag = fileJson["display_flag"]
    glo.waveType = fileJson["waveType"]
    glo.hscale = fileJson["wavewidth"]
    glo.combineSize = fileJson["combinsize"]
    glo.simulateTime = fileJson["simulateTime"]
    glo.finishTime = fileJson["finishTime"]
    glo.showWave = fileJson["showWave"]
    glo.showResult = fileJson["showResult"]

    return [state, message]
