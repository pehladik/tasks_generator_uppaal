# -*- coding: utf-8 -*-
__author__ = 'pehladik'

import task_generator
from string import Template


nb_cores = 4
nsets = 1
nb_tasks = 10
utilization_factor = 1.4

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

f = open("../exp/{0}.xta".format("toto"),"w")
f.write(text)
f.close()



