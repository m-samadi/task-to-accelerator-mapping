 #**************************************************************************
 # gen.py
 #
 # Generate the graph based on a predefined structure or randomly,
 # as well as determine execution time of the tasks, the deadline of the
 # system, and response time of the tasks.
 #**************************************************************************
 # Copyright 2025 Instituto Superior de Engenharia do Porto
 #
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
import random

out_list = [] # Outgoing tasks

# Define the task class #
class task:
	def __init__(self, t_id, t_type, thr_id, dev_id, exe_time, cpu1_time, memcopy1_time, gpu_time, memcopy2_time, cpu2_time, dep, num_out, res_time, status, s_time_cpu, f_time_cpu, s_time_cpu1, f_time_cpu1, s_time_memcopy1, f_time_memcopy1, s_time_gpu, f_time_gpu, s_time_memcopy2, f_time_memcopy2, s_time_cpu2, f_time_cpu2, deadline):
		self.t_id = t_id # Task ID
		self.t_type = t_type # Task type; 0: CPU-only task, 1: GPU-using task
		self.thr_id = thr_id # Thread ID, which can be used only for GPU-using tasks
		self.dev_id = dev_id # Device ID, which can be used only for GPU-using tasks
		self.exe_time = exe_time # Execution time
		self.cpu1_time = cpu1_time # Execution time of the initial CPU segment
		self.memcopy1_time = memcopy1_time # Time to copy memory from host to device
		self.gpu_time = gpu_time # Execution time of the GPU segment
		self.memcopy2_time = memcopy2_time # Time to copy memory from device to host
		self.cpu2_time = cpu2_time # Execution time of the last CPU segment
		self.dep = dep # The tasks list corresponding to input data dependency
		self.num_out = num_out # The number of outgoing tasks
		self.deadline = deadline # Deadline of the task
		self.res_time = res_time # Response time of the task
		# Status #
		# [CPU-only task]
		# s_cpu: CPU-only task started, f_cpu: CPU-only task finished
		# [GPU-using task]
		# s_cpu1: Initial CPU segment started, f_cpu1: Initial CPU segment finished
		# s_memcopy1: Memory copy from host to device started, f_memcopy1: Memory copy from host to device finished
		# s_gpu: GPU segment started, f_gpu: GPU segment finished
		# s_memcopy2: Memory copy from device to host started, f_memcopy2: Memory copy from device to host finished
		# s_cpu2: Last CPU segment started, f_cpu2: Last CPU segment finished
		self.status = status
		self.s_time_cpu = s_time_cpu # Start time of the CPU-only task
		self.f_time_cpu = f_time_cpu # Finish time of the CPU-only task
		self.s_time_cpu1 = s_time_cpu1 # Start time of the initial CPU segment
		self.f_time_cpu1 = f_time_cpu1 # Finish time of the initial CPU segment
		self.s_time_memcopy1 = s_time_memcopy1 # Start time of the memory copy from host to device
		self.f_time_memcopy1 = f_time_memcopy1 # Finish time of the memory copy from host to device
		self.s_time_gpu = s_time_gpu # Start time of the GPU segment
		self.f_time_gpu = f_time_gpu # Finish time of the GPU segment
		self.s_time_memcopy2 = s_time_memcopy2 # Start time of the memory copy from device to host
		self.f_time_memcopy2 = f_time_memcopy2 # Finish time of the memory copy from device to host
		self.s_time_cpu2 = s_time_cpu2 # Start time of the last CPU segment
		self.f_time_cpu2 = f_time_cpu2 # Finish time of the last CPU segment

