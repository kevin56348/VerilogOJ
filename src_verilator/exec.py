#! /usr/bin/python3.8
# -*- coding: utf-8 -*-

import json
import os
from distutils.command.config import config

import yaml
import shlex
import subprocess
import difflib
import sys

FINAL_EXE_NAME = "___XXX_DO_NOT_CHANGE_THIS_EXECUTABLE"


# This is a typical test folder structure. with a config.yaml in testdata folder.
# To make it compatible with older OJs, if the config.yaml were missing, it will
# act as older OJs.

# Typical structure
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

# Structure used in older OJs
# /
# |- coursegrader
# |             |- testdata
# |             |         |- *.v
# |             |         |- *_tb.v
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

def make(dst: str, ans: list, tb: list, onf: list) -> [str, int]:
    """
    This function aims to compile every *.v files into an executable.
    It will first mkdir a target directory recursively, if it doesn't exist.
    Then, it copies other necessary files into our target directory.
    Finally, it compiles the files using verilator, with an executable
    named with the global constant `FINAL_EXE_NAME` since I do not want to handle
    some annoying situations.
    """

    cmd = f"mkdir -p {dst}"
    args = shlex.split(cmd)
    subprocess.check_output(args)  # ignore output

    if len(onf) != 0:  # There are necessary files
        cmd = f"cp {' '.join(onf)} {dst}"
        args = shlex.split(cmd)
        subprocess.check_output(args)  # ignore output

    # Here, you can't use > to redirect its output
    cmd = (
        f"verilator --cc --main --binary --Wno-lint --Wno-style --Wno-TIMESCALEMOD -CFLAGS -std=c++2a -O3 --x-assign fast"
        f" --x-initial fast --noassert --exe --o {FINAL_EXE_NAME}"
        f" --Mdir {dst}"
        f" {' '.join(ans)} {' '.join(tb)}")
    args = shlex.split(cmd)
    rv = ["", 0]
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        rv[0] = e.output.decode("utf-8", "ignore")
        rv[1] = 1
    return rv


def execute(dst: str) -> [str, int]:
    """Execute `FINAL_EXE_NAME` in dst"""

    os.chdir(dst)
    executable = []
    for fx in os.listdir(dst):
        # Check whether the file fx is executable.
        if os.access(os.path.join(dst, fx), os.X_OK):
            if FINAL_EXE_NAME in fx:  # if the `FINAL_EXE_NAME` is found, it means verilator successfully compiled *.v files.
                executable.append(os.path.join(dst, fx))

    rv = ""
    if len(executable) != 1:
        rv = f"Failed to compile!!!, with executables = {executable}"
        return [rv, 1]

    cmd = f"{executable[0]}"
    args = shlex.split(cmd)
    px = subprocess.check_output(args, stderr=subprocess.STDOUT).decode("utf-8", "ignore").splitlines()
    return ['\n'.join(px), 0]


def quitx(msg: str) -> None:
    print(msg)
    exit()


