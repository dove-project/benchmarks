#!/usr/bin/env python3
import random
import csv
import os
import subprocess
import collections

METADATA_FILE = "../examples/sample.metadata"

FRONTEND_DIR = "../../dove-frontend-r/src"
# Relative to above directory
DATA_CSV = "../../dove-backend/examples/data.csv"
HEADER_FILE = "../../dove-frontend-r/examples/ec-original/init_data.R"

DATASET_NAME = "sample"
# Must be the same as HEADER_FILE and METADATA_FILE
DATA_NROW = 10
DATA_NCOL = 10

RATIOS = [0.1, 0.2, 0.3, 0.4, 0.5]

TESTS_UNARY = {
    # True unary operations.
    "No": "z <- +geno",
    "Negation": "z <- -geno",
    "BitwiseNot": "z <- !geno",
    # Math group generics, general functions.
    "Abs": "z <- abs(geno)",
    "Sign": "z <- sign(geno)",
    "Sqrt": "z <- sqrt(geno)",
    "Floor": "z <- floor(geno)",
    "Ceiling": "z <- ceiling(geno)",
    # Math group generics, trigonometry-related functions.
    "Exp": "z <- exp(geno)",
    "Log": "z <- log(geno)",
    "Cos": "z <- cos(geno)",
    "Sin": "z <- sin(geno)",
    "Tan": "z <- tan(geno)",
    # Print is skipped because it is data-dependent.
    # NA-Check.
    "IsNa": "z <- is.na(geno)",
    # Summary.
    "Sum": "z <- sum(geno, na.rm=T)\n",
    "Prod": "z <- prod(geno, na.rm=T)\n",
    "Mean": "z <- mean(geno, na.rm=T)\n",
    "Any": "z <- any(geno, na.rm=T)\n",
    "All": "z <- all(geno, na.rm=T)\n",
    "RowSums": "z <- rowSums(geno, na.rm=T)\n",
    "ColSums": "z <- colSums(geno, na.rm=T)\n",
    "RowMeans": "z <- rowMeans(geno, na.rm=T)\n",
    "ColMeans": "z <- colMeans(geno, na.rm=T)\n",
    "Min": "z <- min(geno, na.rm=T)\n",
    "Max": "z <- max(geno, na.rm=T)\n",
    "Range": "z <- range(geno, na.rm=T)\n",
}

TESTS_BINARY = {
    # Arithmetic operators.
    "Addition": "z <- geno + geno\n",
    "Subtraction": "z <- geno - geno\n",
    "Multiplication": "z <- geno * geno\n",
    "Division": "z <- geno / geno\n",
    "Pow": "z <- geno ^ 2\n",
    "Mod": "z <- geno %% 2\n",
    "IDiv": "z <- geno %/% 4\n",
    "MatMul": "z <- geno[1:10] %*% geno[1:10]\n",

    # Comparison operators.
    "Equal": "z <- geno == 1\n",
    "GreaterThan": "z <- geno > 1\n",
    "LessThan": "z <- geno < 1\n",
    "NotEqual": "z <- geno != 1\n",
    "GreaterThanEqual": "z <- geno >= 1\n",
    "LessThanEqual": "z <- geno <= 1\n",

    # Logic operators.
    "BitwiseAnd": "z <- (geno != 0) & (geno != 1)\n",
    "BitwiseOr": "z <- (geno != 0) | (geno != 1)\n",

    # Log (with two arguments).
    "LogBin": "z <- log(geno, base = dove.wrap(2))\n",

    # PMin/PMax
    "PMax": "z <- pmax(geno + 1, geno - 1)\n",
    "PMin": "z <- pmin(geno + 1, geno - 1)\n",
}

# Uncomment to test operations.
TESTS = collections.OrderedDict(sorted({**TESTS_UNARY, **TESTS_BINARY}.items()))
GDB_FILE = "../../benchmarks/src/trace.gdb"

# Uncomment to test data loading.
# TESTS = {"Load": ""}  # our header script handles the data anyway
# GDB_FILE = "../../benchmarks/src/load.gdb"

VALUES = ["1", "0"]  # uncomment to test different % of 1
# VALUES = ["NA", "1"]   # uncomment to test different % of NAs

EXPORT_SCRIPT = "tmp <- scan('../../dove-backend/src/{}')\ndove.export_data('../../dove-backend/src/{}', tmp)\n"

def process(ratio, if_out, else_out):
    to_export = ["source('dove_export.R')\n"]
    lines = None
    entries = {}
    with open(METADATA_FILE) as f:
        lines = f.readlines()
    for line in lines:
        entry = line.split()
        with open(entry[0] + ".txt", "w") as src:
            output = ""
            for i in range(int(entry[2])):
                for j in range(int(entry[3])):
                    if random.random() < ratio:
                        output += if_out + " "
                    else:
                        output += else_out + " "
            src.write(output)

        to_export += EXPORT_SCRIPT.format(entry[0] + ".txt", entry[0])
        entries[entry[1]] = [int(entry[2]), int(entry[3])]

    if DATASET_NAME not in entries:
        raise ValueError("cannot find " + DATASET_NAME)

    if DATA_NROW != entries[DATASET_NAME][0] or DATA_NCOL != entries[DATASET_NAME][1]:
        raise ValueError("mismatched dimensions for " + DATASET_NAME)

    if ratio > 0:
        os.chdir(FRONTEND_DIR)
        with open("/tmp/dove_exec_trace_export.R", "w") as scr:
            scr.writelines(to_export)
        subprocess.run(["R", "-f", "/tmp/dove_exec_trace_export.R"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        os.chdir("../../dove-backend/src")

    return entries


def main():
    results = {}

    print("TESTS")
    count = 1
    for k, v in TESTS.items():
        print("Testing {} ({}/{})...".format(k, count, len(TESTS)))
        count += 1
        results[k] = {}
        entries = process(-1, VALUES[0], VALUES[1])
        os.chdir(FRONTEND_DIR) #CHANGE DIR TO FRONTEND
        with open(DATA_CSV, "w") as out:
            writer = csv.writer(out)
            for name, dim in entries.items():
                writer.writerow([name, dim[0], dim[1]])

        with open("/tmp/dove_exec_trace_script.R", "w") as scr:
            scr.write("source('dove.R')\nsource('{}')\n{}".format(HEADER_FILE, v))
        subprocess.run(["R", "-f", "/tmp/dove_exec_trace_script.R"], stdout=subprocess.DEVNULL, check=True)
        os.chdir("../../dove-backend/src") #RETURN TO BACKEND

        for ratio in RATIOS:
            print("  Testing {}, ratio {}...".format(k, ratio))
            process(ratio, VALUES[0], VALUES[1])
            result = subprocess.run(["gdb", "--batch", "--command=" + GDB_FILE, "splitapp"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#            print(result)
            results[k][ratio] = [s for s in result.stdout.decode("utf-8").split('\n') if "Recorded" in s][0]
        print("Result for {} ({}/{}):".format(k, count, len(TESTS)))
        record = results[k][RATIOS[0]].split(" for thread ")[0]
        print("  " + record)
        for ratio in RATIOS[1:]:
            found = results[k][ratio].split(" for thread ")[0]
            if (record != found):
                print("  MISMATCH FOR {} RATIO {}:".format(k, ratio))
                print("    " + found)


if __name__ == "__main__":
    main()
