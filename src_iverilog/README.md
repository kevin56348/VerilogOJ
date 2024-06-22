# 细粒度Verilog测评机简介

本细粒度verilog测评机基于iverilog，采用了自动检测测试点数量的方式，可以设置**不同难度**的测试点对同一个verilog代码进行仿真测试。

该测评机为CG平台设计，因此一些路径已经按照CG平台的规则写死。如需移植到其它平台，修改对应的路径即可。一些固定路径如下：

- `/home/pythonfile`路径为该项目SRC文件夹内容所在处，主要存放测评机代码
- `/coursegrader`路径为CG默认的挂载路径，其中
  - `/coursegrader/testdata`中会默认**只读**挂载上传的测试点。该文件夹下需要存放作为正确答案的`.v`文件，以及作为测试用例的`*_tb.v`文件。**只可以存在一个`*_tb.v`文件作为测试激励文件**。
    - `/coursegrader/testdata/pointn`，其中$n$为测试点序号。$n$必须从0开始，且必须连续。
      - 每一个`pointi`中只需要存放测试激励，即`*_tb.v`文件。
      - 该项可以不存在，此时将会默认从`/coursegrader/testdata`下获取标准答案与测试激励。
      - 如果存放在`/coursegrader/testdata`下的测试点通过，则所有`pointi`文件夹下的测试点均不会被测试。因此，建议`/coursegrader/testdata`下的测试点为所有`pointi`下测试点的超集。或者添加`noMainTestPoint : True`到`config.yaml`中
  - `/coursegrader/submit`中会默认**只读**挂载待测试文件

合法的测试用例结构如下所示：

有6个子测试点的结构：

```text
.
|-- submit
|   `-- wire.v
|-- testdata 
    |--config.yaml
    |-- point0
    |   `-- wire_tb.v
    |-- point1
    |   `-- wire_tb.v
    |-- point2
    |   `-- wire_tb.v
    |-- point3
    |   `-- wire_tb.v
    |-- point4
    |   `-- wire_tb.v
    |-- point5
    |   `-- wire_tb.v
    |-- wire.v
    `-- wire_tb.v
```

没有子测试点的结构：

```text
.
|-- submit
|   `-- wire.v
|-- testdata
    |--config.yaml
    |-- wire.v
    `-- wire_tb.v
```

没有主测试点的结构（此时需要在config.yaml中加入`noMainTestPoint : True`）：

```text
.
|-- alu.v
|-- config.yaml
|-- mycpu_top.v
|-- point0
|   |-- async_ram_tb.v
|   |-- bridge_1x2_tb.v
|   |-- confreg_tb.v
|   |-- func
|   |   |-- data_ram.coe
|   |   |-- data_ram.mif
|   |   |-- inst_ram.coe
|   |   |-- inst_ram.mif
|   |   |-- rom.vlog
|   |   `-- test.s
|   |-- mycpu_tb.v
|   `-- soc_lite_top_tb.v
|-- regfile.v
`-- tools.v
```

本测评机测评点文件的结构较为复杂，但由于精力有限，没有让这个过程更加人性化。又因为iverilog对于复杂工程的测评有一些力不从心，因此基于iverilog的方法不再进行维护。
