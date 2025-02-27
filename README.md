# Task-to-accelerator mapping
This simulator performs the task-to-accelerator mapping of OpenMP-based applications using heuristics and multi-criteria decision analysis.
<br/>
<br/>
## Specification
The graphs can be generated in the simulator randomly or based on the benchmarks. The task execution time can be calculated using the minimum, average, or maximum function. The deadline of the system is determined using the volume of graph and a random number. For each method, the response time, missed deadline, and static scheduling of tasks in the accelerator are specified using the simulation process. In addition, graphical results can be generated to show the mapping of tasks in GPU devices. After mapping the graph using each algorithm, the response time and the missed deadline achieved from the methods are exported to a file.
<br/>
<br/>
If the simulator is used to schedule randomly generated graphs, the loop tick (e.g., time interval) in the code of each mapping method is set to 1 (i.e., t += 1) by default. However, if it is applied to schedule the graphs generated using benchmarks and task execution times are high, the loop tick may be set to 1000000 (i.e., t += 1000000).
<br/>
<br/>
## Simulation parameters
The simulation parameters are set by default. However, they can be modified at the beginning of the main.py located at the root.
<br/>
<br/>
## Graphical output
Graphical outputs can be also generated at the end of the simulation process by setting the variable 'graphic_result' to 1. Note that Python Image Library (PIL) should be installed using the command below for this purpose:
```
pip install pillow
```
Since there is a limitation in drawing the shapes in Python, if the number of tasks is high, keep this option disabled in the simulator.
<br/>
<br/>
## Benchmark
Three benchmarks are provided in the simulator (placed in the benchmark folder), including a DOT file (that includes the task ID and data dependencies of the tasks) and a JSON file (that includes the execution times for each task). Two JSON files are provided for each benchmark, where the task execution times are measured based on the cases running with 4 and 8 threads. To use them in the simulator, simply rename one of the files to bench_json, where bench denotes the name of the benchmark, before starting the simulation. Note that the execution times are measured using the Extrae [1] and Papi [2] tools, as well as the JSON files are created with a script [3] and the Paraver toolset [4].
<br/>
<br/>
It is worth mentioning that any new benchmarks can be simply appended to this set and used in the simulator by following the structure of the existing DOT and JSON files.
<br/>
<br/>
## Execution
The simulation process can be run with the following command:
```
python main.py
```
If the graph is generated using the benchmark, press 'y'; otherwise press 'n'.
<br/>
<br/>
## References
[1] Barcelona Supercomputing Center (BSC), "Extrae," December 2023. https://tools.bsc.es/extrae/
<br/>
[2] Innovative Computing Laboratory, University of Tennessee, "Performance Application Programming Interface, PAPI," April 2023. https://icl.utk.edu/papi/index.html/
<br/>
[3] Barcelona Supercomputing Center (BSC), "TDG instrumentation," December 2023. https://gitlab.bsc.es/ampere-sw/wp2/tdg-instrumentation-script/
<br/>
[4]	A. Munera, S. Royuela, G. Llort, E. Mercadal, F. Wartel, and E. Quiñones, "Experiences on the characterization of parallel applications in embedded systems with extrae/paraver," in Proc. of the 49th Int. Conference on Parallel Processing (ICPP '20), Edmonton, AB, Canada, pp. 1–11, August 17–20, 2020.
