#! /usr/bin/python3.8
# -*- coding: utf-8 -*-

"""
A Verilog Judge based on Verilator.
Copyright (C) 2024 Yuchen Wang

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os

import yaml
import shlex
import subprocess
import difflib
import re
import wavedrom

FINAL_EXE_NAME = "___XXX_DO_NOT_CHANGE_THIS_EXECUTABLE"

"""
This is a typical test folder structure. with a config.yaml in testdata folder.
To make it compatible with older OJs, if the config.yaml were missing, it will
act as older OJs.

Typical structure
/
|- coursegrader
|             |- testdata
|             |         |- config.yaml (optional)
|             |         |
|             |         |- subtest point 1 (optional)
|             |         |                |- answer.v (whose name is arbitrary, but should end with .v)
|             |         |                |- testbench_tb.v (whose name is arbitrary, but should end with _tb.v)
|             |         |
|             |         |- subtest point 2 (optional)
|             |         |
|             |         |- answer.v (whose name is arbitrary, but should end with .v)
|             |         |- testbench_tb.v (whose name is arbitrary, but should end with _tb.v)
|             |
|             |- submit 
|                     |- *.v
|
|- home
|     |- test
|     |     |- exec.py
|     |     
|     |
|     |- ojfiles
|     |       |- teacher
|     |       |- student


You can run this file by executing:
    export PATH=/usr/local/bin/:/root/gcc/gcc141/bin:$PATH && export LD_LIBRARY_PATH=/root/gcc/gcc141/lib:/root/gcc/gcc141/lib64:/root/gcc/gcc141/libxec:$LD_LIBRARY_PATH && python3.8 /home/test/exec.py
