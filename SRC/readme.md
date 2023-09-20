# Verilog Online Judge Documentation
## Basic information

This OJ originally build by ???, write all python files and shell file `test`. 

This docker image is built by wyc, add features by zzh, et al. based on a brand new ubuntu image. Installed python3, wavedrom, iverilog and other nessesary packages and utils. 

This judge system can:

- Judge submits in multiple judge points
- Batch judge
- Return wave graph of first wrong answer(WA) point 

Todo list:

- Beautiful judge result
- Changable wrong messages
- Simpler testbench structure

## Technical infromation

1. run `python3 /home/pythonfile/execute.py` to start.

1. config.py contains all changable variables.

1. `test` contains the most enssential code.

1. all testbenches should put in `/coursegrader/testdata/point$i`, which i is a whole number from 0 to n, where n is the number of total judge points.

1. major testbench and answer file should put in `/coursegrader/testdata`.

1. all testbenches' name should end in `_tb.v`, all answers' name should end in `.v`, no more unrelated file should put in folder `testdata`.

## Author 

This OJ built by many students in SCCE, USTB. I can't acuire their name and contributes. However, all names which appeared in docker images would be showed below:

-----

ustb/test:v13 	-author wzg, (et al.)
ustb/oj:v2 	-author wyc, zzh, et al.

-----

END OF FILE
