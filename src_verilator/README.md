# Verilator 测评说明

## 简介

本细粒度 Verilog 测评机基于 `Verilator`，可以自行配置测评点数量与名称。因此老师与助教可以设置 **不同难度** 的测试点对 *
*同一个** Verilog 代码进行仿真测试，给出具有中间值的分数（而非只有 0 或 100）。

该测评机为 CG 平台设计，如需移植到其它平台，修改 `config.yaml` 中对应的路径即可。一个针对 CG 平台的配置文件如下：

```yaml
# This is a sample configuration file.
# Suitable for CG platform
TestSrcPath: /coursegrader/testdata/
SubmitSrcPath: /coursegrader/submit/
TestDstPath: /home/ojfiles/
# if there is only one testpoint, just type 0
TestPointNumber: 0
# if there are no sub-testpoints, you MUST ignore TestPointNames
#TestPointNames:
#  - 1
#  - 2
#  - 3
# Normally, leave it blank
#NecessaryFiles:
#  - a
#  - b
#  - c
DisplayWave: TRUE
```

- `/coursegrader` 路径为 CG 默认的挂载路径，其中
    - `/coursegrader/testdata`中会默认 **只读** 挂载上传的测试点。该文件夹下需要存放作为正确答案的 `.v` 文件，以及作为测试用例的
      `*_tb.v` 文件；
    - `/coursegrader/submit` 中会默认 **只读** 挂载待测试文件。

一个合法的测试用例结构如下所示：

```text
.
|-- alu.v
|-- async_ram_tb.v
|-- bridge_1x2_tb.v
|-- config.yaml
|-- confreg_tb.v
|-- func
|   |-- data_ram.mif
|   `-- inst_ram.mif
|-- mod.w
|   |-- async_ram_tb.v
|   |-- bridge_1x2_tb.v
|   |-- confreg_tb.v
|   |-- func
|   |   |-- data_ram.mif
|   |   `-- inst_ram.mif
|   |-- mycpu_tb.v
|   `-- soc_lite_top_tb.v
|-- mul.w
|   |-- async_ram_tb.v
|   |-- bridge_1x2_tb.v
|   |-- confreg_tb.v
|   |-- func
|   |   |-- data_ram.mif
|   |   `-- inst_ram.mif
|   |-- mycpu_tb.v
|   `-- soc_lite_top_tb.v
|-- mycpu_tb.v
|-- mycpu_top.v
|-- regfile.v
|-- sltui
|   |-- async_ram_tb.v
|   |-- bridge_1x2_tb.v
|   |-- confreg_tb.v
|   |-- func
|   |   |-- data_ram.mif
|   |   `-- inst_ram.mif
|   |-- mycpu_tb.v
|   `-- soc_lite_top_tb.v
|-- soc_lite_top_tb.v
`-- tools.v
```

使用 Verilator 的好处是快速，便捷。

## 使用方法

Verilator 测评机需要在 `testdata` 下存放一个 `config.yaml` 文件，如果文件不存在则所有参数为默认值。参数默认值如下所示：

```yaml
TestSrcPath: /coursegrader/testdata/,
SubmitSrcPath: /coursegrader/submit/,
TestDstPath: /home/ojfiles/,
NecessaryFiles: [ ],
TestPointNumber: 0,
TestPointNames: [ ],
NoFracPoints: True,
DisplayWave: True
```

`config.yaml` 示例如下所示：

```yaml
TestSrcPath: "/coursegrader/testdata/" # 标准答案以及测试用例存放的根目录
SubmitSrcPath: "/coursegrader/submit/" # 待测文件的根目录
TestDstPath: "/home/ojfiles/" # 中间文件生成路径，需要有写权限

TestPointNumber: 3 # 子测试点数量，若没有子测试点，可以为 0
TestPointNames: # 子测试点名称列表，需要与子测试点数量保持一致。
  # 如果子测试点数量不为 0，而此项为空，则以 point0 开始以此命名每个测试点
  - sltui
  - mod.w
  - mul.w

NecessaryFiles: # 其他必要文件。该路径为相对每一个测试点的路径。
  - func/inst_ram.mif
  - func/data_ram.mif
```

注意，测试脚本中读入 yaml 时会自动忽略下划线 `_`，且大小写不敏感。 **不要试图在配置文件中创建只依靠下划线 `_`、大小写进行区分的变量。
**

### 答案、测试用例与提交目录

其中，`TestSrcPath`、`SubmitSrcPath` 为 CG 默认值，`TestSrcPath` 为测试用例、标准答案、相关文件存放位置，`SubmitSrcPath`
为学生提交文件位置，不建议改动。`TestDstPath` 为生成文件目录，编译结果将全部生成在此文件夹下。

注意：`TestSrcPath` 与 `SubmitSrcPath` 均为只读，无法修改。不可以原地编译生成文件。

### 子测试点配置

`TestPointNumber` 用于配置子测试点数量，默认为 0。

`TestPointNames` 用于配置子测试点名称，默认为 `point`$i$，其中 $i$ 为测试点编号，从 0 开始。

### 必要文件配置

其他必要的，非 `.v` 文件。

## 测试原理

该测评机捕捉 `display` 等语句输出的信息，句首必须为 `monitor` 才可以被捕获到。

## 测试结果

测试结果按照 CG 的要求返回，是一个 JSON 字符串。该字符串包括以下字段：`verdict`、`HTML`、`score`、`comment`、`detail`。
其中 `detail` 字段包括一个五行两列的表格，结构如下：

