#! /usr/bin/python3.8
# -*- coding: utf-8 -*-

import json
import os

import yaml
import shlex
import subprocess
import difflib
import sys
import re
import wavedrom

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
        rv[0] = '<br>'.join(e.output.decode("utf-8", "ignore").splitlines())
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
    return ['<br>'.join(px), 0]


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
        
        <script>
            function changeText()
            {{
                if (document.getElementById("btn").value != "隐藏波形"){{
                    document.getElementById("btn").value = "隐藏波形";
                }}else{{
                    document.getElementById("btn").value = "显示波形";
                }}
            }}
                    
            function collapse()
            {{
                if (document.getElementById("svg_wave").style.display != "none"){{
                    document.getElementById("svg_wave").style.display = "none";
                }}else{{
                    document.getElementById("svg_wave").style.display = "";
                }}
                changeText();
            }}

        </script>

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
        
        <style>
            .v-align {{
                margin: 0 auto;
                font: small-caps bold 1.2rem sans-serif;
                width: 100px;
                height: 100px;
                text-align: center;
                line-height: 100px;
                border: 0px solid #ddd;
            }}
        
            .button {{
                background-color: #4CAF50;
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                cursor: pointer;
            }}


            .button:hover {{
                box-shadow:
                inset 0 -3em 3em rgba(0, 0, 0, 0.1),
                0 0 0 0px rgb(255, 255, 255),
                0.3em 0.3em 1em rgba(0, 0, 0, 0.3);
            }}
		
            .button a {{
                display: none;     
            }}
 
            .button:hover a {{
                display: initial;     
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


def load_param(conf: dict):
    if os.path.exists(conf["config_path"]):
        with open(conf["config_path"]) as f:
            conf_data = yaml.load(f, Loader=yaml.FullLoader)

        conf.update({"no_frac_points": False})
        if 'TestSrcPath' in conf_data.keys():
            conf.update({"test_src_path": conf_data['TestSrcPath']})
        if 'SubmitSrcPath' in conf_data.keys():
            conf.update({"submit_src_path": conf_data['SubmitSrcPath']})
        if 'TestDstPath' in conf_data.keys():
            conf.update({"test_dst_path": conf_data['TestDstPath']})
        if 'TestPointNumber' in conf_data.keys():
            conf.update({"test_point_number": conf_data['TestPointNumber']})
        if 'TestPointNames' in conf_data.keys():
            conf.update({"test_point_names": conf_data['TestPointNames']})
        if 'NessaseryFiles' in conf_data.keys():
            conf.update({"nessasery_files": conf_data['NessaseryFiles']})


def prepare_files(conf: dict):
    test_ans_srcs = []
    main_test_tb_srcs = []
    student_ans_srcs = []
    other_necessary_files = []

    detail = ""

    # To find all necessary files
    # These files will be copied to dst
    if len(conf["nessasery_files"]) != 0:
        for f in conf["nessasery_files"]:
            other_necessary_files.append(os.path.join(conf["test_src_path"], f))

    for d in os.listdir(conf["test_src_path"]):
        # print(d[-5:])
        if d[-5:] == '_tb.v':
            # this is a testbench
            main_test_tb_srcs.append(os.path.join(conf["test_src_path"], d))
        elif d[-2:] == '.v':
            # this is an answer
            test_ans_srcs.append(os.path.join(conf["test_src_path"], d))

    for d in os.listdir(conf["submit_src_path"]):
        if d[-2:] == '.v':
            student_ans_srcs.append(os.path.join(conf["submit_src_path"], d))

    # print(main_test_tb_srcs)
    # print(test_ans_srcs)
    # main_test_tb_srcs must be non-empty, otherwise, it will raise an error
    if len(main_test_tb_srcs) == 0:
        detail += "<br><p style='color:#E74C3B'> No testbench! Please contact your TA. </p><br>"
    if len(test_ans_srcs) == 0:
        detail += "<br><p style='color:#E74C3B'> No answer! Please contact your TA. </p><br>"
    if len(student_ans_srcs) == 0:
        detail += "<br><p style='color:#E74C3B'> No answer submitted! Please check your work. </p><br>"
    if len(other_necessary_files) != len(conf["nessasery_files"]):
        detail += "<br><p style='color:#E74C3B'> No necessary files! Please contact your TA. </p><br>"

    return detail, [test_ans_srcs, main_test_tb_srcs, student_ans_srcs, other_necessary_files]


def compile_and_run(conf: dict, file_lists: list):
    detail = ""
    test_ans_srcs, main_test_tb_srcs, student_ans_srcs, other_necessary_files = file_lists

    # make main test
    p = make(conf["test_dst_path"] + "teacher/", test_ans_srcs, main_test_tb_srcs, other_necessary_files)
    if p[1] == 1:
        detail += (f"<br><p style='color:#E74C3B'> Compiling failed in teacher's code. Please contact your TA. <br>"
                   f"Error messages are as follows: </p><br>"
                   f"<div style='color:#E67D22; background-color:#F1F1F1;'> {p[0]} </div><br>")

    # make student ans
    p = make(conf["test_dst_path"] + "student/", student_ans_srcs, main_test_tb_srcs, other_necessary_files)
    if p[1] == 1:
        detail += (f"<br><p style='color:#E74C3B'> Compiling failed in your code. Please check your work. <br>"
                   f"Error messages are as follows: </p><br>"
                   f"<div style='color:#E67D22; background-color:#F1F1F1;'> {p[0]} </div><br>")

    # main testpoint ready
    teacher_result = execute(conf["test_dst_path"] + "teacher/")
    if teacher_result[1] == 1:
        detail += (f"<br><p style='color:#E74C3B'> Executing failed in teacher's code. Please contact your TA. <br> "
                   f"Error messages are as follows: </p><br> "
                   f"<div style='color:#E67D22; background-color:#F1F1F1;'> {teacher_result[0]} </div>")

    student_result = execute(conf["test_dst_path"] + "student/")
    # result file will store in the same directory
    if student_result[1] == 1:
        detail += (f"<br><p style='color:#E74C3B'> Executing failed in your code. <br> "
                   f"Error messages are as follows: </p><br> "
                   f"<div style='color:#E67D22; background-color:#F1F1F1;'> {student_result[0]} </div><br>")

    teacher_result[0] = teacher_result[0].split("<br>")
    student_result[0] = student_result[0].split("<br>")

    return detail, teacher_result, student_result


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
        "detail": "",
        "verdict": "",
        "HTML": "True",
        "score": 0,
        "comment": ""
    }

    detail = ""
    is_pass = False
    mark = 0
    verdict = "WA!!!"
    HTML = True
    comment = ""
    test_passed = 0
    test_cnt = 1
    last_err = ""
    err_cnt = 0
    ttl_cnt = 0

    teacher_result_list = []
    student_result_list = []

    # please ignore spelling mistakes
    # reading configurations from /coursegrader/testdata/config.yaml
    load_param(config_dict)
    # if the yaml file doesn't exist, act as older OJs

    # to prepare answer, testbench, student's answer & other files required by the yaml file.
    d, file_lists = prepare_files(config_dict)
    detail += d

    test_ans_srcs, main_test_tb_srcs, student_ans_srcs, other_necessary_files = file_lists

    # compile and run.
    d, teacher_result, student_result = compile_and_run(config_dict, file_lists)
    detail += d

    svg_string = ""

    if teacher_result[1] == 1 or student_result[1] == 1:
        # something is wrong, error.
        err_cnt = 1
        ttl_cnt = 1
    else:
        for i in teacher_result[0]:
            if i[:7] == 'monitor':
                teacher_result_list.append(i[8:])
                ttl_cnt += 1
        for i in student_result[0]:
            if i[:7] == 'monitor':
                student_result_list.append(i[8:])

        # it will find the first error line.
        first_mismatch_line = -1
        for i in range(min(ttl_cnt, len(student_result_list))):
            if teacher_result_list[i] != student_result_list[i]:
                first_mismatch_line = i
                break

        sig_names = []

        # find all signal names we captured
        sig_n_val = re.split('[,:]', teacher_result_list[0])
        for i in sig_n_val:
            r = re.split('=', i)
            sig_names.append(r[0])

        sig_and_val = [[[] for i in range(len(sig_names))], [[] for i in range(len(sig_names))]]
        sig_and_val_compact = [[[] for i in range(len(sig_names))], [[] for i in range(len(sig_names))]]

        start_line = max(0, first_mismatch_line - 200)
        end_line = min(min(ttl_cnt, len(student_result_list)), first_mismatch_line + 200)

        wave = {
            "signal": [
                [
                    "ref",  # {"name":"", "wave":""}, {"name":"", "wave":""}, {"name":"", "wave":""}
                ],
                [
                    "yours",  # {"name":"", "wave":""}, {"name":"", "wave":""}, {"name":"", "wave":""}
                ]
            ],
            "edge": [
                # edges
            ],
            "head": {
                "text": 'Wave Diff',
                "tick": 0,
                "every": 2
            },
            "config": {
                "skin": "narrow"
            },
        }

        test_results = [teacher_result_list, student_result_list]

        for i in wave['signal']:
            for j in range(len(sig_names)):
                i.append({"name": f"{sig_names[j]}", "wave": "", "node": ""})

        for _ in range(len(wave['signal'])):
            # last_clk = 'x'
            for i in range(start_line, end_line):
                sig_n_val = re.split('[,:]', test_results[_][i])
                # ok_flag = False
                for j in range(len(sig_names)):
                    r = re.split('=', sig_n_val[j])
                    # if ok_flag or r[0] == "clk" and r[1] != last_clk:
                    if r[0] == "clk":
                        # last_clk = r[1]
                        sig_and_val[_][j].append(
                            'h' if r[1] == '1' else 'l'
                        )
                    else:
                        sig_and_val[_][j].append(r[1])
                        # ok_flag = True
                    # else:
                    #     break

            # compress data
            # 10100001 will convert to 1010...1
            for i in range(len(sig_names)):
                last_d = "x"
                sig_and_val_compact[_][i].append(sig_and_val[_][i][0])
                for j in range(1, len(sig_and_val[_][i])):
                    if sig_and_val[_][i][j] == sig_and_val[_][i][j - 1]:
                        sig_and_val_compact[_][i].append('.')
                    else:
                        sig_and_val_compact[_][i].append(sig_and_val[_][i][j])

            for i in range(len(sig_names)):
                wave["signal"][_][i + 1]["wave"] = ''.join(sig_and_val_compact[_][i])
                wave["signal"][_][i + 1]["node"] = '.' * len(sig_and_val_compact[_][i])
                if first_mismatch_line != -1:
                    wave["signal"][_][i + 1]["node"] = wave["signal"][_][i + 1]["node"][:first_mismatch_line] + (
                        'a' if _ == 0 else 'b') + wave["signal"][_][i + 1]["node"][first_mismatch_line + 2:]

        if first_mismatch_line != -1:
            wave["edge"].append("a~b")

        wave = json.dumps(wave)

        svg = wavedrom.render(wave)
        svg_string = svg.tostring()

        err_cnt = 0 if first_mismatch_line == -1 else 1

        # diffs = difflib.context_diff(teacher_result_list, student_result_list)
        # err_cnt = 0
        # for i in diffs:
        #     err_cnt += 1
        #     if err_cnt == 1:
        #         detail += "<br><p style='color:blue'> Diffs are as follows: </p><br>"
        #     if err_cnt < 9:
        #         detail += f"<br>{i}"
        #     else:
        #         break

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
        colour = "#5EB95E"
    elif abs(r) > 1e-8:
        colour = "#E67D22"
    else:
        colour = "#E74C3B"

    detailx = ""
    detailx += (
        f'<div style="background-color: {colour}; padding: 0.5rem; display: inline-block; flex-direction: row; width: 100pt; height: 100pt;" class="button" onclick="collapse()" title="点击展示/隐藏本测试点波形">'
        f'<div style="float:left;" >'
        f'#1'
        f'</div>'
        f'<div class="v-align">'
        f'{("AC" if abs(r - 1) < 1e-8 else "WA") if config_dict["no_frac_points"] else str(int(r * 10000) / 100) + "%"}'
        f'</div>'
        f'</div>'
    )

    if len(svg_string) != 0:
        if err_cnt != 0:
            detailx += ('<br>'
                       f"<div style='width:2000px;overflow:auto;background:#EEEEEE;' id='svg_wave' >{svg_string}</div>")
        else:
            detailx += ('<br>'
                        f"<div style='width:2000px;overflow:auto;background:#EEEEEE;display:none' id='svg_wave' >{svg_string}</div>")

    detail = detailx + detail
    detail += "<div style='width:2000px;' > </div>"

    if config_dict['no_frac_points']:
        mark = 100 if abs(r - 1) < 1e-8 else 0
    else:
        mark = r * 100

    HTML = True

    CG_result.update({"verdict": f"{verdict}"})
    CG_result.update({"HTML": f"{HTML}"})
    CG_result.update({"score": f"{mark}"})
    CG_result.update({"comment": f"{comment}"})
    CG_result.update({"detail": f"{detail}"})

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

        other_necessary_files = []

        for f in config_dict["nessasery_files"]:
            other_necessary_files.append(os.path.join(os.path.join(config_dict["test_src_path"], sub_test_name), f))

        # print(sub_test_tb_src)
        # just replace testbenches with the new

        # make main test
        p = make(config_dict["test_dst_path"] + "teacher/", test_ans_srcs, sub_test_tb_src, other_necessary_files)
        # print(p)

        # make student ans
        p = make(config_dict["test_dst_path"] + "student/", student_ans_srcs, sub_test_tb_src, other_necessary_files)
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
