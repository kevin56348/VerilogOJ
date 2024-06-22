# Makefile
TEST_POINT := 
TEACHER_DEST := /coursegrader/testdata
STUDENT_DEST := /coursegrader/submit
BUILD_DIR := /home/ojfiles/build

ifeq ($(TEST_POINT), )
	TEACHER_TESTBENCH := $(shell ls $(TEACHER_DEST) 2>/dev/null | grep ".*_tb.v" | sed "s:^:$(TEACHER_DEST)/:") 
else
	TEACHER_TESTBENCH := $(shell ls $(TEACHER_DEST)/point$(TEST_POINT) 2>/dev/null | grep ".*_tb.v" | sed "s:^:$(TEACHER_DEST)/point$(TEST_POINT)/:") 
endif

TEACHER_FILES := $(shell ls $(TEACHER_DEST) 2>/dev/null | grep ".v" | grep -v ".*_tb.v" | sed "s:^:$(TEACHER_DEST)/:")
STUDENT_FILES := $(shell ls $(STUDENT_DEST) 2>/dev/null | grep ".v" | sed "s:^:$(STUDENT_DEST)/:")

all: clean teacher_exe student_exe

teacher_exe: $(TEACHER_FILES) $(TEACHER_TESTBENCH)
	mkdir -p $(BUILD_DIR)
	@echo $(TEACHER_DEST)/point$(TEST_POINT)
	iverilog -I $(TEACHER_DEST) -o $(BUILD_DIR)/teacher_exe$(TEST_POINT) $(TEACHER_FILES) $(TEACHER_TESTBENCH)

student_exe: $(STUDENT_FILES) $(TEACHER_TESTBENCH)
	mkdir -p $(BUILD_DIR)
	@echo $(TEACHER_DEST)/point$(TEST_POINT)
	iverilog -I $(TEACHER_DEST)/point$(TEST_POINT) -I $(STUDENT_DEST) -o $(BUILD_DIR)/student_exe$(TEST_POINT) $(STUDENT_FILES) $(TEACHER_TESTBENCH)

clean_teacher:
	rm -f $(BUILD_DIR)/teacher_exe*

clean_student:
	rm -f $(BUILD_DIR)/student_exe*

clean: clean_teacher clean_student
