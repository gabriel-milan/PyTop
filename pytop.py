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
import atexit                                   # Running scripts before exiting
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

# Initial line number
line_number = 0
this_user = getpass.getuser()
cpu_cores = psutil.cpu_count()
procs = []
proc_model = dict([
    ('pid', 000000),            # Unique ID
    ('username', 'user'),       # Owner
    ('nice', -1),               # Priority
    ('memory_percent', 0.0),    # Memory usage
    ('cpu_percent', 0.0),       # CPU usage
    ('name', 'description'),    # Description
    ('status', 'status'),       # For splitting processes according to their status
])

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

    global procs
    global cpu_cores
    global proc_model

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
            procs.append(p)
    # Sorts by CPU usage
    processes = sorted(procs, key=lambda p: p.dict['cpu_percent'],
                       reverse=True)
    return (processes)

# Procedure that prints system-related information
def print_header(procs):
    global this_user
    global cpu_cores
    global header_message

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
                user_cpu_usage += proc.cpu_percent()
            else:
                sys_cpu_usage += proc.cpu_percent()
        except:
            pass
    sys_cpu_usage /= cpu_cores
    user_cpu_usage /= cpu_cores
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

# Procedure that refreshes curses window
def refresh_window(procs):

    global cpu_cores

    templ = "%-10s %-16s %6s %8s %8s %20s"
    curses_scr.erase()
    header = templ % ("PID", "Owner", "Prior", "%Mem", "%CPU", "Description")
    print_header(procs)
    curses_print("")
    curses_print(header, invert_colors=True)
    for proc in procs:
        line = templ % (
            proc.pid,
            proc.username()[:16],
            proc.dict['nice'],
            round(proc.memory_percent(), 2),
            round(proc.cpu_percent() / cpu_cores, 2),
            proc.name() [:20]
        )
        try:
            curses_print(line)
        except curses.error:
            break
        curses_scr.refresh()

# Main function
def main():
    try:
        interval = 0
        while True:
            procs = get_processes_info(interval)
            refresh_window(procs)
            interval = 0.1
    except (KeyboardInterrupt, SystemExit):
        pass

# Calls main function
if __name__ == '__main__':
    main()