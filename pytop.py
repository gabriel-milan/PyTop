# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                       #
#                                       PyTop                                           #
#                       https://github.com/gabriel-milan/PyTop                          #
#       A solution similar to UNIX "top" command with a few different features          #
#                                                                                       #
#   Authors:                                                                            #
#   - Gabriel Gazola Milan (gabriel.gazola@poli.ufrj.br)                                #
#   - Victor Rafael Breves Santos Ferreira (victor.breves@poli.ufrj.br)                 #
#                                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#
#   Imports
#
import os                                       # Gets LoadAvg
import sys                                      # Exiting the script if requirements are not satisfied
import time                                     # Sleeping
import ctypes
import atexit                                   # Running scripts before exiting
import _thread                                  # Getting user input by making a thread
import getpass                                  # Gets the username
import datetime                                 # Gets now() time
try:
    import psutil                               # Process management library
except ImportError:
    sys.exit('==> Requirement not satisfied: "psutil"')
try:
    import curses                               # Graphical interface library
except ImportError:
    sys.exit('==> Your OS is not supported. Please check https://github.com/gabriel-milan/PyTop for further information.')

# Global vars
line_number = 0
procs_cpu_average = dict()
change_priority_status = 0                      # Define [0] to print a message waiting, [1] to get the PID from user and [2] to get the priority
user_input = []                                 # Keeps the user input here
change_pid = 0
change_priority = 0

# Global constants
this_user = getpass.getuser()
cpu_cores = psutil.cpu_count()
average_number = 10
header_message = "PyTop v1.0 - https://github.com/gabriel-milan/PyTop"

# Procedure to terminate a curses application
def terminate_curses():
    curses.nocbreak()
    curses_scr.keypad(False)
    curses.echo()
    curses.endwin()

# Procedure that writes a line into curses screen
def curses_print(line, invert_colors=False):
    # Takes global var "line_number"
    global line_number
    try:
        if invert_colors:
            line += " " * (curses_scr.getmaxyx()[1] - len(line))
            curses_scr.addstr(line_number, 0, line, curses.A_REVERSE)
        else:
            curses_scr.addstr(line_number, 0, line, 0)
    except curses.error:
        line_number = 0
        curses_scr.refresh()
        raise
    else:
        line_number += 1

# Procedure to start curses application
curses_scr = curses.initscr()
curses.noecho()
atexit.register(terminate_curses)