def generate_html_output(CG_result: dict):
    verdict = CG_result.get("verdict", "Unknown")
    score = CG_result.get("score", 0)
    comment = CG_result.get("comment", "")
    detail = CG_result.get("detail", "")

    xx = detail.replace('\\n', '<br>')
    xx = xx.replace('\\r', '<br>')

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
    config_dict = {
        "config_path": "/coursegrader/testdata/config.yaml",
        "test_src_path": "/coursegrader/testdata/",
        "submit_src_path": "/coursegrader/submit/",
        "test_dst_path": "/home/ojfiles/",
        "nessasery_files": [],
        # default: only one testpoint
        "test_point_number": 0,
        "test_point_names": [],
        "no_frac_points": True
    }

    CG_result = {
        "detail": ""
    }

    # please ignore spelling mistakes
    keys = ["TestSrcPath", "SubmitSrcPath", "TestDstPath", "TestPointNumber", "TestPointNames", "NessaseryFiles"]

    # reading configurations from /coursegrader/testdata/config.yaml
    if os.path.exists(config_dict["config_path"]):
        with open(config_dict["config_path"]) as f:
            conf_data = yaml.load(f, Loader=yaml.FullLoader)

        config_dict.update({"no_frac_points": False})
        if 'TestSrcPath' in conf_data.keys():
            config_dict.update({"test_src_path": conf_data['TestSrcPath']})
        if 'SubmitSrcPath' in conf_data.keys():
            config_dict.update({"submit_src_path": conf_data['SubmitSrcPath']})
        if 'TestDstPath' in conf_data.keys():
            config_dict.update({"test_dst_path": conf_data['TestDstPath']})
        if 'TestPointNumber' in conf_data.keys():
            config_dict.update({"test_point_number": conf_data['TestPointNumber']})
        if 'TestPointNames' in conf_data.keys():
            config_dict.update({"test_point_names": conf_data['TestPointNames']})
        if 'NessaseryFiles' in conf_data.keys():
            config_dict.update({"nessasery_files": conf_data['NessaseryFiles']})
    # if the yaml file doesn't exist, act as older OJs

    test_ans_srcs = []
    main_test_tb_srcs = []
    student_ans_srcs = []
    other_nessasery_files = []

    # To find all necessary files
    # These files will be copied to dst
    if len(config_dict["nessasery_files"]) != 0:
        for f in config_dict["nessasery_files"]:
            other_nessasery_files.append(os.path.join(config_dict["test_src_path"], f))

    for d in os.listdir(config_dict["test_src_path"]):
        # print(d[-5:])
        if d[-5:] == '_tb.v':
            # this is a testbench
            main_test_tb_srcs.append(os.path.join(config_dict["test_src_path"], d))
        elif d[-2:] == '.v':
            # this is an answer
            test_ans_srcs.append(os.path.join(config_dict["test_src_path"], d))

    for d in os.listdir(config_dict["submit_src_path"]):
        if d[-2:] == '.v':
            student_ans_srcs.append(os.path.join(config_dict["submit_src_path"], d))

    # print(main_test_tb_srcs)
    # print(test_ans_srcs)
    # main_test_tb_srcs must be non-empty, otherwise, it will raise an error
    if len(main_test_tb_srcs) == 0:
        CG_result.update({"detail": CG_result['detail'] + "<br> No testbench! Please contact your TA. "})

    if len(test_ans_srcs) == 0:
        CG_result.update({"detail": CG_result['detail'] + "<br> No answer! Please contact your TA. "})

    if len(student_ans_srcs) == 0:
        CG_result.update({"detail": CG_result['detail'] + "<br> No answer submitted! Please check your work. "})

    if len(other_nessasery_files) != len(config_dict["nessasery_files"]):
        CG_result.update({"detail": CG_result['detail'] + "<br> No necessary files! Please contact your TA. "})

    # make main test
    p = make(config_dict["test_dst_path"] + "teacher/", test_ans_srcs, main_test_tb_srcs, other_nessasery_files)
    if p[1] == 1:
        CG_result.update({"detail": CG_result[
                                        'detail'] + f"<br> Compiling failed in teacher's code. Please contact your TA <br> {p}"})

    # make student ans
    p = make(config_dict["test_dst_path"] + "student/", student_ans_srcs, main_test_tb_srcs, other_nessasery_files)
    if p[1] == 1:
        CG_result.update({"detail": CG_result['detail'] + f"<br> Compiling failed in your code. <br> {p}"})

    # main testpoint ready
    teacher_result = (execute(config_dict["test_dst_path"] + "teacher/"))
    # print(teacher_result)
    if teacher_result[1] == 1:
        CG_result.update({"detail": CG_result['detail'] + f"<br> {teacher_result[0]}"})

    student_result = (execute(config_dict["test_dst_path"] + "student/"))
    # print(p)
    # result file will store in the same directory
    if student_result[1] == 1:
        CG_result.update({"detail": CG_result['detail'] + f"<br> {student_result[0]}"})

    teacher_result[0] = teacher_result[0].splitlines()
    student_result[0] = student_result[0].splitlines()

    is_pass = False
    mark = 0
    verdict = "WA!!!"
    HTML = True
    comment = ""
    detail = CG_result['detail']
    test_passed = 0
    test_cnt = 1
    last_err = ""

    err_cnt = 0
    ttl_cnt = 0

    teacher_result_list = []
    student_result_list = []

    if teacher_result[1] == 1:
        err_cnt = 1
        ttl_cnt = 1
    else:
        for i in teacher_result[0]:
            # i = i.decode('utf-8', 'ignore')
            if i[:7] == 'monitor':
                teacher_result_list.append(i)
                ttl_cnt += 1
        for i in student_result[0]:
            # i = i.decode('utf-8', 'ignore')
            if i[:7] == 'monitor':
                student_result_list.append(i)

        diffs = difflib.context_diff(teacher_result_list, student_result_list)
        err_cnt = 0
        for i in diffs:
            err_cnt += 1
            if err_cnt < 9:
                detail += f"<br>{i}"
            else:
                break

    # print(f"{ttl_cnt - err_cnt}/{ttl_cnt} lines correct for main testpoint!!!")

    if err_cnt == 0:
        # pass
        test_passed += 1
        is_pass = True
        verdict = "AC!!!"
        comment = f"testpoint passed!!!"
    else:
        comment = f"main testpoint wrong!!!"

    if student_result[1] == 1 or student_result[1] == 1:
        r = 0
    else:
        r = difflib.SequenceMatcher(None, teacher_result_list, student_result_list).ratio()

    if abs(r - 1) < 1e-8:
        colour = "#0f0"
    elif abs(r) > 1e-8:
        colour = "#ff0"
    else:
        colour = "#f00"

    detail += f'<div style="background-color: {colour}; padding: 0.5rem; display: flex; flex-direction: row; width: 100pt; height: 100pt;">  <p style="font: small-caps bold 1.2rem sans-serif; text-align: center;">\n{(100 if abs(r - 1) < 1e-8 else 0) if config_dict["no_frac_points"] else r * 100}% correct for main testpoint!!!</p> </div>'

    if config_dict['no_frac_points']:
        mark = 100 if abs(r - 1) < 1e-8 else 0
    else:
        mark = r * 100

    HTML = True

    CG_result.update({"verdict": f"{verdict}"})
    CG_result.update({"HTML": f"{HTML}"})
    CG_result.update({"score": f"{mark}"})
    CG_result.update({"comment": f"{comment}"})
    CG_result.update({"detail": f"{CG_result['detail'] + detail}"})

    CG_result = generate_html_output(CG_result)

    sub_mark = []

    output_final = json.dumps(CG_result)
    if is_pass:
        quitx(output_final)
        # pass

    # not pass
    if config_dict["test_point_number"] == 0:
        # nothing to test
        # end 
        quitx(output_final)

    # something to test
    if len(config_dict["test_point_names"]) != 0 and len(config_dict["test_point_names"]) != config_dict[
        "test_point_number"]:
        quitx(output_final)

    test_cnt = config_dict["test_point_number"]

    for i in range(config_dict["test_point_number"]):
        sub_test_tb_src = []
        if len(config_dict["test_point_names"]) == 0:
            sub_test_name = f"point{i}"
        else:
            sub_test_name = config_dict["test_point_names"][i]

        # print(f"entering {sub_test_name}")

        for d in os.listdir(os.path.join(config_dict["test_src_path"], sub_test_name)):
            # print(d[-5:])
            if d[-5:] == '_tb.v':
                # this is a testbench
                sub_test_tb_src.append(os.path.join(os.path.join(config_dict["test_src_path"], sub_test_name), d))

        other_nessasery_files = []

        for f in config_dict["nessasery_files"]:
            other_nessasery_files.append(os.path.join(os.path.join(config_dict["test_src_path"], sub_test_name), f))

        # print(sub_test_tb_src)
        # just replace testbenches with the new

        # make main test
        p = make(config_dict["test_dst_path"] + "teacher/", test_ans_srcs, sub_test_tb_src, other_nessasery_files)
        # print(p)

        # make student ans
        p = make(config_dict["test_dst_path"] + "student/", student_ans_srcs, sub_test_tb_src, other_nessasery_files)
        # print(p)

        # main testpoint ready
        teacher_result = (execute(config_dict["test_dst_path"] + "teacher/")).splitlines()

        student_result = (execute(config_dict["test_dst_path"] + "student/")).splitlines()

        err_cnt = 0
        ttl_cnt = 0

        CG_result = {}

        teacher_result_list = []
        student_result_list = []

        for k in teacher_result:
            # k = k.decode('utf-8', 'ignore')
            teacher_result_list.append(k)
            if k[:7] == 'monitor':
                ttl_cnt += 1
        for k in student_result:
            # k = k.decode('utf-8', 'ignore')
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
        if config_dict['no_frac_points']:
            sub_mark.append(100 if abs(r - 1) < 1e-8 else 0)
        else:
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
    quitx(output_final)
