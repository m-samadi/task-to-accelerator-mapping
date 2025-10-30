#**************************************************************************
# main.py
#
# This simulator performs task-to-accelerator mapping in OpenMP
# applications.
#**************************************************************************
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#              http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#**************************************************************************
import gen
import func
import math
from method import baseline
from method import O_KGLP
from method import HPC_DAG
from method import new

# Global variables #
max_num_tasks = 1250 # Maximum number of tasks [random case]
num_tasks = 0 # Number of tasks [random case]
bench_name = 'axpy' # The name of the benchmark
ran_pro = 0.05 # Probability of selecting data dependencies between tasks [random case]
type_pro = 0.99 # The probability to specify the task type [random case]
itr_et = 10 # Number of iterations for execution time generation [random case]
et_min = 1 # Minimum execution time [random case]
et_max = 50 # Maximum execution time [random case]
et_type = 'max' # The type of execution time generation; min: Minimum, avg: Average, max: Maximum
dl_min_task = 1 # Minimum probability for determining the deadline of the task
dl_max_task = 5 # Maximum probability for determining the deadline of the task
itr_prg = 100 # Number of iterations for the program
num_cpu_threads = 64 # Number of CPU threads
gpu_task_num = [] # GPU-using task number (the index starts from 0)
num_gpu_devices = 8 # Number of GPU devices
loc_queue_cap = math.ceil(num_cpu_threads / num_gpu_devices) # Capacity of the local queues of GPU devices
graphic_result = 0 # Graphical output; 0: Not show, 1: Show

# Generate the graph #
graph_type = input("Generate the graph based on benchmark (press y) or random graph (press n)? ")

# Show the status of the mapping process #
print('The mapping is in progress...')

# Reset the files to write the results #
file = open("output/results.dat", "w")
file.close()

file = open("output/max_tasks.dat", "w")
file.close()

file = open("output/num_edge.dat", "w")
file.close()

for i in range(itr_prg):
	print('\nIteration ' + str(i + 1) + '\n====================')

	if graph_type == 'y':
		# Specify GPU-using task number(s)
		gpu_task_num = gen.read_gpu_task(bench_name, gpu_task_num)

		# Generate the graph based on the benchmark #
		num_tasks, task_list = gen.graph_predef(bench_name, gpu_task_num)
	else:
		# Generate the graph randomly #
		num_tasks, task_list, gpu_task_num = gen.graph_rand(max_num_tasks, type_pro, ran_pro, gpu_task_num)

	# Determine execution time of tasks, deadline of the system, and generate the list of tasks #
	task_list, deadline = gen.specify_et(graph_type, num_tasks, task_list, bench_name, et_min, et_max, et_type, itr_et, dl_min_task, dl_max_task, num_cpu_threads, gpu_task_num)

	# Export the specification of the graph to the JSON file #
	#func.export_json(num_tasks, task_list)

	# ++++++++++++++++++ Start the mapping with the algorithms ++++++++++++++++++++ #

	results = []

	# MTET-MET, Baseline #
	results.append(baseline.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'Baseline', graphic_result))

	# MTET-MET, O-KGLP #
	results.append(O_KGLP.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'O-KGLP', graphic_result))

	# MTET-MET, TET-BF-TET #
	results.append(HPC_DAG.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'TET', 'BF', 'TET', graphic_result))

	# MTET-MET, TET-WF-TET #
	results.append(HPC_DAG.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'TET', 'WF', 'TET', graphic_result))

	# MTET-MET, LET-MNJ-MNAOT #
	#results.append(new.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'LET', 'MNJ', 'MNAOT', graphic_result))

	# MTET-MET, LET-LTET-MNAOT #
	results.append(new.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'LET', 'LTET', 'MNAOT', graphic_result))

	# MTET-MET, LET-WSM-MNAOT #
	#results.append(new.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'LET', 'WSM', 'MNAOT', graphic_result))

	# MTET-MET, WSM-MNJ-MNAOT #
	#results.append(new.execute(num_tasks, num_cpu_threads, num_gpu_devices, loc_queue_cap, func.clear(num_tasks, task_list), deadline, 'MTET', 'MET', 'WSM', 'MNJ', 'MNAOT', graphic_result))

	# Write the results to the file #
	file = open("output/results.dat", "a")

	for j in range(0, 5):
		file.write(str(results[j][0]))
		#file.write(str(results[i][0]) + "\t")
		#file.write(str(results[i][1]))

		if j != 4:
			file.write("\t")

	if i != itr_prg - 1:
		file.write("\n")

file.close()
