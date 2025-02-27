 #**************************************************************************
 # O_KGLP.py
 #
 # Map the tasks of the graph using the enhanced O-KGLP method pressented in
 # the following paper:
 # "An optimal k-exclusion real-time locking protocol motivated by
 # multi-GPU systems"
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
from operator import itemgetter
import func

# Global variables #
task_stack = [] # The task stack [CPU]
alloc_queue = [] # Allocation queues of the threads [CPU]
exec_queue = [] # Execution queues of the threads [CPU]
wait_queue = [] # Waiting queues of the threads (FIFO queue) [CPU]
curr_thr = -1 # The current thread [CPU]
last_idle = [] # Last idle time of the threads (-1 for a busy thread) [CPU]
prio_queue = [] # Priority queue of the devices [GPU]
FIFO_queue = [] # FIFO queues of the devices [GPU]
ker_exec_queue = [] # Kernel execution queues of the devices [GPU]
task_device = [] # Allocation of devices to tasks [GPU]
comp_tasks_cnt = 0 # The number of completed tasks

alpha = 0.5
beta = 0
gamma = 0.5

theta = 0.4
psi = 0.6

# Select an allocation queue using one of the CPU allocation algorithms #
def cpu_alloc_algorithm(num_cpu_threads, cpu_alloc_alg, t):
	global alloc_queue, curr_thr, last_idle, alpha, beta, gamma

	thr_list = [] # The thread information

	# The MNTP algorithm #
	if cpu_alloc_alg == 'MNTP':
		# Determine the number of tasks existing in the queues #
		for i in range(num_cpu_threads):
			thr_list.append([i, len(alloc_queue[i])])

		# Sort the list based on the minimum number of tasks #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = False)

		return thr_list[0][0]

	# The NT algorithm #
	elif cpu_alloc_alg == 'NT':
		# Select the next thread #
		if curr_thr < num_cpu_threads - 1:
			curr_thr += 1
		else:
			curr_thr = 0

		return curr_thr

	# The MRIT algorithm #
	elif cpu_alloc_alg == 'MRIT':
		# Calculate the recent idle time of the threads #
		for i in range(num_cpu_threads):
			if last_idle[i] != -1:
				thr_list.append([i, t - last_idle[i]])
			else:
				thr_list.append([i, 0])

		# Sort the list based on the most recent idle time #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = True)

		return thr_list[0][0]

	# The MTET algorithm #
	elif cpu_alloc_alg == 'MTET':
		# Calculate the total execution time of the queues #
		for i in range(num_cpu_threads):
			total_et = 0
			for j in range(len(alloc_queue[i])):
				total_et += alloc_queue[i][j].exe_time

			thr_list.append([i, total_et])

		# Sort the list based on the minimum total execution time #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = False)

		return thr_list[0][0]

	# The MTRT algorithm #
	elif cpu_alloc_alg == 'MTRT':
		# Calculate the total response time of the queues #
		for i in range(num_cpu_threads):
			total_rt = 0
			for j in range(len(alloc_queue[i])):
				total_rt += alloc_queue[i][j].res_time

			thr_list.append([i, total_rt])

		# Sort the list based on the maximum total response time #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = True)

		return thr_list[0][0]

	# The TMCD algorithm #
	elif cpu_alloc_alg == 'TMCD':
		# Calculate the recent idle time of the threads #
		rec_idle_time = []
		for i in range(num_cpu_threads):
			if last_idle[i] != -1:
				rec_idle_time.append(t - last_idle[i])
			else:
				rec_idle_time.append(0)

		# Calculate total number of tasks, total idle time, and total execution time #
		total_num_tasks = 0
		total_it = 0
		total_et = 0

		for i in range(num_cpu_threads):
			total_it += rec_idle_time[i]
			for j in range(len(alloc_queue[i])):
				total_num_tasks += 1
				total_et += alloc_queue[i][j].exe_time

		if total_num_tasks == 0:
			total_num_tasks = 1
		if total_it == 0:
			total_it = 1
		if total_et == 0:
			total_et = 1

		# Calculate the cost of the queues #
		for i in range(num_cpu_threads):
			if rec_idle_time[i] != 0:
				val_it = 1 / (rec_idle_time[i] / total_it)
			else:
				val_it = 0

			sum_et = 0
			for j in range(len(alloc_queue[i])):
				sum_et += alloc_queue[i][j].exe_time

			thr_list.append([i, alpha * len(alloc_queue[i]) / total_num_tasks + beta * val_it + gamma * sum_et / total_et])

		# Sort the list based on the least cost #
		thr_list = sorted(thr_list, key = itemgetter(1), reverse = False)

		return thr_list[0][0]

