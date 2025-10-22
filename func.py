#**************************************************************************
# main.py
#
# This simulator performs task-to-accelerator mapping in OpenMP
# applications.
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
from PIL import Image, ImageDraw, ImageFont

path_length = [] # Length of all paths in the graph

# Clear the detailed contents of the tasks #
def clear(num_tasks, task_list):
	for i in range(num_tasks):
		task_list[i].thr_id = None
		task_list[i].dev_id = None
		task_list[i].status = None
		task_list[i].s_time_cpu1 = None
		task_list[i].f_time_cpu1 = None
		task_list[i].s_time_memcopy1 = None
		task_list[i].f_time_memcopy1 = None
		task_list[i].s_time_gpu = None
		task_list[i].f_time_gpu = None
		task_list[i].s_time_memcopy2 = None
		task_list[i].f_time_memcopy2 = None
		task_list[i].s_time_cpu2 = None
		task_list[i].f_time_cpu2 = None

	return task_list

# Check for current idle threads #
def check_idle_thr(num_threads, thread_queue):
	flag_empty = False

	for i in range(num_threads):
		if not bool(thread_queue[i]):
			flag_empty = True
		else:
			if thread_queue[i][len(thread_queue[i]) - 1].status == 'f_cpu' or thread_queue[i][len(thread_queue[i]) - 1].status == 'f_cpu1' or thread_queue[i][len(thread_queue[i]) - 1].status == 'f_cpu2':
				flag_empty = True

	return flag_empty

# Check meeting the dependencies #
def check_dep(task_list, dep_list):
	flag_finished = True

	for i in range(len(dep_list)):
		for j in range(len(task_list)):
			if dep_list[i] == task_list[j] and (task_list[j].status == None or task_list[j].status == 's_cpu' or task_list[j].status == 's_cpu1' or task_list[j].status == 'f_cpu1' or task_list[j].status == 's_memcopy1' or task_list[j].status == 's_gpu' or task_list[j].status == 's_memcopy2' or task_list[j].status == 'f_memcopy2' or task_list[j].status == 's_cpu2'):
				flag_finished = False

	return flag_finished

# Specify the missed deadline status of the system #
def miss_deadline(deadline, t):
	if t <= deadline:
		return 0
	else:
		return 1

# Export the scheduling of the threads to the files #
def export_scheduling(num_threads, queue, alg_name, par1, par2, par3, par4, par5):
	# Create the output file #
	if alg_name == 'O-KGLP' or 'Baseline':
		file = open("output/scheduling/" + par1 + "-" + par2 + "," + alg_name + ".dat", "w")
	elif alg_name == 'new':
		file = open("output/scheduling/" + par1 + "-" + par2 + "," + par3 + "-" + par4 + "-" + par5 + ".dat", "w")

	for i in range(num_threads):
		# Write the name of the thread #
		file.write('Thr' + str(i) + ':\n')

		# Write the name of each task executed by the thread #
		for j in range(len(queue[i])):
			file.write('T' + str(queue[i][j].t_id) + "\n")

		if i != num_threads - 1:
			file.write("\n")

	file.close()

# Export the allocation of devices to tasks to the file #
def export_device_allocation(alloc_list, alg_name, par1, par2, par3, par4, par5):
	# Create the output file #
	if alg_name == 'O-KGLP' or 'Baseline':
		file = open("output/device allocation/" + par1 + "-" + par2 + "," + alg_name + ".dat", "w")
	elif alg_name == 'new':
		file = open("output/device allocation/" + par1 + "-" + par2 + "," + par3 + "-" + par4 + "-" + par5 + ".dat", "w")

	for i in range(len(alloc_list)):
		# Write the task ID and device ID #
		if i < len(alloc_list) - 1:
			file.write(str(alloc_list[i][0]) + "," + str(alloc_list[i][1]) + "\n")
		else:
			file.write(str(alloc_list[i][0]) + "," + str(alloc_list[i][1]))

	file.close()

