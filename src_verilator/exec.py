#! /usr/bin/python3.8
# -*- coding: utf-8 -*-

import json
import os
import yaml
import shlex
import subprocess
import difflib
import sys


# /
# |- coursegrader
# |             |- testdata
# |             |         |- config.yaml
# |             |         |
# |             |         |- sub test point ?
# |             |         |- sub test point ?
# |             |         |- sub test point ?
# |             |         |- sub test point ?
# |             |
# |             |- submit 
# |                     |- *.v
# |
# |- home
# |     |- root
# |     |     |- exec.py
# |     |     |- ...
# |     |
# |     |- ojfiles
# |     |       |- teacher
# |     |       |- student


def make(dst: str, ans: list, tb: list, onf: list):

    # CC = "rm -rf {} 2> /dev/null"
    # cmd = CC.format(dst)
    # args = shlex.split(cmd)
    # try:
    #     p = subprocess.check_output(args, shell=True)
    # except subprocess.CalledProcessError as e:
    #     # oops, do not let anybody knows there is an error
    #     pass
    #
    CC = "mkdir -p {}"
    cmd = CC.format(dst)
    args = shlex.split(cmd)
    p = subprocess.check_output(args)

    CC = "cp {} {}"
    cmd = CC.format(" ".join(onf), dst)
    args = shlex.split(cmd)
    p = subprocess.check_output(args)

    CC = """verilator 
                --cc 
                --main 
                --binary 
                --Wno-lint 
                --Wno-style 
                --Wno-TIMESCALEMOD 
                -CFLAGS -std=c++2a 
                -O3 
                --x-assign fast 
                --x-initial fast 
                --noassert 
                --exe  
                --o ___XXX_DO_NOT_CHANGE_THIS_EXECUTABLE 
                --Mdir {} 
                {} {}"""

    cmd = CC.format(dst, " ".join(ans), " ".join(tb))
    args = shlex.split(cmd)
    p = subprocess.check_output(args)
    return p


def execute(dst: str):
    os.chdir(dst)
    executable = []
    for f in os.listdir(dst):
        if os.access(os.path.join(dst, f), os.X_OK):
            # every file in nessasery files should has a ext name
            # for example, inst_ram.mif
            # not inst_ram
            if "___XXX_DO_NOT_CHANGE_THIS_EXECUTABLE" in f:  # ok
                executable.append(os.path.join(dst, f))
    if len(executable) != 1:
        # pass
        raise Exception(f"Failed to compile!!!, with executables = {executable}")
    cmd = f"{executable[0]}"
    args = shlex.split(cmd)
    p = subprocess.check_output(args, stderr=subprocess.STDOUT)
    return p


def quit(msg: str):
    print(msg)
    exit()

def generate_html_output(CG_result):
    verdict = CG_result.get("verdict", "Unknown")
    score = CG_result.get("score", 0)
    comment = CG_result.get("comment", "")
    detail = CG_result.get("detail", "")

    xx = detail.replace('\\n', '<br>')

    # 使用HTML表格展示结果
    html_content = f"""
    <html>
    <head>
        <title>测试结果</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            table, th, td {{
                border: 1px solid #ccc;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .verdict {{
                font-weight: bold;
                font-size: 1.2em;
            }}
            .comment {{
                font-style: italic;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <h1>测试结果</h1>
        <table>
            <tr>
                <th>项目</th>
                <th>结果</th>
            </tr>
            <tr>
                <td>判定</td>
                <td class="verdict">{verdict}</td>
            </tr>
            <tr>
                <td>得分</td>
                <td>{score}</td>
            </tr>
            <tr>
                <td>评论</td>
                <td class="comment">{comment}</td>
            </tr>
            <tr>
                <td>详细信息</td>  
                <td>{xx}</td> <!-- 使用<br>换行 -->
            </tr>
        </table>
    </body>
    </html>
    """

    CG_result.update({"detail": html_content})
    return CG_result