# Choose a task from the allocation queue using one of the CPU dispatching algorithms #
def cpu_disp_algorithm(sel_tasks, cpu_disp_alg):
	global theta, psi

	# The MET algorithm #
	if cpu_disp_alg == 'MET':
		sel_id = 0
		# Find the task with the minimum execution time #
		for i in range(len(sel_tasks))[1::]:
			if sel_tasks[i].exe_time < sel_tasks[sel_id].exe_time:
				sel_id = i

	# The MRT algorithm #
	elif cpu_disp_alg == 'MRT':
		sel_id = 0
		# Find the task with the maximum response time #
		for i in range(len(sel_tasks))[1::]:
			if sel_tasks[i].res_time > sel_tasks[sel_id].res_time:
				sel_id = i

	# The MCD algorithm #
	elif cpu_disp_alg == 'MCD':
		# Calculate total execution time and total response time of the tasks #
		total_et = 0
		total_rt = 0
		for i in range(len(sel_tasks)):
			total_et += sel_tasks[i].exe_time
			total_rt += sel_tasks[i].res_time

		if total_et == 0:
			total_et = 1
		if total_rt == 0:
			total_rt = 1

		# Calculate the cost of each task #
		cost = []
		for i in range(len(sel_tasks)):
			cost.append(theta * sel_tasks[i].exe_time / total_et + psi * 1 / (sel_tasks[i].res_time / total_rt))

		# Select the task with the least cost #
		sel_id = 0
		for i in range(len(sel_tasks))[1::]:
			if cost[i] < cost[sel_id]:
				sel_id = i

	return sel_id

# Calculate the total number of tasks in FIFO queues #
def tot_num_FIFO(num_gpu_devices):
	global FIFO_queue

	tot = 0
	for i in range(num_gpu_devices):
		tot += len(FIFO_queue[i])

	return tot

# Choose the FIFO queue with fewer tasks #
def short_FIFO(num_gpu_devices):
	global FIFO_queue

	queue_id = 0
	for i in range(num_gpu_devices)[1::]:
		if len(FIFO_queue[i]) < len(FIFO_queue[queue_id]):
			queue_id = i

	return queue_id

# Select a task from the priority queue #
def gpu_prio_queue_sel():
	global prio_queue

	# Find the job with the earliest deadline #
	sel_id = 0
	for i in range(len(prio_queue))[1::]:
		if prio_queue[i].deadline < prio_queue[sel_id].deadline:
			sel_id = i
	
	return sel_id