# Generate the graph based on a predefined structure #
def graph_predef(bench_name, gpu_task_num):
	global out_list

	num_tasks = 0
	task_list = []

	# Open the file and read the contents #
	file = open("benchmark/" + bench_name + "_tdg_modified.dot", "r")
	lines = file.readlines()
	file.close()

	# Fetch the number of tasks #
	for line in lines:
		line_arr = line.strip().split("->")

		for i in range(len(line_arr)):
			if int(line_arr[i]) > num_tasks:
				num_tasks = int(line_arr[i])

	num_tasks += 1

	# Initialize the list of tasks #
	for i in range(num_tasks):
		task_list.append(task(i, None, None, None, None, None, None, None, None, None, [], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None))

	# Determine task type of the tasks #
	for i in range(num_tasks):
		if i not in gpu_task_num:
			task_list[i].t_type = 0 # CPU-only task
		else:
			task_list[i].t_type = 1 # GPU-using task

	# Specify data dependencies between the tasks #
	for line in lines:
		line_arr = line.strip().split("->")

		if len(line_arr) == 2:
			task_list[int(line_arr[1])].dep.append(task_list[int(line_arr[0])])

	# Determine the number of all outgoing tasks of the tasks #
	for i in range(num_tasks):
		out_list = []
		num_out_task_predef(i, lines)

		task_list[i].num_out = len(out_list)

	return num_tasks, task_list

# Generate the graph randomly #
def graph_rand(max_num_tasks, type_pro, ran_pro, gpu_task_num):
	global out_list

	# Determine the number of tasks #
	num_GPU_tasks = round(max_num_tasks * type_pro / 10) # Number of GPU-using tasks
	num_CPU_tasks = round(max_num_tasks - (max_num_tasks * type_pro)) # Number of CPU-only tasks
	num_tasks = num_CPU_tasks + num_GPU_tasks # Number of tasks

	# Initialize the list of tasks #
	task_list = []
	for i in range(num_tasks):
		task_list.append(task(i, None, None, None, None, None, None, None, None, None, [], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None))

	# Specify the task type #
	gpu_task_num = []
	while (len(gpu_task_num) < num_GPU_tasks):
		task_id = random.randint(0, num_tasks - 1)

		if task_id not in gpu_task_num:
			gpu_task_num.append(task_id)

	for i in range(num_tasks):
		if i in gpu_task_num:
			task_list[i].t_type = 1
		else:
			task_list[i].t_type = 0

	# Specify data dependencies between the tasks #
	M = [ [ 0 for i in range(num_tasks) ] for j in range(num_tasks) ]

	for i in range(num_tasks):
		for j in range(num_tasks)[:i:]:
			if random.random() < ran_pro:
				M[i][j] = 1

	num_edge = 0 # Number of edges

	for j in range(num_tasks):
		dep_list = []
		for i in range(num_tasks):
			if (i != j) and (M[i][j] == 1):
				dep_list.append(i)
				num_edge += 1
		
		for k in range(len(dep_list)):
			task_list[j].dep.append(task_list[dep_list[k]])

	# Write the result to the file #
	file = open("output/num_edge.dat", "a")
	file.write(str(num_edge) + "\n")
	file.close()

	# Determine the number of all outgoing tasks of the tasks #
	task_arr = []
	proc_list = []
	for i in range(num_tasks):
		if len(task_list[i].dep) != 0:
			for j in range(len(task_list[i].dep)):
				task_arr.append([task_list[i].dep[j].t_id, task_list[i].t_id])
				proc_list.append(task_list[i].dep[j].t_id)
	for i in range(num_tasks):
		if i not in proc_list:
			task_arr.append([i])

	for i in range(num_tasks):
		out_list = []
		num_out_task_rand(i, task_arr)

		task_list[i].num_out = len(out_list)

	return num_tasks, task_list, gpu_task_num

# Specify the number of outgoing tasks of a certain task based on the predefined structure #
def num_out_task_predef(task_id, lines):
	global out_list

	for line in lines:
		line_arr = line.strip().split("->")

		if len(line_arr) == 2:
			if int(line_arr[0].strip()) == task_id:
				if int(line_arr[1].strip()) not in out_list:
					out_list.append(int(line_arr[1].strip()))
					#print(int(line_arr[1].strip()))

					num_out_task_predef(int(line_arr[1].strip()), lines)