if __name__ == '__main__':
    config_path = "/coursegrader/testdata/config.yaml"

    test_src_path = "/coursegrader/testdata/"
    submit_src_path = "/coursegrader/submit/"
    test_dst_path = "/home/ojfiles/"
    # nessasery_files = ["func/inst_ram.mif", "func/data_ram.mif"]
    nessasery_files = []

    # default only one testpoint
    test_point_number = 0
    test_point_names = []

    # reading conigurations from /coursegrader/testdata/config.yaml
    if os.path.exists(config_path):
        with open(config_path) as f:
            conf_data = yaml.load(f, Loader=yaml.FullLoader)
        if 'TestSrcPath' in conf_data.keys():
            test_src_path = conf_data['TestSrcPath']
        if 'SubmitSrcPath' in conf_data.keys():
            submit_src_path = conf_data['SubmitSrcPath']
        if 'TestDstPath' in conf_data.keys():
            test_dst_path = conf_data['TestDstPath']
        if 'TestPointNumber' in conf_data.keys():
            test_point_number = conf_data['TestPointNumber']
        if 'TestPointNames' in conf_data.keys():
            test_point_names = conf_data['TestPointNames']
        if 'NessaseryFiles' in conf_data.keys():
            nessasery_files = conf_data['NessaseryFiles']

    test_ans_srcs = []
    main_test_tb_srcs = []
    student_ans_srcs = []
    other_nessasery_files = []

    if len(nessasery_files) != 0:
        for f in nessasery_files:
            other_nessasery_files.append(os.path.join(test_src_path, f))

    for d in os.listdir(test_src_path):
        # print(d[-5:])
        if d[-5:] == '_tb.v':
            # this is a testbench
            main_test_tb_srcs.append(os.path.join(test_src_path, d))
        elif d[-2:] == '.v':
            # this is an answer
            test_ans_srcs.append(os.path.join(test_src_path, d))

    for d in os.listdir(submit_src_path):
        if d[-2:] == '.v':
            student_ans_srcs.append(os.path.join(submit_src_path, d))

    # print(main_test_tb_srcs)
    # print(test_ans_srcs)
    # main_test_tb_srcs must be non-empty, otherwise, it will raise a error
    if len(main_test_tb_srcs) == 0:
        raise Exception("No testbenches!!!")

    if len(test_ans_srcs) == 0:
        raise Exception("No answers!!!")

    if len(student_ans_srcs) == 0:
        raise Exception("No student answers!!!")

    if len(other_nessasery_files) != len(nessasery_files):
        raise Exception("No nessasery files")

    # make main test
    p = make(test_dst_path + "teacher/", test_ans_srcs, main_test_tb_srcs, other_nessasery_files)
    # print(p)

    # make student ans
    p = make(test_dst_path + "student/", student_ans_srcs, main_test_tb_srcs, other_nessasery_files)
    # print(p)

    # main testpoint ready
    teacher_result = (execute(test_dst_path + "teacher/")).splitlines()
    # print(teacher_result)

    student_result = (execute(test_dst_path + "student/")).splitlines()
    # print(p)
    # result file will store in the same directory

    err_cnt = 0
    ttl_cnt = 0

    CG_result = {}

    is_pass = False
    mark = 0
    verdict = "WA!!!"
    HTML = True
    comment = ""
    detail = ""
    test_passed = 0
    test_cnt = 1
    last_err = ""

    teacher_result_list = []
    student_result_list = []

    for i in teacher_result:
        i = i.decode('utf-8', 'ignore')
        if i[:7] == 'monitor':
            teacher_result_list.append(i)
            ttl_cnt += 1
    for i in student_result:
        i = i.decode('utf-8', 'ignore')
        if i[:7] == 'monitor':
            student_result_list.append(i)

    diffs = difflib.context_diff(teacher_result_list, student_result_list)
    err_cnt = 0
    for i in diffs:
        err_cnt += 1
        if err_cnt < 9:
            detail += f"\n{i}"
        else:
            break

    # print(f"{ttl_cnt - err_cnt}/{ttl_cnt} lines correct for main testpoint!!!")

    if err_cnt == 0:
        # pass
        test_passed += 1
        is_pass = True
        mark = 100
        verdict = "AC!!!"
        comment = f"testpoint passed!!!"
    else:
        comment = f"main testpoint wrong!!!"

    r = difflib.SequenceMatcher(None, teacher_result_list, student_result_list).ratio()

    detail += f"\n{r * 100}% correct for main testpoint!!!"

    HTML = True
    CG_result.update({"verdict": f"{verdict}"})
    CG_result.update({"HTML": f"{HTML}"})
    CG_result.update({"score": f"{mark}"})
    CG_result.update({"comment": f"{comment}"})
    CG_result.update({"detail": f"{detail}"})

    sub_mark = []

    output_final = json.dumps(CG_result)
    if is_pass:
        quit(output_final)
        # pass

    # not pass
    if test_point_number == 0:
        # nothing to test
        # end 
        quit(output_final)

    # something to test
    if len(test_point_names) != 0 and len(test_point_names) != test_point_number:
        quit(output_final)

    test_cnt = test_point_number

    for i in range(test_point_number):
        sub_test_tb_src = []
        if len(test_point_names) == 0:
            sub_test_name = f"point{i}"
        else:
            sub_test_name = test_point_names[i]

        # print(f"entering {sub_test_name}")

        for d in os.listdir(os.path.join(test_src_path, sub_test_name)):
            # print(d[-5:])
            if d[-5:] == '_tb.v':
                # this is a testbench
                sub_test_tb_src.append(os.path.join(os.path.join(test_src_path, sub_test_name), d))

        other_nessasery_files = []

        for f in nessasery_files:
            other_nessasery_files.append(os.path.join(os.path.join(test_src_path, sub_test_name), f))

        # print(sub_test_tb_src)
        # just replace testbenches with the new

        # make main test
        p = make(test_dst_path + "teacher/", test_ans_srcs, sub_test_tb_src, other_nessasery_files)
        # print(p)

        # make student ans
        p = make(test_dst_path + "student/", student_ans_srcs, sub_test_tb_src, other_nessasery_files)
        # print(p)

        # main testpoint ready
        teacher_result = (execute(test_dst_path + "teacher/")).splitlines()

        student_result = (execute(test_dst_path + "student/")).splitlines()

        err_cnt = 0
        ttl_cnt = 0

        CG_result = {}

        teacher_result_list = []
        student_result_list = []

        for k in teacher_result:
            k = k.decode('utf-8', 'ignore')
            teacher_result_list.append(k)
            if k[:7] == 'monitor':
                ttl_cnt += 1
        for k in student_result:
            k = k.decode('utf-8', 'ignore')
            student_result_list.append(k)

        diffs = difflib.context_diff(teacher_result_list, student_result_list)
        err_cnt = 0
        for k in diffs:
            err_cnt += 1
            if err_cnt < 9:
                detail += f"<p>\n{k}</p>"
            else:
                break

        if err_cnt == 0:
            test_passed += 1

        r = difflib.SequenceMatcher(None, teacher_result_list, student_result_list).ratio()
        # detail += f"<p>\n{r*100}% correct for subtestpoint{i}!!!</p>"
        if abs(r - 1) < 1e-8:
            colour = "#0f0"
        elif abs(r) > 1e-8:
            colour = "#ff0"
        else:
            colour = "#f00"

        detail += f'<div style="background-color: {colour}; padding: 0.5rem; display: flex; flex-direction: row; width: 100pt; height: 100pt;">  <p style="font: small-caps bold 1.2rem sans-serif; text-align: center;">\n{r * 100}% correct for subtestpoint{i}!!!</p> </div>'
        sub_mark.append(r * 100)

    comment += f"\n{test_passed}/{test_cnt} testpoint passed!!!"
    mark = 0
    for i in sub_mark:
        mark += i

    CG_result.update({"verdict": f"{verdict}"})
    CG_result.update({"HTML": f"{HTML}"})
    CG_result.update({"score": f"{mark}"})
    CG_result.update({"comment": f"{comment}"})
    CG_result.update({"detail": f"{detail}"})

    # json.dumps(CG_result)

    output_final = generate_html_output(CG_result)
    output_final = json.dumps(output_final)
    quit(output_final)
