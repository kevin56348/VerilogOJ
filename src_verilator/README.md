# Verilator测评说明

## 简介


本细粒度verilog测评机基于verilator，可以自行配置测评点数量与名称，可以设置**不同难度**的测试点对同一个verilog代码进行仿真测试。

该测评机为CG平台设计，如需移植到其它平台，修改config.yaml中对应的路径即可。一个针对CG平台的配置文件如下：

```yaml
TestSrcPath: "/coursegrader/testdata/" # 标准答案以及测试用例存放的根目录
SubmitSrcPath: "/coursegrader/submit/" # 待测文件的根目录
TestDstPath: "/home/ojfiles/" # 中间文件生成路径，需要有写权限

TestPointNumber: 3 # 子测试点数量，若没有子测试点，可以为 0
TestPointNames :   # 子测试点名称列表，需要与子测试点数量保持一致。
                   # 如果子测试点数量不为 0，而此项为空，则以 point0 开始以此命名每个测试点
  - sltui
  - mod.w
  - mul.w

NessaseryFiles: # 其他必要文件，必须有文件后缀。该路径为相对每一个测试点的路径。
  - func/inst_ram.mif
  - func/data_ram.mif
```

- `/coursegrader`路径为CG默认的挂载路径，其中
  - `/coursegrader/testdata`中会默认**只读**挂载上传的测试点。该文件夹下需要存放作为正确答案的`.v`文件，以及作为测试用例的`*_tb.v`文件。
  - `/coursegrader/submit`中会默认**只读**挂载待测试文件

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

使用verilator的好处是快速，便捷。

## 使用方法

Verilator测评机需要的测试数据有所变化。本测评机需要testdata下存放一个config.yaml文件，如果文件不存在则所有参数为默认值。参数默认值如下所示：

|        TestSrcPath        |      SubmitSrcPath      |   TestDstPath    | TestPointNumber | TestPointNames | NessaseryFiles |
| :-----------------------: | :---------------------: | :--------------: | :-------------: | :------------: | :------------: |
| "/coursegrader/testdata/" | "/coursegrader/submit/" | "/home/ojfiles/" |        0        |       []       |       []       |

config.yaml示例如下所示：

```yaml
TestSrcPath: "/coursegrader/testdata/" # 标准答案以及测试用例存放的根目录
SubmitSrcPath: "/coursegrader/submit/" # 待测文件的根目录
TestDstPath: "/home/ojfiles/" # 中间文件生成路径，需要有写权限

TestPointNumber: 3 # 子测试点数量，若没有子测试点，可以为 0
TestPointNames :   # 子测试点名称列表，需要与子测试点数量保持一致。
                   # 如果子测试点数量不为 0，而此项为空，则以 point0 开始以此命名每个测试点
  - sltui
  - mod.w
  - mul.w

NessaseryFiles: # 其他必要文件，必须有文件后缀。该路径为相对每一个测试点的路径。
  - func/inst_ram.mif
  - func/data_ram.mif
```

### 答案、测试用例与提交目录

其中，TestSrcPath、SubmitSrcPath为CG默认值，TestSrcPath为测试用例、标准答案、相关文件存放位置，SubmitSrcPath为学生提交文件位置，不建议改动。TestDstPath为生成文件目录，编译结果将全部生成在此文件夹下。

注意：TestSrcPath与SubmitSrcPath均为只读，无法修改。不可以原地编译生成文件。

### 子测试点配置

TestPointNumber用于配置子测试点数量，默认为0。

TestPointNames用于配置子测试点名称，默认为point$i$，其中$i$为测试点编号，从0开始。

### 必要文件配置

其他必要的，非.v文件必须带有扩展名。


## 测试原理

该测评机捕捉dislpay等语句输出的信息，句首必须为monitor才可以被捕获到。

## 测试结果

测试结果按照CG的要求返回，是一个JSON字符串。该字符串包括以下字段：verdict、HTML、score、comment、detail。
目前添加了简单的div元素以美化显示。