|  项目  |                       结果                       |
|:----:|:----------------------------------------------:|
|  判定  |             `WA`、`CE`、`AC`、`PC` 之一             | 
|  得分  |                  $0 \sim 100$                  | 
|  评论  |                  对 `判定` 的简短描述                  | 
| 详细信息 | 一个 html 网页，会内嵌 `exec.css` 样式文件， `exec.js` 脚本文件 | 

为了更加直观，该表格会重复显示返回 JSON 字符串中的 `verdict`、`comment` 项，是有意为之。

### 编译错误

若测试出现编译错误、执行错误等情况，统一归类至编译错误选项，`verdict` 显示 `CE`。错误信息头部将会使用 `error_head` 类简单描述，详细错误信息使用 `error_message` 类输出，紧随错误信息头部。一个输出的示例如下所示：

<html lang="en">
<body>
    <p style="color: #E74C3B;font-weight: bold;"> Compiling failed in your code. Please check your work.","Error messages are as follows: </p>
    <p style="color: #E67D22;background-color: #F1F1F1;"> 
    %Error: /coursegrader/submit/proc_fsm_ce.v:17:5: syntax error, unexpected output, expecting ','<br>
    17 | output wire Ain ,<br>
    | ^~~~~~<br>
    %Error: /coursegrader/submit/proc_fsm_ce.v:18:5: syntax error, unexpected output, expecting IDENTIFIER or do or final or randomize<br>
    18 | output wire Gin ,<br>
    | ^~~~~~<br>
    %Error: /coursegrader/submit/proc_fsm_ce.v:19:5: syntax error, unexpected output, expecting IDENTIFIER or do or final or randomize<br>
    19 | output wire Gout ,<br>
    | ^~~~~~<br>
    %Error: /coursegrader/submit/proc_fsm_ce.v:20:5: syntax error, unexpected output, expecting IDENTIFIER or do or final or randomize<br>
    20 | output wire addsub ,<br>
    | ^~~~~~<br>
    %Error: /coursegrader/submit/proc_fsm_ce.v:21:5: syntax error, unexpected output, expecting IDENTIFIER or do or final or randomize<br>
    21 | output wire externx<br>
    | ^~~~~~<br>
    %Error: /coursegrader/submit/proc_fsm_ce.v:44:5: syntax error, unexpected assign<br>
    44 | assign inst_load = F == 2'b00;<br>
    | ^~~~~~<br>
    %Error: Exiting due to 6 error(s)<br>
    </p>
    <div style="padding: 8px;display: inline-block;width: 160px;height: 160px;position: relative;z-index: 1; background-color: #9E3DD0;" >
        <div style="float: left;color:white;"> #1 </div>
        <div style="margin: 0;font: small-caps bold 1.8rem sans-serif;width: 160px;text-align: center;line-height: 160px;border: 0 solid #ddd;position: absolute;z-index: 2;top: 0;left: 0;color:white;"> CE </div>
    </div>
</body>
</html>

### 答案错误

若测试出现答案错误，`verdict` 显示 `WA`。此时错误信息应为空。

<html lang="en">
<body>
    <div style="padding: 8px;display: inline-block;width: 160px;height: 160px;position: relative;z-index: 1;background-color: #E74C3B;" >
        <div style="float: left;color:white"> #1 </div>
        <div style="margin: 0;font: small-caps bold 1.8rem sans-serif;width: 160px;text-align: center;line-height: 160px;border: 0 solid #ddd;position: absolute;z-index: 2;top: 0;left: 0;color:white;"> WA </div>
    </div>
</body>
</html>

[//]: # (TODO CONFIGURABLE)
波形图会自动展开。单击 `WA` 可收起波形图。目前波形图只会显示错误点前后各200次的数据，需要在源码中配置该值。

### 部分正确

[//]: # (TODO CONFIGURABLE)
若测试部分正确且达到某一分数阈值，`verdict` 显示 `PC`。此时错误信息应为空，分数应为 $60 \sim 100$ 之间的数值。波形图会自动展开。单击 `PC` 可收起波形图。

<html lang="en">
<body>
    <div style="padding: 8px;display: inline-block;width: 160px;height: 160px;position: relative;z-index: 1;background-color: #E67D22;" >
        <div style="float: left;color:white;"> #1 </div>
        <div style="margin: 0;font: small-caps bold 1.8rem sans-serif;width: 160px;text-align: center;line-height: 160px;border: 0 solid #ddd;position: absolute;z-index: 2;top: 0;left: 0;color:white;"> PC </div>
    </div>
</body>
</html>

### 答案正确

若测试部分正确，`verdict` 显示 `AC`，表示答案被接受。此时错误信息应为空。波形自动收起，但同样可以通过单击评分块展开波形。

<html lang="en">
<body>
    <di style="padding: 8px;display: inline-block;width: 160px;height: 160px;position: relative;z-index: 1;background-color: #5EB95E;" >
        <div style="float: left;color:white"> #1 </div>
        <div style="margin: 0;font: small-caps bold 1.8rem sans-serif;width: 160px;text-align: center;line-height: 160px;border: 0 solid #ddd;position: absolute;z-index: 2;top: 0;left: 0;color:white;"> AC </div>
    </di>
</body>
</html>

### 状态一览表

- CE: Compile Error
- WA: Wrong Answer
- PC: Partially Correct
- AC: Accepted
