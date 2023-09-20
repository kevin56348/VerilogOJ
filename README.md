# Introduction {#sec:-introduction}

To fill up the blank of verilog online judger, which could boost the
verifying of open-problem in teaching and in exam, we designed this
verilog judger based on `iverilog`, `python` and `bash`. It can be
simply run by using a docker container in CG platform, or somewhere
else, and generate a `json` output via standard output for further
usage.

It could automatically detect the number of test points, and offers the
reference and wrong answer of the first test point where error occurs.

# Usage {#sec:-usage2}

## OJ Structure

See doc.pdf

## Testbench

Testbench should offer some output through the console, otherwise it can
not judge whether the answer is right or wrong. Sentences such as
`$display`, `$monitor` or `$write` can be used.

[^1]: If it doesn't pass the main testbench, sub-testbench will work.
    Otherwise, those sub-testbench will be bypassed.
