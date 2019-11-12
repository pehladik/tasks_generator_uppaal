# -*- coding: utf-8 -*-
__author__ = 'pehladik'

import task_generator
from string import Template


def generate_param(nb_tasks, nb_sets, utilization_factor, periods = None, round_to_int=False):
    if periods != None:
        periods = task_generator.gen_periods_discrete(nb_tasks, nb_sets, periods)
    else:
        periods = task_generator.gen_periods_loguniform(nb_tasks, nb_sets, 100, 1000, True)
    wcet = task_generator.gen_randfixedsum(nb_sets, utilization_factor, nb_tasks)
    tasksets = task_generator.gen_tasksets(wcet, periods)

    if (round_to_int):
        for i in range(0,nb_sets):
            for j in range(0,nb_tasks):
                tasksets[i][j] = (max(1,int(round(tasksets[i][j][0]))), int(round(tasksets[i][j][1])))
    return tasksets


def compute_bcet(wcet, factor):
    bcet = []
    for w in wcet:
        bcet.append(max(1,int(w*factor)))
    return bcet

def compute_utilization_factor(taskset):
    return sum([float(e[0])/e[1] for e in taskset])


def write_classic_model(taskset, name="test"):
    f = open("./model/classic_model/header.txt")
    tmp = Template(f.read())
    f.close()

    dico_header = {
        "nb_core":str(nb_cores),
        "nb_tasks":str(nb_tasks),
        "init_wpt":', '.join(["-2"]*len(taskset)),
        "task_periods":', '.join([str(int(p[1])) for p in taskset]),
        "task_wcet":', '.join([str(p[0]) for p in taskset]),
        "task_bcet":', '.join([str(e) for e in (compute_bcet([p[0] for p in taskset], 0.75))]),
        "init_value_timer": ', '.join(["false"]*len(taskset))}

    text = tmp.safe_substitute(dico_header)
    f = open("./model/classic_model/processes.txt")
    text += f.read()
    f.close()

    f = open("./model/classic_model/instantiations.txt")
    tmp = Template(f.read())
    dico_instances = {"list_task_instance": '\n'.join(["timer_task_{0} := pTimer({0});\ntask_{0} := pTask({0}, insert, up, en, cnt);".format(i) for i in range(0,nb_tasks)]),
                      "list_task":', '.join(["task_{0}".format(i) for i in range(0,nb_tasks)]),
                      "list_timer":', '.join(["timer_task_{0}".format(i) for i in range(0,nb_tasks)])}

    text += tmp.safe_substitute(dico_instances)
    f.close()
    f = open("./exp/{0}.xta".format(name),"w")
    f.write(text)
    f.close()


def write_dichotomic_model(taskset, name="test"):
    f = open("./model/factorized_model/header.txt")
    tmp = Template(f.read())
    f.close()

    dico_header = {
        "nb_core":str(nb_cores),
        "nb_tasks":str(nb_tasks),
        "init_wpt":', '.join(["-2"]*len(taskset)),
        "task_periods":', '.join([str(int(p[1])) for p in taskset]),
        "task_wcet":', '.join([str(p[0]) for p in taskset]),
        "task_bcet":', '.join([str(e) for e in (compute_bcet([p[0] for p in taskset], 0.75))]),
        "init_value_timer": ', '.join(["false"]*len(taskset))}

    text = tmp.safe_substitute(dico_header)

    f = open("./model/factorized_model/processes.txt")
    text += f.read()
    f.close()
    f = open("./model/factorized_model/instantiations.txt")
    tmp = Template(f.read())
    dico_instances = {"list_task_instance": '\n'.join(["timer_task_{0} := pTimer({0});\ntask_{0} := pTask({0}, insert, up, en, cnt);".format(i) for i in range(0,nb_tasks)]),
                      "list_task":', '.join(["task_{0}".format(i) for i in range(0,nb_tasks)]),
                      "list_timer":', '.join(["timer_task_{0}".format(i) for i in range(0,nb_tasks)])}

    text += tmp.safe_substitute(dico_instances)
    f.close()

    f = open("./exp/{0}.xta".format(name),"w")
    f.write(text)
    f.close()


def write_query(nb_task, name):
    text = ""
    for i in range(0,nb_tasks):
        text += "A[] (not task_{0}.start imply not timer_values[{0}])\n".format(i)
    text += "A[] not urg.stop"

    f = open("./exp/{0}.q".format(name),"w")
    f.write(text)
    f.close()


def model1():
	f = open("./model/header.txt")
	tmp = Template(f.read())
	f.close()

	periods = task_generator.gen_periods_uniform(nb_tasks, nsets, 100, 1000, True)
	wcet = task_generator.gen_uunifastdiscard(nsets, utilization_factor, nb_tasks)
	tasksets = task_generator.gen_tasksets(wcet, periods)

	#print(sum([a[0]/a[1] for a in zip([int(max(1,p[0]*p[1])) for p in zip(wcet[0],periods[0])], periods[0])]))

	dico_header = {
		"nb_core":str(nb_cores),
		"nb_tasks":str(nb_tasks),
		"init_wpt":', '.join(["-2" for p in periods[0]]),
		"task_periods":', '.join([str(int(p)) for p in periods[0]]),
		"task_wcet":', '.join([str(int(max(1,p[0]*p[1]))) for p in zip(wcet[0],periods[0])]),
		"list_timer": '\n'.join(["bool tick_timer_{0} := false;".format(i) for i in range(0,nb_tasks)])}

	text = tmp.safe_substitute(dico_header)

	f = open("./model/process_scheduler.txt")
	text += f.read()
	f.close()

	f = open("./model/process_task.txt")
	tmp = Template(f.read())
	for i in range (0, nb_tasks):
		dico_task = {"num_task":i}
		text += tmp.safe_substitute(dico_task)
	f.close()

	f = open("./model/instantiations.txt")
	tmp = Template(f.read())
	dico_instances = {"list_task_instance": '\n'.join(["timer_task_{0} := pTimer_task_{0}(tick_timer_{0});\ntask_{0} := pTask_{0}(insert, up, en, cnt, tick_timer_{0});".format(i) for i in range(0,nb_tasks)]),
					  "list_task":', '.join(["task_{0}".format(i) for i in range(0,nb_tasks)])}

	text += tmp.safe_substitute(dico_instances)
	f.close()

	f = open("./exp/{0}.xta".format("test"),"w")
	f.write(text)
	f.close()


nb_cores = 4
nsets = 2
nb_tasks = 5
utilization_factor = 3.4

tasksets = generate_param(nb_tasks, nsets, utilization_factor, [10,20,50,100,200], True)
print compute_utilization_factor(tasksets[0])


for i in range(0,nsets):
    write_classic_model(tasksets[i], "classic_{0}".format(i))
    write_dichotomic_model(tasksets[i], "dicho_{0}".format(i))
    write_query(nb_tasks, "query")