#!/usr/bin/env python3
import random
import csv
import os
import subprocess
import collections

#METADATA_FILE = "temp/sample.metadata"

FRONTEND_DIR = "../../dove-frontend-r/src/"
BACKEND_DIR = os.getcwd()
# Relative to above directory
#DATA_CSV = "data.csv"
#HEADER_FILE = "unmod-scripts/init_data.R"

#DATASET_NAME = "snp.mat"
# Must be the same as HEADER_FILE and METADATA_FILE
#DATA_NROW = 2808570
#DATA_NCOL = 60

EC_SCRIPTS = [
    "allele_sharing",
    "EHHS",
    "hwe_chisq",
    "hwe_fisher",
    "iES",
    "neiFis_multispop",
    "neiFis_onepop",
    "snp_stats",
    "wcFstats",
    "wcFst_spop_pairs"
]

EC_SUBPOP = [
    "neiFis_multispop",
    "wcFstats",
    "wcFst_spop_pairs",
]

ORIG_LOC = BACKEND_DIR+"/../../../evachan.org-Rscripts/rscripts/"

RUNSTRING_R_SUBPOP = '\nto.read <- file("'+BACKEND_DIR+'/../examples/sample.data", "rb")\nloaded <- readBin(to.read, double(), n=100, endian="little")\ngeno <- matrix(loaded, nrow=10, ncol=10, byrow=TRUE)\nsubpop <- rep(LETTERS[1:3],c(3,3,4))\nsource("{}calc_{}.R")\nz<-calc_{}(geno, subpop)\n\n'

RUNSTRING_R_CLEAN = '\nto.read <- file("'+BACKEND_DIR+'/../examples/sample.data", "rb")\nloaded <- readBin(to.read, double(), n=100, endian="little")\ngeno <- matrix(loaded, nrow=10, ncol=10, byrow=TRUE)\nsource("{}calc_{}.R")\nz <- calc_{}(geno)\n\n'

RUNSTRING_R_IES = '\nto.read <- file("'+BACKEND_DIR+'/../examples/sample.data", "rb")\nloaded <- readBin(to.read, double(), n=100, endian="little")\ngeno <- matrix(loaded, nrow=10, ncol=10, byrow=TRUE)\nsource("{}calc_EHHS.R")\nEHHS<-calc_EHHS(geno)\nlox<-matrix(1:nrow(EHHS),nrow=nrow(EHHS))\nsource("{}calc_{}.R")\nz <- calc_{}(EHHS, lox)\n\n'

#RUNSTRING_FEND = 'source("ec-scripts/secret_{}.R")\n'

def run_r(filename, script):
    script_path = "../examples/ec-original/calc_"+script+".R"
    ps = subprocess.run(["/usr/bin/time", "-v", "R", "-f", filename, "--args", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    # ps = subprocess.run(["R", "-f", filename], stdout=subprocess.DEVNULL, check=True)
    return ps

def run_native_r(filename):
    ps = subprocess.run(["/usr/bin/time", "-v", "R", "-f", filename], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    return ps

def run_enclave():
    ps = subprocess.run(["/usr/bin/time", "-v", "./app"], stderr=subprocess.PIPE, check=True)
    return ps

def run_noenclave():
    ps = subprocess.run(["/usr/bin/time", "-v", "./splitapp"], stderr=subprocess.PIPE, check=True)
    return ps

def test_r(script):
    r_results = []
    os.chdir(FRONTEND_DIR)

    with open("/tmp/dove_perf_analysis_base.R", "w") as scr:
        if script in EC_SUBPOP:
            scr.write(RUNSTRING_R_SUBPOP.format(ORIG_LOC,script, script))
        elif script == "iES":
        	scr.write(RUNSTRING_R_IES.format(ORIG_LOC,ORIG_LOC,script, script))
        else:
            scr.write(RUNSTRING_R_CLEAN.format(ORIG_LOC,script, script))

    print("  [R] Running base R...")
    for i in range(0,1):
        r_results.append((run_native_r("/tmp/dove_perf_analysis_base.R").stderr).decode('utf8'))
    os.chdir("../../dove-backend/src/")

    with open('../../benchmarks/dynamic/R_' + script + '.txt', 'w') as outf:
        outf.writelines(r_results)

    return r_results

def test_enclave(script):
    results = {}
    results["frontend"] = []
    results["backend"] = []
    os.chdir(FRONTEND_DIR)

    print("  [Enclave] Running front-end...")
    for i in range(0,1):
        pth = os.path.abspath(os.getcwd())+'/dove_automate.R'
        results["frontend"].append((run_r(pth, script).stderr).decode('utf8'))
    os.chdir(BACKEND_DIR)

    with open('../../benchmarks/dynamic/fend_' + script + '.txt', 'w') as outf:
        outf.writelines(results["frontend"])

    print("  [Enclave] Running back-end...")
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

    print("  [Enclave] Running front-end...")
    for i in range(0,1):
        pth = os.path.abspath(os.getcwd())+'/dove_automate.R'
        results["frontend"].append((run_r(pth, script).stderr).decode('utf8'))
    os.chdir(BACKEND_DIR)

    with open('../../benchmarks/dynamic/fend_' + script + '.txt', 'w') as outf:
        outf.writelines(results["frontend"])

    print("  [Enclave] Running back-end...")
    for i in range(0,1):
        results["backend"].append(run_noenclave().stderr.decode('utf8'))

    with open('../../benchmarks/dynamic/bend_noe_' + script + '.txt', 'w') as outf:
        outf.writelines(results["backend"])

    return results

def main():
    # subprocess.run(["make", "clean"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # subprocess.run(["make", "all"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r_results = collections.OrderedDict()
    dove_results = collections.OrderedDict()

    print("TESTS")
    count = 1
    for script in EC_SCRIPTS:
        print("Testing {} ({}/{})...".format(script, count, len(EC_SCRIPTS)))
        #test_enclave(script)
        #test_noenclave(script)
        test_r(script)
        count += 1

if __name__ == "__main__":
    main()
