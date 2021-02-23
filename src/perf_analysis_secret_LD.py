#!/usr/bin/env python3
import random
import csv
import os
import subprocess
import collections

FRONTEND_DIR = "../../dove-frontend-r/src"

EC_SCRIPTS2 = [
    "LD",
]

ORIG_LOC = FRONTEND_DIR+"/../../../evachan.org-Rscripts/rscripts/"

EC_RUNSTRINGS2_R = {
    "LD": "LDrsq.allpops.SNPs1to1k <- calc_LD(snp.mat, get.D=T, get.Dprime=T, get.rsq=T, get.chisq=T, get.chisq_prime=T)"
}

RUNSTRING_R = '\nto.read <- file("'+FRONTEND_DIR+'/../../dove-backend/examples/sample.data", "rb")\nsnp.mat <- readBin(to.read, double(), n=10*10, endian="little")\ndim(snp.mat) <- c(10, 10)\nsource("{}calc_{}.R")\nclose(to.read)\n{}\n\n'

def run_r(filename):
    os.chdir(FRONTEND_DIR)
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
    os.chdir("../../dove-backend/src/")

    with open('../../benchmarks/dynamic/R_' + script + '.txt', 'w') as outf:
        outf.writelines(results)

    return results

def test_enclave(script):
    results = {}
    results["frontend"] = []
    results["backend"] = []
    
    os.chdir(FRONTEND_DIR)
    print("  Running front-end...")
    for i in range(0,1):
        results["frontend"].append((run_r("../examples/ec-modified/secret_LD.R").stderr).decode('utf8'))
    os.chdir("../../dove-backend/src")

    with open('results/fend_' + script + '.txt', 'w') as outf:
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
    print("  Running front-end...")
    for i in range(0,1):
        results["frontend"].append((run_r("../examples/ec-modified/secret_LD.R").stderr).decode('utf8'))
    os.chdir("../../dove-backend/src")

    print("  Running back-end...")
    for i in range(0,1):
        results["backend"].append(run_noenclave().stderr.decode('utf8'))

    with open('../../benchmarks/dynamic/bend_noe_' + script + '.txt', 'w') as outf:
        outf.writelines(results["backend"])

    return results

def test_backend():
    pass

def main():
    # subprocess.run(["make", "clean"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # subprocess.run(["make", "all"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("TESTS")
    count = 1
    for script in EC_SCRIPTS2:
        print("Testing {} ({}/{})...".format(script, count, len(EC_SCRIPTS2)))
        #test_r(script)
        #test_enclave(script)
        test_noenclave(script)
        count += 1

if __name__ == "__main__":
    main()
