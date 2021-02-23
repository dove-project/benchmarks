#!/usr/bin/env python3
import random
import csv
import os
import subprocess
import collections

FRONTEND_DIR = "../../dove-frontend-r/src/"
BACKEND_DIR = os.getcwd()

EC_SCRIPTS2 = [
    "page_rank"
]

ORIG_LOC = FRONTEND_DIR+"../examples/pagerank/"

EC_RUNSTRINGS2_R = {
        "page_rank": 'v <- page_rank(M, 10)\n'.format(ORIG_LOC)
}

RUNSTRING_R = '\nto.read <- file("'+BACKEND_DIR+'/../examples/sample.data", "rb")\nM <- readBin(to.read, double(), n=100, endian="little")\ndim(M) <- c(10, 10)\nsource("{}calc_{}.R")\nclose(to.read)\n{}\n\n'

RUNSTRING_FEND = 'source("'+FRONTEND_DIR+'../examples/pagerank/secret_{}.R")\n'

def run_r(filename):
    ps = subprocess.run(["/usr/bin/time", "-v", "R", "-f", filename], stderr=subprocess.PIPE, check=True)
    # ps = subprocess.run(["R", "-f", filename], stdout=subprocess.DEVNULL, check=True)
    return ps

def run_enclave():
    ps = subprocess.run(["/usr/bin/time", "-v", "./app"], stderr=subprocess.PIPE, check=True)
    return ps

def run_noenclave():
    ps = subprocess.run(["/usr/bin/time", "-v", "./splitapp"], stderr=subprocess.PIPE, check=True)
    return ps

def test_r(script):
    os.chdir(FRONTEND_DIR)
    results = []

    with open("/tmp/dove_perf_analysis_base.R", "w") as scr:
        scr.write(RUNSTRING_R.format(ORIG_LOC,script, EC_RUNSTRINGS2_R[script]))

    for i in range(0,1):
        results.append((run_r("/tmp/dove_perf_analysis_base.R").stderr).decode('utf8'))
    os.chdir("..")

    with open('results/R_' + script + '.txt', 'w') as outf:
        outf.writelines(results)

    return results

def test_enclave(script):
    results = {}
    results["frontend"] = []
    results["backend"] = []
    # entries = {DATASET_NAME: [DATA_NROW, DATA_NCOL]}
    # os.chdir(FRONTEND_DIR)
    # with open(DATA_CSV, "w") as out:
    #     writer = csv.writer(out)
    #     for name, dim in entries.items():
    #         writer.writerow([name, dim[0], dim[1]])

    with open("/tmp/dove_perf_analysis_fend.R", "w") as scr:
            scr.write(RUNSTRING_FEND.format(script))

    os.chdir(FRONTEND_DIR)
    with open("/tmp/dove_perf_analysis_base.R", "w") as scr:
        scr.write(RUNSTRING_R.format(ORIG_LOC,script, EC_RUNSTRINGS2_R[script]))

    print("  Running front-end...")
    for i in range(0,1):
        results["frontend"].append((run_r("/tmp/dove_perf_analysis_fend.R").stderr).decode('utf8'))
    os.chdir("../../dove-backend/src/")

    with open('../../benchmarks/dynamic/fend_' + script + '.txt', 'w') as outf:
        outf.writelines(results["frontend"])

    print("  Running back-end...")
    for i in range(0,1):
        results["backend"].append(run_enclave().stderr.decode('utf8'))

    with open('../../benchmarks/dynamic/bend_' + script + '.txt', 'w') as outf:
        outf.writelines(results["backend"])

    return results


def test_noenclave(script):
    results = {}
    results["frontend"] = []
    results["backend"] = []

    os.chdir(FRONTEND_DIR)
    with open("/tmp/dove_perf_analysis_noe_fend.R", "w") as scr:
            scr.write(RUNSTRING_FEND.format(script))

    print("  Running front-end...")
    for i in range(0,1):
        results["frontend"].append((run_r("/tmp/dove_perf_analysis_noe_fend.R").stderr).decode('utf8'))
    os.chdir("../../dove-backend/src/")

    print("  Running back-end...")
    for i in range(0,1):
        results["backend"].append(run_noenclave().stderr.decode('utf8'))

    with open('../../benchmarks/dynamic/bend_noe_' + script + '.txt', 'w') as outf:
        outf.writelines(results["backend"])

    return results

def main():
    # subprocess.run(["make", "clean"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # subprocess.run(["make", "all"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("TESTS")
    count = 1
    for script in EC_SCRIPTS2:
        print("Testing {} ({}/{})...".format(script, count, len(EC_SCRIPTS2)))
        test_r(script)
        # test_enclave(script)
        # test_noenclave(script)
        count += 1

if __name__ == "__main__":
    main()