# Draw the graphical result #
def graphic_result(num_threads, queue, t, alg_name, par1, par2, par3, par4, par5):
	# Specify the width of the window, the height of the queues, and the height of the window #
	win_width = num_threads * 100 + (num_threads - 1) * 10 + 100 # The width of the window
	queue_height = t # The height of the queues
	win_height = queue_height * 10 + 100 # The height of the window

	# Prepare the drawing process #
	im = Image.new('RGB', (win_width, win_height), (255, 255, 255))
	draw = ImageDraw.Draw(im)

	# Draw the name and contents of each thread #
	l_point = 50
	font_thr_id = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', 20) 
	font_task_id = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', 15)

	for i in range(num_threads):
		# Draw the name of the thread #
		thr_id = 'Thr' + str(i)
		draw.text((l_point + 25, 20), thr_id, fill = "black", font = font_thr_id, align = "center")

		# Draw the main box of the thread #
		draw.rectangle((l_point, 50, l_point + 100, queue_height * 10 + 60), fill = (255, 255, 255), outline = (0, 0, 0), width = 2)

		for j in range(len(queue[i])):
			if queue[i][j].t_type == 0:
				# Draw the box related to the execution of each task #
				draw.rectangle((l_point, queue[i][j].s_time_cpu * 10 + 50, l_point + 100, queue[i][j].f_time_cpu * 10 + 50), fill = (0, 255, 0), outline = (0, 0, 0), width = 1)
				# Draw the name of the task #
				task_id = 'T' + str(queue[i][j].t_id)
				draw.text((l_point + 40, (queue[i][j].s_time_cpu + (queue[i][j].f_time_cpu - queue[i][j].s_time_cpu) // 2) * 10 + 45), task_id, fill = "black", font = font_task_id, align = "center")
			else:
				# Draw the box related to the execution of each task #
				draw.rectangle((l_point, queue[i][j].s_time_cpu1 * 10 + 50, l_point + 100, queue[i][j].f_time_cpu2 * 10 + 50), fill = (0, 255, 0), outline = (0, 0, 0), width = 1)
				# Draw the name of the task #
				task_id = 'T' + str(queue[i][j].t_id)
				draw.text((l_point + 40, (queue[i][j].s_time_cpu1 + (queue[i][j].f_time_cpu2 - queue[i][j].s_time_cpu1) // 2) * 10 + 45), task_id, fill = "black", font = font_task_id, align = "center")				

		l_point += 110

	# Create the output file #
	if alg_name == 'O-KGLP' or 'Baseline':
		im.save("output/graphic/" + par1 + "-" + par2 + "," + alg_name + ".jpg", quality = 300)
	elif alg_name == 'new':
		im.save("output/graphic/" + par1 + "-" + par2 + "," + par3 + "-" + par4 + "-" + par5 + ".jpg", quality = 300)

# Calculate the length of the critical path #
def critical_path_length(num_tasks, task_list):
	global path_length

	'''
	for i in range(num_tasks):
		dep = []
		for j in range(len(task_list[i].dep)):
			dep.append(task_list[i].dep[j].t_id)
		if len(dep) == 0:
			print(i)
		else:
			for k in range(len(dep)):
				print(str(dep[k]) + " -> " + str(i))
	'''

	# Specify source nodes #
	source = []
	for i in range(num_tasks):
		if len(task_list[i].dep) == 0:
			source.append(i)

	# Specify sink nodes #
	sink = []
	for i in range(num_tasks):
		dep = []
		for j in range(num_tasks):
			for k in range(len(task_list[j].dep)):
				dep.append(task_list[j].dep[k].t_id)
		if i not in dep:
			sink.append(i)

	# Determine graph connectivity #
	conn = [([0]*num_tasks) for i in range(num_tasks)]
	for i in range(num_tasks):
		for j in range(len(task_list[i].dep)):
			conn[task_list[i].dep[j].t_id][i] = 1

	# Calculate the length of all paths #
	path_length = []
	for i in range(len(source)):
		path_length_calc(num_tasks, task_list, conn, task_list[source[i]].exe_time, source[i])
		#path_discovery(num_tasks, conn, str(source[i]), source[i])

	return max(path_length)

# Calculate the length of all paths in the graph #
def path_length_calc(num_tasks, task_list, conn, length, task_id):
	global path_length

	flag = False
	for i in range(num_tasks):
		if conn[task_id][i] == 1:
			path_length_calc(num_tasks, task_list, conn, length + task_list[i].exe_time, i)
			flag = True
	
	if flag == False:
		path_length.append(length)

# Discover all paths in the graph #
def path_discovery(num_tasks, conn, path, task_id):
	flag = False
	for i in range(num_tasks):
		if conn[task_id][i] == 1:
			path_discovery(num_tasks, conn, path + ", " + str(i), i)
			flag = True
	
	if flag == False:
		print(path)

# Export graph specification to JSON file #
def export_json(num_tasks, task_list):
	file = open("output/dag.dat", "w")

	file.write("digraph TDG {" + "\n")
	file.write("   compound=true" + "\n")
	file.write("   subgraph cluster_0 {" + "\n")
	file.write("      label=TDG_main" + "\n")

	for i in range(num_tasks):
		if task_list[i].t_type == 0:
			file.write("      " + str(i) + "[color=blue,style=bold]" + "\n")
		else:
			file.write("      " + str(i) + "[color=red,style=bold]" + "\n")
	
	file.write("   }" + "\n")

	for i in range(num_tasks):
		dep = []
		for j in range(len(task_list[i].dep)):
			dep.append(task_list[i].dep[j].t_id)
		if len(dep) == 0:
			file.write("   " + str(i) + "\n")
		else:
			for k in range(len(dep)):
				file.write("   " + str(dep[k]) + " -> " + str(i) + "\n")

	file.write("   node [shape=plaintext];" + "\n")
	file.write("    subgraph cluster_1000 {" + "\n")
	file.write('      label="User functions:"; style="rounded";' + "\n")
	file.write(' user_funcs [label=<<table border="0" cellspacing="10" cellborder="0">' + "\n")
	file.write("      <tr>" + "\n")
	file.write('         <td bgcolor="aquamarine3" width="15px" border="1"></td>' + "\n")
	file.write("         <td>;axpy.c;saxpy;37;13;;</td>" + "\n")
	file.write("      </tr>" + "\n")
	file.write("      <tr>" + "\n")
	file.write('         <td bgcolor="crimson" width="15px" border="1"></td>' + "\n")
	file.write("         <td>;axpy.c;saxpy;58;13;;</td>" + "\n")
	file.write("      </tr>" + "\n")
	file.write("      </table>>]" + "\n")
	file.write("}}" + "\n")

	file.close()