# Function that returns a readable type of bytes
def readable_bytes(n_bytes):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n_bytes >= prefix[s]:
            value = int(float(n_bytes) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n_bytes

# Function that returns processes and information about them
def get_processes_info(interval):

    global average_number
    global procs_cpu_average

    # Sleeps for "interval"
    time.sleep(interval)
    procs = []
    for p in psutil.process_iter():
        try:
            p.dict = p.as_dict([
                'pid',              # Unique ID
                'username',         # Owner
                'nice',             # Priority
                'memory_percent',   # Memory usage
                'cpu_percent',      # CPU usage
                'name',             # Description
                'status',           # For splitting processes according to their status
            ])
        except:
            pass
        else:
            if (p.pid in procs_cpu_average):
                if (len(procs_cpu_average[p.pid]) >= average_number):
                    procs_cpu_average[p.pid].pop(0)
                else:
                    procs_cpu_average[p.pid].append(p.dict['cpu_percent'])
            else:
                procs_cpu_average[p.pid] = [p.dict['cpu_percent']]
            procs.append(p)
    # Sorts by CPU usage
    processes = sorted(procs, key=lambda p: sum(procs_cpu_average[p.pid]),
                       reverse=True)
    return (processes)

# Procedure that prints system-related information
def print_header(procs):

    global this_user
    global cpu_cores
    global header_message
    global average_number
    global procs_cpu_average
    global change_priority_status

    # Function that returns the no. of pipeline characters and space characters (max. of 40)
    def count_pipelines(perc):
        dashes = "|" * int((float(perc) / 10 * 4.1))
        empty_dashes = " " * (41 - len(dashes))
        return dashes + empty_dashes

    curses_print(header_message, invert_colors=True)
    curses_print("")

    # Gets CPU usage
    sys_cpu_usage = 0.0
    user_cpu_usage = 0.0
    for proc in procs:
        try:
            if (proc.username() == this_user):
                user_cpu_usage += sum(procs_cpu_average[proc.pid])
            else:
                sys_cpu_usage += sum(procs_cpu_average[proc.pid])
        except:
            pass
    sys_cpu_usage /= (cpu_cores * average_number)
    user_cpu_usage /= (cpu_cores * average_number)
    curses_print(" CPU (User) [%s] %5s%%" % (count_pipelines(user_cpu_usage), round(user_cpu_usage, 2)))
    curses_print(" CPU (Syst) [%s] %5s%%" % (count_pipelines(sys_cpu_usage), round(sys_cpu_usage, 2)))

    # Gets memory usage
    mem = psutil.virtual_memory()
    mem_usage_bar = count_pipelines(mem.percent)
    line = " Memory     [%s] %5s%% %6s / %s" % (
        mem_usage_bar,
        mem.percent,
        str(int(mem.used / 1024 / 1024)) + "M",
        str(int(mem.total / 1024 / 1024)) + "M"
    )
    curses_print(line)

    # Gets swap usage
    swap = psutil.swap_memory()
    swap_usage_bar = count_pipelines(swap.percent)
    line = " Swap       [%s] %5s%% %6s / %s" % (
        swap_usage_bar,
        swap.percent,
        str(int(swap.used / 1024 / 1024)) + "M",
        str(int(swap.total / 1024 / 1024)) + "M"
    )
    curses_print(line)

    # Gets load average and uptime
    uptime = datetime.datetime.now() - \
        datetime.datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    line = " Load avg:  1 min [%.2f] / 5 min [%.2f] / 15 min [%.2f]  Uptime: %s" \
        % (av1, av2, av3, str(uptime).split('.')[0])
    curses_print(line)

    # Prints the "waiting for character" line
    curses_print("")
    if (change_priority_status == 0):
        curses_print (" Press [c] to change the priority of a process by its PID", invert_colors=True)
    elif (change_priority_status == 1):
        curses_print (" Which process do you want to change priority? PID: " + "".join(user_input), invert_colors=True)
    elif (change_priority_status == 2):
        curses_print (" What priority to set? It can be a value from -20 to 20,", invert_colors=True)
        curses_print (" the lower the value, the higher priority > " + "".join(user_input), invert_colors=True)
    else:
        change_priority_status = 0

# Procedure that refreshes curses window
def refresh_window(procs):

    global cpu_cores

    templ = "%-10s %-16s %6s %8s %8s %20s %8s"
    curses_scr.erase()
    header = templ % ("PID", "Owner", "Prior", "%Mem", "%CPU", "Description", "Status")
    print_header(procs)
    curses_print("")
    curses_print(header, invert_colors=True)
    try:
        for proc in procs:
            line = templ % (
                proc.pid,
                proc.username()[:16],
                proc.dict['nice'],
                round(proc.memory_percent(), 2),
                round(sum(procs_cpu_average[proc.pid]) / average_number / cpu_cores, 2),
                proc.name() [:20],
                proc.dict['status']
            )
            try:
                curses_print(line)
            except curses.error:
                break
            curses_scr.refresh()
    except:
        pass

# Thread to get user inputs
def input_thread ():
    global user_input
    c = curses_scr.getkey()
    user_input.append(c)
    _thread.exit()
    return

# Procedure to change process priority
def change_process_priority (procs, pid, priority):
    global user_input
    for proc in procs:
        if proc.pid == pid:
            proc.nice(priority)
            user_input = ['TESTE']
    return

# Main function
def main():

    global user_input
    global change_pid
    global change_priority
    global change_priority_status

    import ctypes, os
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if (is_admin == False):
        print ("==> Please run with admin privileges!")
        return

    try:
        interval = 0.1
        create_thread = True
        while (True):
            if (create_thread == True):
                _thread.start_new_thread(input_thread, ())
                create_thread = False
            procs = get_processes_info(interval)
            refresh_window(procs)
            if (len(user_input) > 0):
                if (change_priority_status == 0):
                    if ((user_input[0] == 'C') or (user_input[0] == 'c')):
                        change_priority_status = 1
                    user_input = []
                    create_thread = True
                elif (change_priority_status == 1):
                    if (user_input[-1] == '\n'):
                        change_priority_status = 2
                        change_pid = int("".join(user_input))
                        user_input = []
                    elif (user_input[-1] == '\x7f'):
                        user_input = user_input[:-2]
                    elif (user_input[-1].isdigit() == False):
                        user_input = user_input[:-1]
                    create_thread = True
                elif (change_priority_status == 2):
                    if (user_input[-1] == '\n'):
                        change_priority_status = 0
                        change_priority = int("".join(user_input))
                        change_process_priority(procs, change_pid, change_priority)
                        user_input = []
                    elif (user_input[-1] == '\x7f'):
                        user_input = user_input[:-2]
                    elif (user_input[-1].isdigit() == False):
                        if (len(user_input) > 1):
                            user_input = user_input[:-1]
                        elif (user_input[-1] != '-'):
                            user_input = user_input[:-1]
                    create_thread = True
    except (KeyboardInterrupt, SystemExit):
        pass

# Calls main function
if __name__ == '__main__':
    main()