benchmarks 🕊
================================================

Introduction
--------------------
This repository provides scripts to run benchmarks that we used for evaluating DOVE, as well our benchmark results. You can read more about this in our academic research paper, [DOVE: A Data-Oblivious Virtual Environment](https://www.ndss-symposium.org/ndss-paper/dove-a-data-oblivious-virtual-environment/), which appeared in NDSS 2021.

This is **research code**, and has not been certified for production use. That being said, if you see something, [say something](https://github.com/dove-project/benchmarks/issues)!

Running the benchmarks
--------------------------------
### Prerequisites
Our benchmark scripts assume that you have ``python3`` installed on your system.

Furthermore, our scripts run a frontend located at ``../dove-frontend-r/src`` with benchmark scripts located at ``../dove-frontend-r/examples`` and run a backend located at either ``../dove-backend/src/splitapp`` (for non-SGX backend) or ``../dove-backend/src/app`` (for SGX backend). When running benchmarks for native R, we assume that you cloned the [original genomic evaluation programs](https://github.com/ekfchan/evachan.org-Rscripts) to ``../../evachan.org-Rscripts``.

### Instructions
For scripts with a prefix ``perf_``, you first need to comment/uncomment the function calls with prefix ``test_`` in order to choose whether you want to run benchmarks on (1) native R (``test_r()``, (2) backend without SGX (``test_noenclave()``), or (3) backend with SGX (``test_enclave()``).

To run the script, run following commands:
```sh
cd ../dove-backend/src
python3 ../../benchmarks/src/NAME_OF_SCRIPT
```
You may need superuser privileges (`sudo`) in some cases.

Script Information
---------------------------------
- ``exec_trace.py``: This script measures the backend's execution trace using branch trace store. This script runs only on the non-SGX version of the backend, compiled with debug flags.
    - ``load.gdb``: The GDB command file used by the above script to actually run branch trace store on the backend's data loading.
    - ``trace.gdb``: The GDB command file used by the above script to actually run branch trace store on the backend's leaf functions.
- ``get_opcodes.py``: This script uses `objdump` to load the instructions used in the backend's object files, and then compare them against instructions found in [`libfixedtimefixedpoint`](https://github.com/kmowery/libfixedtimefixedpoint). This script runs only on the non-SGX version of the backend, compiled with debug flags.
- ``perf_analysis_ec-original.py``: This script runs performance benchmarks for 10 evaluation programs that are located at ``../dove-frontend-r/examples/ec-original/``.
- ``perf_analysis_secret_LD.py``: This script runs performance benchmarks for one evaluation program named ``secret_LD.py`` that is located at ``../dove-frontend-r/examples/ec-modified/``.
- ``perf_analysis_pagerank.py``: This script runs performance benchmarks for PageRank algorithm implemented at ``../dove-frontend-r/examples/pagerank/``.