# Specify the number of outgoing tasks of a certain task based on the random structure #
def num_out_task_rand(task_id, task_arr):
	global out_list

	for i in range(len(task_arr)):
		if len(task_arr[i]) == 2:
			if task_arr[i][0] == task_id:
				if task_arr[i][1] not in out_list:
					out_list.append(task_arr[i][1])

					num_out_task_rand(task_arr[i][1], task_arr)

# Read GPU-using task number(s) from file
def read_gpu_task(bench_name, gpu_task_num):
	# Read the file as lines #
	with open("benchmark/" + bench_name + "_gpu_task.dat") as f:
		lines = f.readlines() # Content of the file
		f.close() # Close the file

	# Traverse the file to find tasks numbers #
	for i in range(len(lines)):
		# Check whether the line includes a range (-) #
		if (lines[i].find('-') != -1):
			sp_line = lines[i].split('-') # Split the line
			min_range = int(sp_line[0])
			max_range = int(sp_line[1])

			for i in range (min_range, max_range + 1):
				gpu_task_num.append(i)
		else:
			gpu_task_num.append(int(lines[i].replace("\n", "")))

	return gpu_task_num

# Specify execution time of the tasks, as well as calculate the deadline of the system #
# and response time of the tasks #
def specify_et(graph_type, num_tasks, task_list, bench_name, et_min, et_max, et_type, itr_et, dl_min_task, dl_max_task, dl_min_graph, dl_max_graph, gpu_task_num):
	if graph_type == 'y':
		# Determine an execution time for each task based on the json file #
		tdg_st_line_num = [] # The starting line number of each task

		# Read the json file as lines #
		with open("benchmark/" + bench_name + "_json.json") as f:
			lines_json = f.readlines() # Content of the file
			f.close() # Close the file

		# Traverse the file to find the starting line number of each task #
		for i in range(num_tasks):
			for j in range(len(lines_json)):
				# Check whether the task number (i) is found in the current line #
				if (lines_json[j].find('"' + str(i) + '":') != -1):
					tdg_st_line_num.append(j) # Set the starting line number

		# Determine execution time for each task #
		for i in range(num_tasks):
			exe_list = [] # The list of execution times
			st_line_num = tdg_st_line_num[i] # The starting line number of the task

			# Specify the finishing line number of the task #
			if i != num_tasks - 1:
				fn_line_num = tdg_st_line_num[i + 1] - 1
			else:
				fn_line_num = len(lines_json) - 1

			# Find execution total times in the json and add it to the list #
			for j in range (st_line_num, fn_line_num):
				# Check whether execution total time exists in the current line #
				if (lines_json[j].find('execution_total_time') != -1):
					sp_line = lines_json[j].split(':') # Split the line
					et = int(sp_line[1].strip()) # Fetch the execution total time from the line
					exe_list.append(et) # Add the execution time to the list

			# Determine the execution time based on the minimum value #
			if et_type == 'min':
				task_list[i].exe_time = min(exe_list)
			# Determine the execution time based on the average value #
			elif et_type == 'avg':
				task_list[i].exe_time = round(sum(exe_list) / len(exe_list))
			# Determine the execution time based on the maximum value #
			elif et_type == 'max':
				task_list[i].exe_time = max(exe_list)

		# Determine detailed times for GPU-using tasks #
		with open("benchmark/" + bench_name + "_gpu_trace.csv") as f:
			lines_csv = f.readlines() # Content of the file
			f.close() # Close the file

		mem_copy = []
		for i in range (len(lines_csv)):
			if (lines_csv[i].find('memcopy:start') != -1) or (lines_csv[i].find('memcopy:terminate') != -1):
				sp_line = lines_csv[i].split(', memcopy') # Split the line
				mem_copy.append(int(sp_line[0]))

		mem_copy_diff = []
		for j in range (0, len(mem_copy), 2):
			mem_copy_diff.append(mem_copy[j + 1] - mem_copy[j])

		if et_type == 'min': # The minimum value #
			mem_copy_time = min(mem_copy_diff)
		elif et_type == 'avg': # The average value #
			mem_copy_time = round(sum(mem_copy_diff) / len(mem_copy_diff))
		elif et_type == 'max': # The maximum value #
			mem_copy_time = max(mem_copy_diff)

		for k in range(num_tasks):
			if task_list[k].t_type == 1:
				task_list[k].memcopy1_time = mem_copy_time
				task_list[k].memcopy2_time = mem_copy_time

		# Determine the execution time for GPU-using tasks #
		kernel = []
		for i in range (len(lines_csv)):
			if (lines_csv[i].find('kernel') != -1):
				sp_line = lines_csv[i].split(', kernel') # Split the line
				kernel.append(int(sp_line[0]))

		kernel_diff = []
		for j in range (0, len(kernel), 2):
			kernel_diff.append(kernel[j + 1] - kernel[j])

		for i in range(len(gpu_task_num)):
			for j in range(num_tasks):
				if (gpu_task_num[i] == j):
					task_list[j].gpu_time = kernel_diff[i]

		# Determine execution time of the CPU segments for GPU-using tasks #
		for i in range(num_tasks):
			if task_list[i].t_type == 1:
				task_list[i].cpu1_time = round(abs(task_list[i].exe_time - (task_list[i].memcopy1_time + task_list[i].gpu_time + task_list[i].memcopy2_time)) / 2)
				task_list[i].cpu2_time = task_list[i].cpu1_time
	else:
		# Specify execution times for each task based on the random procedure #
		for i in range(num_tasks):		
			# CPU-only task
			if task_list[i].t_type == 0:
				# Generate the random values #
				ran_list = []
				for j in range(itr_et):
					ran_list.append(round(random.random() * (et_max - et_min)))

				# Determine the execution time based on the minimum value #
				if et_type == 'min':
					task_list[i].exe_time = min(ran_list)
				# Determine the execution time based on the average value #
				elif et_type == 'avg':
					task_list[i].exe_time = round(sum(ran_list) / len(ran_list))
				# Determine the execution time based on the maximum value #
				elif et_type == 'max':
					task_list[i].exe_time = max(ran_list)
			# GPU-using task
			else:
				# Generate the random values #
				ran_list = []
				for j in range(itr_et):
					ran_list.append(round(random.random() * (et_max - et_min) * 10))

				# Determine the execution time based on the minimum value #
				if et_type == 'min':
					task_list[i].exe_time = min(ran_list)
				# Determine the execution time based on the average value #
				elif et_type == 'avg':
					task_list[i].exe_time = round(sum(ran_list) / len(ran_list))
				# Determine the execution time based on the maximum value #
				elif et_type == 'max':
					task_list[i].exe_time = max(ran_list)
				
				# Specify the memory copy times #
				task_list[i].memcopy1_time = round(task_list[i].exe_time * 0.05, 2)
				task_list[i].memcopy2_time = round(task_list[i].exe_time * 0.05, 2)

				# Specify the execution time of the GPU segment #
				task_list[i].gpu_time = round(task_list[i].exe_time * 0.85, 2)

				# Specify the execution time of the CPU segments #
				task_list[i].cpu1_time = round(abs(task_list[i].exe_time - (task_list[i].memcopy1_time + task_list[i].gpu_time + task_list[i].memcopy2_time)) / 2, 2)
				task_list[i].cpu2_time = task_list[i].cpu1_time

	# Specify the deadline of the task #
	for i in range(num_tasks):
		# CPU-only task
		if task_list[i].t_type == 0:
			task_list[i].deadline = random.randint(dl_min_task, dl_max_task)
		# GPU-using task
		else:
			task_list[i].deadline = random.randint(dl_min_task, dl_max_task) * 10

	# Determine the deadline of the system #
	sum_et = 0
	for i in range(num_tasks):
		sum_et += task_list[i].exe_time
	deadline = random.randint(dl_min_graph, dl_max_graph) * sum_et

	# Calculate response time of the tasks #
	for i in range(num_tasks):
		task_list[i].res_time = round(deadline * task_list[i].exe_time / sum_et)

	return task_list, deadline