# The mapping process #
def mapping(num_tasks, num_cpu_threads, num_gpu_devices, FIFO_queue_cap, task_list, cpu_alloc_alg, cpu_disp_alg):
	global task_stack, alloc_queue, exec_queue, wait_queue, curr_thr, last_idle, prio_queue, FIFO_queue, ker_exec_queue, task_device, comp_tasks_cnt

	t = 0 # Response time

	# Continue the mapping process while the allocation queues of the threads are not empty, as well as #
	# the execution queues of the threads include executing tasks #
	while comp_tasks_cnt < num_tasks:
		# CPU execution #
		for thr_num in range(num_cpu_threads):
			# Check the execution queue of the thread #
			if bool(exec_queue[thr_num]):
				task = exec_queue[thr_num][len(exec_queue[thr_num]) - 1]

				# CPU-only task #
				# Check whether the execution of the CPU-only task has been finished #
				if task.status == 's_cpu' and task.f_time_cpu <= t:
					task.status = 'f_cpu'

					curr_thr = thr_num
					last_idle[thr_num] = t
					comp_tasks_cnt += 1

				# GPU-using task #
				# Check whether the execution of the initial CPU segment has been finished #
				elif task.status == 's_cpu1' and task.f_time_cpu1 <= t:
					task.status = 'f_cpu1'
					
					curr_thr = thr_num
					last_idle[thr_num] = t

					# Enqueue the task into the shortest FIFO queue #
					flag = 0
					if (len(prio_queue) + tot_num_FIFO(num_gpu_devices)) < num_cpu_threads:
						queue_id = short_FIFO(num_gpu_devices)

						if len(FIFO_queue[queue_id]) < FIFO_queue_cap:
							FIFO_queue[queue_id].append(task)
							flag = 1

							task_device.append([task.t_id, queue_id])

					# Enqueue the task into the priority queue #
					if flag == 0:
						prio_queue.append(task)

				# Check whether the execution of the last CPU segment has been finished #
				elif task.status == 's_cpu2' and task.f_time_cpu2 <= t:
					task.status = 'f_cpu2'

					curr_thr = thr_num
					last_idle[thr_num] = t
					comp_tasks_cnt += 1

			# Check the task stack and add ready tasks to the allocation queues #
			# This process is done just by the master thread #
			if thr_num == 0:
				remove_list = []
				for i in range(len(task_stack)):
					# Add the ready tasks to the allocation queues if there are not any data dependencies, or #
					# there are any data dependencies but the related tasks are finished #
					if task_stack[i].dep == None or func.check_dep(task_list, task_stack[i].dep) == True:
						# Select an allocation queue from the list of queues #
						thread_id = -1
						for j in range(num_cpu_threads): # Select empty queue belonging to an idle thread
							if len(alloc_queue[j]) == 0 and last_idle[j] != -1:
								thread_id = j
								break

						if thread_id == -1: # Select the queue using the allocation heuristic
							thread_id = cpu_alloc_algorithm(num_cpu_threads, cpu_alloc_alg, t)

						# Append the task to the selected queue #
						alloc_queue[thread_id].append(task_stack[i])

						remove_list.append(task_stack[i])

						# Set the thread ID of the task #
						task_stack[i].thr_id = thread_id

				# Remove the tasks, which were processed, from the task stack #
				for j in range(len(remove_list)):
					task_stack.remove(remove_list[j])

			# Check whether the thread is idle #
			if not bool(exec_queue[thr_num]) or last_idle[thr_num] != -1:
				# Check the waiting queue of the thread and dispatch one of the tasks (if any) to it #
				if bool(wait_queue[thr_num]):
					# Choose the first task (i.e., FIFO) from the waiting queue #
					sel_task = wait_queue[thr_num][0]

					# Dispatch the task to the thread #
					exec_queue[thr_num].append(sel_task)
					task = exec_queue[thr_num][len(exec_queue[thr_num]) - 1]

					task.status = 's_cpu2'
					task.s_time_cpu2 = t
					task.f_time_cpu2 = t + task.cpu2_time

					last_idle[thr_num] = -1

					# Remove the task from the waiting queue #
					wait_queue[thr_num].remove(sel_task)

				# Check the allocation queue of the thread and dispatch one of the tasks (if any) to it #
				elif bool(alloc_queue[thr_num]):
					# Choose one of the tasks from the allocation queue #
					sel_task = alloc_queue[thr_num][cpu_disp_algorithm(alloc_queue[thr_num], cpu_disp_alg)]

					# Dispatch the task to the thread #
					exec_queue[thr_num].append(sel_task)
					task = exec_queue[thr_num][len(exec_queue[thr_num]) - 1]

					if task.t_type == 0: # CPU-only task
						task.status = 's_cpu'
						task.s_time_cpu = t
						task.f_time_cpu = t + task.exe_time
					else: # GPU-using task
						task.status = 's_cpu1'
						task.s_time_cpu1 = t
						task.f_time_cpu1 = t + task.cpu1_time

					last_idle[thr_num] = -1

					# Remove the task from the allocation queue #
					alloc_queue[thr_num].remove(sel_task)

		# GPU execution #
		for dev_num in range(num_gpu_devices):
			# Check the kernel execution queue of the device #
			if bool(ker_exec_queue[dev_num]):
				task = ker_exec_queue[dev_num][len(ker_exec_queue[dev_num]) - 1]

				# Check whether the execution of the task has been finished #
				if task.status == 's_memcopy1' and task.f_time_memcopy1 <= t:
					task.status = 's_gpu'
					task.s_time_gpu = t
					task.f_time_gpu = t + task.gpu_time
				elif task.status == 's_gpu' and task.f_time_gpu <= t:
					task.status = 's_memcopy2'
					task.s_time_memcopy2 = t
					task.f_time_memcopy2 = t + task.memcopy2_time	
				elif task.status == 's_memcopy2' and task.f_time_memcopy2 <= t:
					task.status = 'f_memcopy2'

					wait_queue[task.thr_id].append(task) # Allocate the task to the waiting queue of the thread	

			# Check whether the device is idle #
			if not bool(ker_exec_queue[dev_num]) or ker_exec_queue[dev_num][len(ker_exec_queue[dev_num]) - 1].status == 'f_memcopy2' or ker_exec_queue[dev_num][len(ker_exec_queue[dev_num]) - 1].status == 's_cpu2' or ker_exec_queue[dev_num][len(ker_exec_queue[dev_num]) - 1].status == 'f_cpu2':
				# Check the FIFO queue of the device and dispatch one of the tasks (if any) to it #
				if bool(FIFO_queue[dev_num]):
					# Select the first task from the FIFO queue #
					sel_task = FIFO_queue[dev_num][0]

					# Remove the task from the FIFO queue #
					FIFO_queue[dev_num].remove(sel_task)

					# Dispatch the task to the device #
					ker_exec_queue[dev_num].append(sel_task)
					task = ker_exec_queue[dev_num][len(ker_exec_queue[dev_num]) - 1]

					task.status = 's_memcopy1'
					task.s_time_memcopy1 = t
					task.f_time_memcopy1 = t + task.memcopy1_time

					# Dequeue a task from the priority queue and enqueue it into the FIFO queue #
					if (len(FIFO_queue[dev_num]) < FIFO_queue_cap) and (len(prio_queue) > 0):
						task = prio_queue[gpu_prio_queue_sel()]

						prio_queue.remove(task)
						FIFO_queue[dev_num].append(task)

						task_device.append([task.t_id, dev_num])
			'''
			# Dequeue a task from the priority queue and enqueue it into the current FIFO queue #
			if (len(prio_queue) > 0) and (tot_num_FIFO(num_gpu_devices) == 0):
				task = prio_queue[gpu_prio_queue_sel()]

				prio_queue.remove(task)
				FIFO_queue[dev_num].append(task)

				task_device.append([task.t_id, dev_num])
			'''
		t += 1

	return t

