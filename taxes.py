def Cv(label):
    return cell_list[label].value

exec(open("cells.py").read())

def add_a_form(name):
    global cell_list
    cell_list =dict(list(cell_list.items()) + list(eval(name).items()))


def setup_inform(print_out):
    if not print_out:  #Just adjust the calcs
        for i in cell_list.items():
            if (i[1].flag.find('u')>-1):
                i[1].calc="%s" %(i[0],)
        return

    with open("inform.py", "w") as f:
        for i in cell_list.items():
            if (i[1].flag.find('u')>-1):
                f.write(
"""
#%s
%s = 0
""" % (i[1].text, i[0]))



def print_a_form(title, fname):
    print(">>>>>>>>>> %s <<<<<<<<<" %(title,))
    out=list()
    for i in cell_list.keys():
        if (cell_list[i].form!=fname):
            continue
        if (show_optional_zeros or cell_list[i].value != 0 or cell_list[i].flag.find('o')==-1) and cell_list[i].line>0:
            out.append((cell_list[i].line, cell_list[i].text, cell_list[i].value))
    out.sort()
    max_len = 0
    for i in out:
    	max_len = max(max_len, len(i[1]))
    for i in out:
    	print("%4g | %*s | %g" %( i[0], max_len, i[1], i[2]))

def clear_done_flags(start):
    cell_list[start].done=False
    parents = cell_list[start].parents
    if (parents != None):
        for i in parents:
            clear_done_flags(i)

def print_the_tree(starting_cell, level=0):
    if level==0:
        clear_done_flags(starting_cell)
    print("%s├ %s=%g" % ("│   "*level, starting_cell, Cv(starting_cell)))
    parents = cell_list[starting_cell].parents
    if (parents != None):
        print("%s├───┐" % ("│   "*level))
        for i in parents:
            if (cell_list[i].situation and not cell_list[i].done):
                print_the_tree(i, level+1)
                cell_list[i].done=True

def get_maxcell(starting_cell, maxsofar=0, level=0):
    maxsofar = max(maxsofar, cell_list[starting_cell].value)
    parents = cell_list[starting_cell].parents
    if (parents != None):
        for i in parents:
            maxsofar = max(maxsofar, get_maxcell(i, maxsofar, level+1))
    return maxsofar

def print_to_graphviz(starting_cell, f, level=0):
    parents = deps[starting_cell]
    if (parents != None):
        for i in parents:
            f.write("%s  -> %s \n" % (i, starting_cell))
            print_to_graphviz(i, f, level+1)

def charitable():
    """A sample what-if scenario"""
    for i in cell_list.keys():
        cell_list[i].done=False
    current = -cell_list['f1040_refund'].value + cell_list['f1040_tax_owed'].value

    global f1040_sched_a_charity_cash
    f1040_sched_a_charity_cash= f1040_sched_a_charity_cash+ 100

    cell_list['f1040_refund'].compute()
    cell_list['f1040_tax_owed'].compute()

    new = -cell_list['f1040_refund'].value + cell_list['f1040_tax_owed'].value
    print("If you gave another $100 to charity, your taxes would fall by $%g" % (current-new,))



# The main routine: build interview and inform, calculate taxes, print
status="no interview yet"

import pathlib, sys
from shutil import copyfile
if (not pathlib.Path("interview.py").exists()):
    copyfile("forms/interview_template.py", "interview.py")
    print("Have generated interview.py. Please fill it in and rerun this script.")
    sys.exit(1)

exec(open("interview.py").read())
if (status=="no interview yet"):
    print("Please follow the steps in interview.py and rerun this script.")
    sys.exit(1)

from interview import *

import os
import pdb
exec(open("taxforms.py").read())

"""
for f in os.listdir('forms'):
    #pdb.set_trace()
    fsplit=f.partition('.')
    if f=='interview_template.py' or fsplit[2]!="py": continue
    exec(open("forms/"+f).read())
    add_a_form(fsplit[0])
    """

if (not pathlib.Path("inform.py").exists()):
    setup_inform(print_out=True)
    print("Have generated inform.py. Please fill it in and rerun this script.")
    sys.exit(1)

from inform import *
setup_inform(print_out=False)









cell_list['f1040_refund'].compute()
cell_list['f1040_tax_owed'].compute()
cell_list['f8582_carryover_to_next_year'].compute()
if itemizing:
    print_a_form("Schedule A", "f1040_sched_a")
if have_rr:
    print_a_form("Schedule E", "f1040_sched_e")
    print_a_form("Form 8582", "f8582")
print_a_form("Form 1040", "f1040")

#print("\n")
#print_the_tree('refund')
f=open("graph.dot", "w")
f.write("digraph {")
print_to_graphviz('f1040_refund', f)
f.write("}")
f.close()

if itemizing:
    charitable()
