# -*- coding: utf-8 -*-

import json
import solve_configjson as solve_configjson
import config as glo
import shlex
import subprocess
import trans_test as wave_trans
import codecs
import sys
import os
import yaml

# text format set to utf-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
# type = sys.getfilesystemencoding()

def err_message(str):
    p = {"score": "0", "comment": str}
    return json.dumps(p)


def run():

    # solve json is unavailable now
    #[state, message] = solve_configjson.resolveJson('/coursegrader/testdata/config.json')
    #if(state == 1):
    #    print(err_message(message))
    #    exit()
    noMainTestPoint = "M"
    conf_data = []
    if os.path.exists("/coursegrader/testdata/config.yaml"):
        with open("/coursegrader/testdata/config.yaml") as file1:
            conf_data = yaml.load(file1, Loader=yaml.FullLoader)
        if conf_data["noMainTestPoint"] == True:
            noMainTestPoint = "N"
    # call `test` to synthesis and simulate
    command_line = "/home/pythonfile/test {0} {1} {2}".format(str(glo.simulateTime), str(glo.finishTime), str(noMainTestPoint))
    args = shlex.split(command_line)
    p = "err"
    
    # try to decode return value, just in case there are some weird character in students' answer
    # it happened when judging answers from a final exam
    # otherwise, it will crash all system, especially when you processing a batch judge
    try:
        p = bytes.decode(subprocess.check_output(args, stderr=subprocess.STDOUT), encoding='utf-8')
        p = p[:-1]
    except Exception as e:
        try:
            p = bytes.decode(subprocess.check_output(args, stderr=subprocess.STDOUT), encoding='ISO-8859-1')
        except Exception as eq:
            print(err_message(str(e) + " DECODE ERROR ISO-8859-1"))
            exit()
        print(err_message(str(e) + " DECODE ERROR UTF8"))
        exit()

    stdjson = '{"HTML":"true","verdict":"","comment":"","score":"0","detail":""}'
    res_std = json.loads(stdjson)
    mid_json = p.splitlines();   
    first_mis = -1;
    
    # only one line means an AC
    if(len(mid_json)==1):
        try:
            result_json = json.loads(p)
        except Exception as e:
            result_json["detail"] = ";[ERROR] 10000, ERROR AT LOADING JSON; " + str(e)
        print(result_json)
    else:
        for it in mid_json:
            try:
                result_json = json.loads(it)            
            except Exception as e:
                res_std["detail"] = res_std["detail"] + ";[ERROR] 10001, ERROR AR LOADING JSON; " + str(e)
            res_std["verdict"] = res_std["verdict"] + ", " + result_json["verdict"]
            res_std["score"] = int(res_std["score"]) + int(result_json["score"])
            res_std["comment"] = res_std["comment"] + ", " + result_json["comment"]
        if(int(res_std["score"])!=100):
            try:
                for j, index in zip(mid_json, range(0,10)):
                    tmp = json.loads(j)
                    if(int(tmp["score"])==0 and first_mis == -1):
                        first_mis = index
            except Exception as e:
                res_std["detail"] = res_std["detail"] + ";[ERROR] 10001, ERROR AT LOADING JSON; " + str(e)
            try:
                if(first_mis == -1):
                    first_mis = 0
                [svg_string, grade, state, message] = wave_trans.deal_wave(first_mis)
                if(state != 0):
                    raise Exception(message + ";[ERROR] 10003, ERROR AT DEALING THE WAVE; ")
                res_std["detail"] = res_std["detail"] + svg_string
                res_std["score"] = grade if glo.display_flag else res_std["score"]
            except Exception as e:
                res_std["detail"] = res_std["detail"] + ";[ERROR] 10004, ERROR AT POST JUDGE; " + str(e)
            subprocess.check_call(["/home/pythonfile/quit_oj"])
            print(res_std)
        else:
            print(res_std)

if __name__ == "__main__":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    run()