in a docker image/container.
"""


class HtmlBlock:
    """
    This class is a simple wrapper to produce html components.
    Script, title, style, and table, p, div can be added in to this class.

    Using stop_append() and start_append() to switch appending mode.
    """

    def __init__(self):
        self.html = ""
        self.script = ""
        self.title = ""
        self.style = ""
        self.contents = []
        self.cnt = 0
        self.app = True

    def stop_append(self):
        """
        stop appending content and return the content it generated.
        """
        self.app = False

    def start_append(self):
        """
        start appending content and STOP return the content it generated.
        """
        self.app = True

    def get_append(self):
        return self.app

    def set_append(self, value):
        self.app = value

    def parse_dic(self, dic: dict):
        """
        A simple method whose function is converting a dict to the format can attach to a label.
        """
        p = ""
        if dic is None:
            dic = {}
        for d in dic.keys():
            if type(dic[d]) == dict:
                p += f"{d}='"
                for dd in dic[d].keys():
                    p += f"{dd}:{dic[d][dd]};"
                p += "' "
            elif type(dic[d]) == list:
                for dd in dic[d]:
                    p += f'{d}="{dd}" '
            else:
                p += f"{d}='{dic[d]}' "
        return p

    def generate_html(self, supp=None) -> str:
        """
        Wrapping and output whole html string.
        """
        if supp is None:
            supp = []
        self.html = (f"<html>"
                     f"<head>"
                     f"<title> {self.title} </title>"
                     f"<script> {self.script} </script>"
                     f"<style> {self.style} </style>"
                     f"</head>"
                     f"<body>")
        if type(supp) == str:
            self.html += supp
        elif type(supp) == list:
            for i in supp:
                self.html += f"{i}"
        for i in range(len(self.contents)):
            self.html += self.contents[i]
        self.html += (f"</body>"
                      f"</html>")
        return self.html

    def add_script(self, script: str):
        self.script += f"\n {script} \n"

    def add_script_from_file(self, script: str):
        with open(script, "r") as f:
            self.script += f"\n {f.read()} \n"

    def add_title(self, title: str):
        self.title = f"\n {title} \n"

    def add_style(self, style: str):
        self.style += f"\n {style} \n"

    def add_style_from_file(self, style: str):
        with open(style, "r") as f:
            self.style += f"\n {f.read()} \n"

    def add_table(self, table_head: list, table_body: list):
        head = ""
        body = ""
        for i in table_head:
            head += f"<th> {i} </th>"
        head = f"<thead><tr> {head} </tr></thead>"
        for r in table_body:
            row = ""
            for c in r:
                if type(c) != list:
                    row += f"<td> {c} </td>"
                else:
                    row += f"<td {c[1]}> {c[0]} </td>"
            body += f"<tr> {row} </tr>"
        body = f"<tbody> {body} </tbody>"
        if self.app:
            self.contents.append(f"<table> {head} {body} </table>")
            self.cnt += 1
        else:
            return f"<table> {head} {body} </table>"

    def add_p(self, px: list or str, dic=None):
        mp = ""
        if type(px) == str:
            mp = f"<p {self.parse_dic(dic)}> {px} </p>"
        else:
            for i in px:
                mp += f"{i}<br>"
            mp = f"<p {self.parse_dic(dic)}> {mp} </p>"
        if self.app:
            self.contents.append(mp)
            self.cnt += 1
        else:
            return mp

    def add_h(self, h: str, lv: int):
        if self.app:
            self.contents.append(f"<h{lv}>{h}</h{lv}>")
            self.cnt += 1
        else:
            return f"<h{lv}>{h}</h{lv}>"

    def add_div(self, div: list or str, dic=None):
        mp = ""
        if type(div) == str:
            mp = f"<div {self.parse_dic(dic)}>{div}</div>"
        else:
            for i in div:
                mp += f"{i}<br>"
            mp = f"<div {self.parse_dic(dic)}> {mp} </p>"
        if self.app:
            self.contents.append(mp)
            self.cnt += 1
        else:
            return mp


html_blk = HtmlBlock()


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

    app = html_blk.get_append()
    html_blk.start_append()
    html_blk.add_title("测试结果")
    html_blk.add_script_from_file("/home/test/exec.js")
    # it's okay for a single page.
    html_blk.add_style_from_file("/home/test/exec.css")
    html_blk.stop_append()

    h1 = html_blk.add_h("测试结果", 1)
    tab = html_blk.add_table(["项目", "结果"],
                             [
                                 ["判定", [f"{verdict}", "class='verdict'"]],
                                 ["得分", f"{score}"],
                                 ["评论", [f"{comment}", "class='comment'"]],
                                 ["详细信息", f"{xx}"]
                             ])

    html_content = html_blk.generate_html([h1, tab])
    html_blk.set_append(app)

    CG_result.update({"detail": html_content})
    return CG_result


def load_param(conf: dict):
    def check_name_match(str1: str, str2: str) -> bool:
        # remove all "_"s, and convert all letters to lowercase
        str2 = str2.lower()
        str1 = str1.lower()
        str2 = str2.replace('_', '')
        str1 = str1.replace('_', '')
        return str1 == str2

    def check_name_in(str1: str, str2: list):
        for s in str2:
            if check_name_match(str1, s):
                return s  # return the key.
        return None


    if os.path.exists(conf["config_path"]):
        with open(conf["config_path"]) as f:
            conf_data = yaml.load(f, Loader=yaml.FullLoader)
        configurables = [
            "test_src_path",
            "submit_src_path",
            "test_dst_path",
            "test_point_number",
            "test_point_names",
            "necessary_files",
            "no_frac_points",
            "display_wave"
        ]

        for c in configurables:
            s = check_name_in(c, conf_data.keys())
            if s is not None:
                # find a valid key
                conf.update({c: conf_data[s]})

def prepare_files(conf: dict):
    test_ans_srcs = []
    main_test_tb_srcs = []
    student_ans_srcs = []
    other_necessary_files = []

    # To find all necessary files
    # These files will be copied to dst
    if len(conf["necessary_files"]) != 0:
        for f in conf["necessary_files"]:
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

    detail = ""
    app = html_blk.get_append()
    html_blk.stop_append()
    if len(main_test_tb_srcs) == 0:
        detail += html_blk.add_p("No testbench! Please contact your TA.", {"class": "error_head"})
    if len(test_ans_srcs) == 0:
        detail += html_blk.add_p("No answer! Please contact your TA.", {"class": "error_head"})
    if len(student_ans_srcs) == 0:
        detail += html_blk.add_p("No answer submitted! Please check your work.", {"class": "error_head"})
    if len(other_necessary_files) != len(conf["necessary_files"]):
        detail += html_blk.add_p("No necessary files! Please contact your TA.", {"class": "error_head"})
    html_blk.set_append(app)

    return detail, [test_ans_srcs, main_test_tb_srcs, student_ans_srcs, other_necessary_files]


def compile_and_run(conf: dict, file_lists: list):
    test_ans_srcs, main_test_tb_srcs, student_ans_srcs, other_necessary_files = file_lists
    detail = ""
    app = html_blk.get_append()
    html_blk.stop_append()
    # make main test
    comp_teacher = make(conf["test_dst_path"] + "teacher/", test_ans_srcs, main_test_tb_srcs, other_necessary_files)
    if comp_teacher[1] == 1:
        detail += html_blk.add_p("Compiling failed in teacher's code. Please contact your TA.", {"class": "error_head"})
        detail += html_blk.add_p("Error messages are as follows:")
        detail += html_blk.add_div(comp_teacher[0], {"class": "error_message"})

    # make student ans
    comp_student = make(conf["test_dst_path"] + "student/", student_ans_srcs, main_test_tb_srcs, other_necessary_files)
    if comp_student[1] == 1:
        detail += html_blk.add_p("Compiling failed in your code. Please check your work.", {"class": "error_head"})
        detail += html_blk.add_p("Error messages are as follows:")
        detail += html_blk.add_div(comp_student[0], {"class": "error_message"})

    # main testpoint ready
    teacher_result = execute(conf["test_dst_path"] + "teacher/")
    if teacher_result[1] == 1:
        detail += html_blk.add_p("Executing failed in teacher's code. Please contact your TA.",
                                 {"class": "error_head"})
        detail += html_blk.add_p("Error messages are as follows:")
        detail += html_blk.add_div(teacher_result[0], {"class": "error_message"})

    student_result = execute(conf["test_dst_path"] + "student/")
    # result file will store in the same directory
    if student_result[1] == 1:
        detail += html_blk.add_p("Executing failed in your code. Please check your work.", {"class": "error_head"})
        detail += html_blk.add_p("Error messages are as follows:")
        detail += html_blk.add_div(student_result[0], {"class": "error_message"})

    teacher_result[0] = teacher_result[0].split("<br>")
    student_result[0] = student_result[0].split("<br>")

    html_blk.set_append(app)

    return detail, teacher_result, student_result


def generate_wave(test_results: list, first_mismatch_line: int, test_num: int, ttl_cnt: int):
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
            "text": f'Wave Diff {test_num}',
            "tick": 0,
            "every": 2
        },
        "config": {
            "skin": "narrow"
        },
    }

    sig_names = []

    # find all signal names we captured
    sig_n_val = re.split('[,:]', test_results[0][0])
    for i in sig_n_val:
        r = re.split('=', i)
        sig_names.append(r[0])

    sig_and_val = [[[] for i in range(len(sig_names))], [[] for i in range(len(sig_names))]]
    sig_and_val_compact = [[[] for i in range(len(sig_names))], [[] for i in range(len(sig_names))]]

    start_line = max(0, first_mismatch_line - 200)
    end_line = min(min(ttl_cnt, len(test_results[1])), first_mismatch_line + 200)

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

    return svg_string


def judge_one(config_dict: dict, number_test: int, total_num: int):
    CG_result = {
        "detail": "",
        "verdict": "",
        "HTML": "True",
        "score": 0,
        "comment": ""
    }

    detail = ""
    comment = ""
    test_passed = 0
    ttl_cnt = 0
    teacher_result_list = []
    student_result_list = []
    svg_string = ""

    blks = ""
    svgs = ""

    # to prepare answer, testbench, student's answer & other files required by the yaml file.
    d, file_lists = prepare_files(config_dict)
    detail += d
    test_ans_srcs, main_test_tb_srcs, student_ans_srcs, other_necessary_files = file_lists
    # compile and run.
    d, teacher_result, student_result = compile_and_run(config_dict, file_lists)
    detail += d

    ce_flag = teacher_result[1] == 1 or student_result[1] == 1

    if ce_flag:
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
        if config_dict['display_wave']:
            test_results = [teacher_result_list, student_result_list]
            svg_string = generate_wave(test_results, first_mismatch_line, number_test, ttl_cnt)

        err_cnt = 0 if first_mismatch_line == -1 else 1

    r = difflib.SequenceMatcher(None, teacher_result_list, student_result_list).ratio()

    if ce_flag:
        colour = "#9E3DD0"
        verdict = "CE"
        r = 0
    elif err_cnt == 0:
        comment = "Accepted"
        colour = "#5EB95E"
        verdict = "AC"
        r = 1
        test_passed += 1
    elif not config_dict['no_frac_points'] and r >= 0.60:
        colour = "#E67D22"
        verdict = "PC"
        comment = "Partially Correct"
    else:
        colour = "#E74C3B"
        verdict = "WA"
        comment = "Wrong Answer"

    html_blk.stop_append()

    div_num = html_blk.add_div(f"#{number_test}", {"style": {"float": "left"}})
    div_verdict = html_blk.add_div(f"{verdict}", {"class": "v-align"})

    blks = html_blk.add_div(f"{div_num} {div_verdict}", {
        "style": {
            "background-color": colour,
        },
        "class": ["button", "test_blk_container"],
        "onclick": f"collapse({number_test}, {total_num})",
        "title": "点击展示/隐藏本测试点波形"
    })

    if config_dict['display_wave']:
        if len(svg_string) != 0:
            svgs = html_blk.add_div(f"{svg_string}", {
                "class": "my_svg_container",
                "id": f"svg_wave_{number_test}"
            })

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

    return CG_result, blks, svgs


if __name__ == '__main__':
    """ ==========================================================
                           LOADING CONFIG...
        =========================================================="""

    config_dict = {
        "config_path": "/coursegrader/testdata/config.yaml",
        "test_src_path": "/coursegrader/testdata/",
        "submit_src_path": "/coursegrader/submit/",
        "test_dst_path": "/home/ojfiles/",
        "necessary_files": [],
        # default: only one testpoint
        "test_point_number": 0,
        "test_point_names": [],
        "no_frac_points": True,
        "display_wave": True
    }

    # please ignore spelling mistakes
    # reading configurations from /coursegrader/testdata/config.yaml
    load_param(config_dict)
    # if the yaml file doesn't exist, act as older OJs

    mark = 0
    blks = []
    svgs = []
    app = html_blk.get_append()
    html_blk.stop_append()
    dx = html_blk.add_div(f" ", {
        "style": {
            "width": "100vw",
        }})
    html_blk.start_append()

    """ ==========================================================
                          JUDGE MAIN TEST POINT
        =========================================================="""
    CG_result, blk, svg = judge_one(config_dict, 0, config_dict['test_point_number'])
    blks.append(blk)
    if config_dict['display_wave']:
        svgs.append(svg)

    if CG_result['score'] == "100" or config_dict["test_point_number"] == 0 or len(
            config_dict["test_point_names"]) != 0 and len(config_dict["test_point_names"]) != config_dict[
        "test_point_number"] or CG_result['verdict'] == "CE":
        if config_dict['display_wave']:
            CG_result.update({"detail": f"{CG_result['detail']} {blks[0]} {svgs[0]} {dx}"})
        else:
            CG_result.update({"detail": f"{CG_result['detail']} {blks[0]}"})
        CG_result = generate_html_output(CG_result)
        output_final = json.dumps(CG_result)
        quitx(output_final)

    """ ==========================================================
                        JUDGE SUB TEST POINTS
        =========================================================="""

    test_cnt = config_dict["test_point_number"]

    for i in range(test_cnt):
        config_bk = config_dict.copy()

        sub_test_tb_src = []
        if len(config_bk["test_point_names"]) == 0:
            sub_test_name = f"point{i}"
        else:
            sub_test_name = config_bk["test_point_names"][i]

        # print(f"entering {sub_test_name}")
        config_bk.update({"test_src_path": os.path.join(config_dict["test_src_path"], sub_test_name)})
        config_bk.update({"test_dst_path": os.path.join(config_dict["test_dst_path"], sub_test_name)})

        CG_result_sub, blk, svg = judge_one(config_bk, i + 1, test_cnt)
        blks.append(blk)
        if config_dict['display_wave']:
            svgs.append(svg)

        CG_result.update({"comment": f"{CG_result['comment']} <br> {CG_result_sub['comment']}"})
        CG_result.update({"detail": f"{CG_result['detail']} <br> {CG_result_sub['detail']}"})

        if CG_result_sub['score'] == "100":
            mark += 1

    CG_result.update({"score": f"{mark}"})

    if mark == 0:
        CG_result.update({"verdict": f"WA"})
    elif mark != test_cnt and not config_dict['no_frac_points']:
        CG_result.update({"verdict": f"PC"})
    else:
        CG_result.update({"verdict": f"AC"})

    for i in range(len(blks)):
        CG_result.update({"detail": f"{CG_result['detail']} {blks[i]}"})
    if config_dict['display_wave']:
        for i in range(len(svgs)):
            CG_result.update({"detail": f"{CG_result['detail']} {svgs[i]}"})
        CG_result.update({"detail": f"{CG_result['detail']} {dx}"})

    CG_result = generate_html_output(CG_result)
    output_final = json.dumps(CG_result)
    quitx(output_final)
