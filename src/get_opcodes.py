#!/usr/bin/env python3
import re
import subprocess

PREFIX = "Enclave/"
OBJ_FILES = [
    # "Enclave.o",
    "p_block.o",
    # "symbols.o",
    "runtime.o",
    "primitives.o",
    "unary_op.o",
    "unary/isna.o",
    "unary/mathgen.o",
    "unary/mathtrig.o",
    "unary/plusminus.o",
    "unary/summary.o",
    "unary/print.o",   # data dependent by design
    "unary/ustats.o",  # only the opcode for the dispatch, not the actual.
    "binary_op.o",
    "binary/arith.o",
    "binary/bstats.o", # only the opcode for the dispatch, not the actual.
    "binary/log_bin.o",
    "binary/logic.o",
    "binary/matmul.o",
    "binary/compare.o",
    "binary/pminmax.o",
    "binary/bstats.o",
]

CONDITIONALS = [
]

# LIBFTFP = set(['add','mov','pop','setg','and','movabs','push','setl', 'call','movsd','rep','setle','cdqe','movsx','ret','setne','cmp','movsxd','sar','shl', 'imul','movzx','sbb','shr','je','mul','seta','sub', 'jmp','neg','setae','test', 'jne','not','setbe','xor', 'lea','or','sete']) - set(['jne', 'je'])
LIBFTFP = set(['add','mov','pop','setg','and','movabs','push','setl', 'call','movsd','rep','setle','cdqe','movsx','ret','setne','cmp','movsxd','sar','shl', 'imul','movzx','sbb','shr','je','mul','seta','sub', 'jmp','neg','setae','test', 'jne','not','setbe','xor', 'lea','or','sete'])

SKIP = ['nop',]

opcodes = set()
cond_results = {}
# subprocess.run(["make", "-f", "split.makefile", "clean"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# subprocess.run(["make", "-f", "split.makefile", "all"], check=True)
for obj_file in OBJ_FILES:
    cond_results[obj_file] = set()
    dump = subprocess.run(["objdump", "-M", "intel", "-dr", PREFIX + obj_file], stdout=subprocess.PIPE, check=True).stdout
    for line in dump.decode("utf-8").split("\n"):
        cols = line.split('\t')
        if len(cols) > 2:
            new_code = re.sub(' .*', '', cols[2])
            if new_code == '':
                continue
            # if new_code in CONDITIONALS:
            if new_code not in LIBFTFP and new_code not in SKIP:
                cond_results[obj_file].add(new_code)
            opcodes.add(new_code)


# print(sorted(opcodes))
print(sorted(opcodes - LIBFTFP))
for k,v in cond_results.items():
    print(k,sorted(v))

combo = LIBFTFP.copy()
# for s in ['ja', 'jae', 'jb', 'je', 'jne', 'jge', 'jle', 'repz', 'cmovne', 'movq', 'jns']:
#     combo.add(s)
combo.add("cmovne")
combo = sorted(combo)
for i in range(0, len(combo)):
    print(r'\texttt{' + combo[i] + '}', end='')
    if combo[i] not in LIBFTFP:
        print('*', end='')
    if i % 5 == 4:
        print(r' \\')
    else:
        print(' & ', end='')