# The main function #
def execute(num_tasks, num_cpu_threads, num_gpu_devices, FIFO_queue_cap, task_list, deadline, cpu_alloc_alg, cpu_disp_alg, gpu_alg, graphic_result):
	global task_stack, alloc_queue, exec_queue, wait_queue, last_idle, FIFO_queue, ker_exec_queue, task_device, comp_tasks_cnt

	# Create the task stack and append the tasks to this list #
	task_stack = []
	for i in range(num_tasks):
		task_stack.append(task_list[i])

	# Create an allocation queue for each thread #
	alloc_queue = []
	for i in range(num_cpu_threads):
		alloc_queue.append([])

	# Create an execution queue for each thread #
	exec_queue = []
	for i in range(num_cpu_threads):
		exec_queue.append([])

	# Create a waiting queue for each thread to execute the second CPU segment of GPU-using tasks #
	wait_queue = []
	for i in range(num_cpu_threads):
		wait_queue.append([])

	# Create a list for the last idle time of the threads #
	last_idle = []
	for i in range(num_cpu_threads):
		last_idle.append(0)

	# Create a FIFO queue for each device #
	FIFO_queue = []
	for i in range(num_gpu_devices):
		FIFO_queue.append([])

	# Create a kernel execution queue for each device #
	ker_exec_queue = []
	for i in range(num_gpu_devices):
		ker_exec_queue.append([])

	# Initialize the allocation of devices to tasks #
	task_device = []

	# Initialize the number of completed tasks #
	comp_tasks_cnt = 0

	# Show the mapping algorithm #
	print('\n' + cpu_alloc_alg + '-' + cpu_disp_alg + ', ' + gpu_alg + '\n------------------------------')
	t = mapping(num_tasks, num_cpu_threads, num_gpu_devices, FIFO_queue_cap, task_list, cpu_alloc_alg, cpu_disp_alg)

	# Calculate the results #
	response_time = t # The response time
	miss_deadline = func.miss_deadline(deadline, t) # The missed deadline status of the system

	# Show the results #
	print('Response time: ' + str(response_time))
	print('Missed deadline: ' + str(miss_deadline))

	# Export the scheduling of the threads #
	func.export_scheduling(num_cpu_threads, exec_queue, 'O-KGLP', cpu_alloc_alg, cpu_disp_alg, gpu_alg, '', '')

	# Export the allocation of devices to tasks #
	func.export_device_allocation(task_device, 'O-KGLP', cpu_alloc_alg, cpu_disp_alg, gpu_alg, '', '')

	# Draw the graphical output #
	if graphic_result == 1:
		func.graphic_result(num_cpu_threads, exec_queue, t, 'O-KGLP', cpu_alloc_alg, cpu_disp_alg, gpu_alg, '', '')

	# Return the results to the main program #
	return response_time, miss_deadline
