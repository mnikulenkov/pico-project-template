import json
import sys
import subprocess
import os
import time
import socket

BOARD_TYPES = {"pico", "pico_w", "pico2", "pico2_w"}
BUILD_TYPES = {"debug", "release"}
BEHAVIOUR_TYPES = {"run", "build_only"}
GDB_DEBUG = {"on", "off"}
PICOTOOL_LISTEN = {"on", "off"}
OPENOCD_OUTPUT = {"on", "off"}

PICO_RELOAD_TIMEOUT = 10
PICOTOOL_LOAD_TIMEOUT = 10
OPENOCD_INIT_TIMEOUT = 5

def send_gdb_command_remote(gdb_port, cmd):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', int(gdb_port)))
            s.sendall((cmd + "\n").encode())
            # Read response if needed
            return True
    except (ConnectionRefusedError, OSError) as e:
        print(f"Failed to connect to GDB on port {gdb_port}: {e}")
        return False

def err(text):
    print(text)
    sys.exit(1)

def run_shell_split(args, sudo=False, root_pw=''):
    print(" ".join(args))
    if not sudo:
        res = subprocess.run(args, stdout=subprocess.PIPE)
    else:
        root_pw_fix = root_pw + "\n"
        args_fix = ["sudo", "-S"] + args
        res = subprocess.run(args_fix, input=root_pw_fix.encode(), stdout=subprocess.PIPE)
    return_code = res.returncode
    #shell_output = res.stdout.decode('utf-8')
    if res.returncode != 0:
        err("Shell command '{v1}' exited with code '{v2}'".format(v1=" ".join(args), v2=return_code))

def run_shell(shell_str, sudo=False, root_pw=''):
    run_shell_split(shell_str.split(), sudo=sudo, root_pw=root_pw)

if len(sys.argv) <= 1:
    err("An error occurred: No config path passed.")

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = sys.argv[1]

ignore_stdout_warning = False
if len(sys.argv) >= 3:
    if sys.argv[2].lower().strip() == "--ignore_stdout_warning":
        ignore_stdout_warning = True

try:
    with open(config_path, 'r') as file:
        config = json.loads(file.read())
    file.close()
except IOError as e:
    err("An error occurred: {}".format(e))

#check config correctness
if "devices" not in config.keys():
    err("An error occurred: No 'devices' in json structure.")
if "programs" not in config.keys():
    err("An error occurred: No 'programs' in json structure.")
if "behaviour" not in config.keys():
    err("An error occurred: No 'behaviour' in json structure.")
if "build_path" not in config.keys():
    err("An error occurred: No 'build_path' in json structure.")
if "pico_sdk_path" not in config.keys():
    err("An error occurred: No 'pico_sdk_path' in json structure.")
if "build_nproc" not in config.keys():
    err("An error occurred: No 'build_nproc' in json structure.")
if "gdb_debug" not in config.keys():
    err("An error occurred: No 'gdb_debug' in json structure.")
if "gdb_commands_path" not in config.keys():
    err("An error occurred: No 'gdb_commands_path' in json structure.")
if "openocd_output" not in config.keys():
    err("An error occurred: No 'openocd_output' in json structure.")
if "picotool_listen" not in config.keys():
    err("An error occurred: No 'picotool_listen' in json structure.")
if "root_pw" not in config.keys():
    err("An error occurred: No 'root_pw' in json structure.")

for device in config["devices"]:
    if "name" not in device:
        err("An error occurred: Incorrect device specified, no 'name' found")
    if "board" not in device:
        err("An error occurred: Incorrect device specified, no 'board' found")
    if "serial" not in device:
        err("An error occurred: Incorrect device specified, no 'serial' found")

for program in config["programs"]:
    if "name" not in program:
        err("An error occurred: Incorrect program specified, no 'name' found")
    if "build_type" not in program:
        err("An error occurred: Incorrect program specified, no 'build_type' found")
    if "device_name" not in program:
        err("An error occurred: Incorrect program specified, no 'device_name' found")
    if "src_path" not in program:
        err("An error occurred: Incorrect program specified, no 'src_path' found") 
    if "debug_device_name" not in program:
        err("An error occurred: Incorrect program specified, no 'debug_device_name' found")
    if "gdb_port" not in program:
        err("An error occurred: Incorrect program specified, no 'gdb_port' found")
    if "tcl_port" not in program:
        err("An error occurred: Incorrect program specified, no 'tcl_port' found")
    if "telnet_port" not in program:
        err("An error occurred: Incorrect program specified, no 'telnet_port' found")
    if '-' in program["name"]:
        err("Forbidden symbol '-' in program name")

#convert values to lowercase
#ingore serial
for device in config["devices"]:
    device["name"] = device["name"].lower().strip()
    device["board"] = device["board"].lower().strip()
    device["serial"] = device["serial"].upper().strip()

#ingore src_path
for program in config["programs"]:
    program["name"] = program["name"].lower().strip().replace(" ", "_")
    program["build_type"] = program["build_type"].lower().strip()
    program["device_name"] = program["device_name"].lower().strip()
    program["debug_device_name"] = program["debug_device_name"].lower().strip()
    program["src_path"] = program["src_path"].strip()
    if program["src_path"][0] != '/':
        program["src_path"] = "{v1}/{v2}".format(v1=script_dir, v2=program["src_path"])
    program["src_path"] = program["src_path"].strip()
    program["gdb_port"] = program["gdb_port"].strip()
    program["tcl_port"] = program["tcl_port"].strip()
    program["telnet_port"] = program["telnet_port"].strip()

config["behaviour"] = config["behaviour"].lower().strip()
config["build_path"] = config["build_path"].strip()
if config["build_path"][0] != '/':
        config["build_path"] = "{v1}/{v2}".format(v1=script_dir, v2=config["build_path"])
config["build_nproc"] = config["build_nproc"].strip()
config["pico_sdk_path"] = config["pico_sdk_path"].strip()
if config["pico_sdk_path"][0] != '/':
        config["pico_sdk_path"] = "{v1}/{v2}".format(v1=script_dir, v2=config["pico_sdk_path"])
config["gdb_commands_path"] = config["gdb_commands_path"].strip()
if config["gdb_commands_path"][0] != '/':
        config["gdb_commands_path"] = "{v1}/{v2}".format(v1=script_dir, v2=config["gdb_commands_path"])
config["openocd_output"] = config["openocd_output"].lower().strip()
config["picotool_listen"] = config["picotool_listen"].lower().strip()
config["root_pw"] = config["root_pw"].strip()

#check for duplicates
DEVICE_NAMES = set()
for device in config["devices"]:
    if device["name"] in DEVICE_NAMES:
        err("An error occurred: Duplicate device name found.")
    DEVICE_NAMES.add(device["name"])

PROGRAM_NAMES = set()
for program in config["programs"]:
    if program["name"] in PROGRAM_NAMES:
        err("An error occurred: Duplicate program name found.") 
    PROGRAM_NAMES.add(program["name"])

PROGRAM_GDB_PORTS = set()
for program in config["programs"]:
    if program["gdb_port"] in PROGRAM_GDB_PORTS and len(program["gdb_port"]) > 0:
        err("An error occurred: Duplicate gdb port found.") 
    PROGRAM_NAMES.add(program["gdb_port"])

PROGRAM_TCL_PORTS = set()
for program in config["programs"]:
    if program["tcl_port"] in PROGRAM_GDB_PORTS and len(program["tcl_port"]) > 0:
        err("An error occurred: Duplicate tcl port found.") 
    PROGRAM_NAMES.add(program["tcl_port"])

PROGRAM_TELNET_PORTS = set()
for program in config["programs"]:
    if program["telnet_port"] in PROGRAM_GDB_PORTS and len(program["telnet_port"]) > 0:
        err("An error occurred: Duplicate telnet port found.") 
    PROGRAM_NAMES.add(program["telnet_port"])

#check settings correctness
for device in config["devices"]:
    if device["board"] not in BOARD_TYPES:
        err("An error occurred: incorrect board type '{}' found.".format(device["board"]))

for program in config["programs"]:
    if program["build_type"] not in BUILD_TYPES:
        err("An error occurred: incorrect board type '{}' found.".format(program["build_type"]))
    if program["device_name"] not in DEVICE_NAMES:
        err("An error occurred: device name '{}' is not specified.".format(program["device_name"]))
    if program["debug_device_name"] not in DEVICE_NAMES and program["debug_device_name"] != "":              
        err("An error occurred: debug device name '{}' is not specified.".format(program["debug_device_name"]))

if config["behaviour"] not in BEHAVIOUR_TYPES:
    err("An error occurred: incorrect behaviour '{}' found.".format(config["behaviour"]))
if config["picotool_listen"] not in PICOTOOL_LISTEN:
    err("An error occurred: incorrect picotool_listen parameter '{}' found.".format(config["picotool_listen"]))

try:
    int(config["build_nproc"])
except ValueError:
    err("An error occurred: incorrect build_nproc value '" + config["build_nproc"] + "'.".format())

behaviour = config["behaviour"]
if behaviour not in ("run", "build_only"):
    err("Behaviour {} is not supported.".format(behaviour))
if config["gdb_debug"] not in GDB_DEBUG:
    err("An error occurred: incorrect gdb_debug parameter '{}' found.".format(config["gdb_debug"]))

gdb_commands = []
if len(config["gdb_commands_path"]) > 0:
    try:
        with open(config["gdb_commands_path"], 'r') as file:
            gdb_commands = json.loads(file.read())
        file.close()
    except IOError as e:
        err("An error occurred: {}".format(e))

if not ignore_stdout_warning and config["picotool_listen"] == "off" and config["behaviour"] == "run":
    while True:
        answer = input("Proceeding will flash devices with regular binaries. You will have to manually flash them with picotool-friendly binaries to use this tool later. Do you want to continue? (y/n): ").strip().lower()
        if answer in ('yes', 'no', 'y', 'n'):
            break
        if answer in ('no', 'n'):
            print("Terminating program.")
        sys.exit(0)

do_write = True
do_build = True
do_debug = (config["gdb_debug"] == "on")
if behaviour in ("build_only"):
    do_write = False
    do_debug = False

build_path = config["build_path"]
build_nproc = config["build_nproc"]
pico_sdk_path_arg = config["pico_sdk_path"]

if build_path[-1] == '/':
    build_path = build_path[:-1]
if build_path[0] != '/':
    build_path = "{v1}/{v2}".format(v1=script_dir, v2=build_path)
if pico_sdk_path_arg[-1] == '/':
    pico_sdk_path_arg = pico_sdk_path_arg[:-1]
if pico_sdk_path_arg[0] != '/':
    pico_sdk_path_arg = "{v1}/{v2}".format(v1=script_dir, v2=pico_sdk_path_arg)

if do_build:
    bin_path = "{}/bin".format(build_path)
    run_shell("mkdir -p {}".format(bin_path))
    run_shell("rm -r {}".format(bin_path))
    run_shell("mkdir -p {}".format(bin_path))

for program in config["programs"]:
    device = next(d for d in config["devices"] if d["name"] == program["device_name"])
    board_arg = device["board"]
    stdio_usb_arg = (config["picotool_listen"] == "on")
    serial = device["serial"]
    program_name = program["name"]

    if do_build:
        program_name = program["name"]

        make_path = "{v1}/make/{v2}".format(v1=build_path, v2=program_name)
        run_shell("mkdir -p {}".format(make_path))

        if program["build_type"] == "debug" or do_debug:
            build_type_arg = "Debug"
        else:
            build_type_arg = "Release"
        src_path = program["src_path"] 

        run_shell("cmake -DPICO_BOARD={v1} -DCMAKE_BUILD_TYPE={v2} -DPICO_SDK_PATH={v3} -DSTDIO_USB={v4} -B {v5} -S {v6}".format(v1=board_arg, v2=build_type_arg, v3=pico_sdk_path_arg, v4=stdio_usb_arg, v5=make_path, v6=src_path))
        files = [f for f in os.listdir(make_path) if os.path.isfile("{v1}/{v2}".format(v1=make_path, v2=f)) and ".uf2" in f]
        target_absent = (len(files) == 0)
        if len(files) > 1:
            err("Target is unclear: multiple .uf2 files in make directory. Clear the build directory")

        if target_absent:
            run_shell("make -C {v1} -j {v2} --always-make".format(v1=make_path, v2=build_nproc))
        else:
            run_shell("make -C {v1} -j {v2}".format(v1=make_path, v2=build_nproc))

        files = [f for f in os.listdir(make_path) if os.path.isfile("{v1}/{v2}".format(v1=make_path, v2=f)) and ".uf2" in f]
        if len(files) > 1:
            err("Target is unclear: multiple .uf2 files in make directory. Clear the build directory")
        run_shell("cp {v1}/{v2} {v3}/{v4}-{v5}.uf2".format(v1=make_path, v2=files[0], v3=bin_path, v4=program_name, v5=serial))
                
        files = [f for f in os.listdir(make_path) if os.path.isfile("{v1}/{v2}".format(v1=make_path, v2=f)) and ".elf" in f and ".map" not in f]
        if len(files) > 1:
            err("Target is unclear: multiple .elf files in make directory. Clear the build directory")
        run_shell("mkdir -p {}/debug/elf".format(bin_path))
        run_shell("cp {v1}/{v2} {v3}/debug/elf/{v4}.elf".format(v1=make_path, v2=files[0], v3=bin_path, v4=program_name))

if do_write:
    files = [f for f in os.listdir(bin_path) if os.path.isfile("{v1}/{v2}".format(v1=bin_path, v2=f)) and ".uf2" in f]
    for f in files:
        uf_path = "{v1}/{v2}".format(v1=bin_path, v2=f)
        serial = f.split("-")[-1][:-4]
        run_shell("picotool reboot --ser {v1} -f".format(v1=serial), sudo=True, root_pw=config["root_pw"])
        time.sleep(PICO_RELOAD_TIMEOUT)
        run_shell("picotool load {v1} --ser {v2} -f".format(v1=uf_path, v2=serial), sudo=True, root_pw=config["root_pw"])

#wait for picos to reboot
print("Rebooting...")
time.sleep(PICOTOOL_LOAD_TIMEOUT)

ocd_tasks = []
gdb_tasks = []
gdb_tasks_ports = []
openocd_gdb_conn_proc = None
if do_debug: 
    openocd_gdb_conn = [
    "openocd",
    "-f", "openocd.cfg",
    "-c", "gdb_max_connections 4"
    ]

    openocd_gdb_conn_proc = subprocess.Popen(
        openocd_gdb_conn,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    openocd_startup_commands = []
    gdb_startup_commands = []

    debug_path = "{}/debug".format(bin_path)
    run_shell("mkdir -p {}".format(debug_path))
    run_shell("mkdir -p {}/config".format(debug_path))    
    run_shell("mkdir -p {}/elf".format(debug_path))
    debug_path = "{}/debug".format(bin_path)
    config_path = "{}/config".format(debug_path)
    
    #kill all openocd and gdb jobs
    subprocess.run(["killall", "-9", "openocd"])
    subprocess.run(["killall", "-9", "gdb"])

    enable_openocd_output = (config["openocd_output"] == "on")
    for program in config["programs"]:
        if program["build_type"] == "release":
            continue
        if program["debug_device_name"] != "":
            program_name = program["name"]
            debug_device = next(d for d in config["devices"] if d["name"] == program["debug_device_name"])
            target_device = next(d for d in config["devices"] if d["name"] == program["device_name"])
            picoprobe_serial = debug_device["serial"] 
            elf_file_path = "{v1}/elf/{v2}.elf".format(v1=debug_path, v2=program_name)
            gdb_port = program["gdb_port"]
            tcl_port = program["tcl_port"]
            telnet_port = program["telnet_port"]
            if target_device["board"] in ("pico", "pico_w"):
                target_arch = "rp2040"
            else:
                target_arch = "rp2350"
            
            gdb_list = ["-ex \"set confirm off\"", "-ex \"set pagination off\"","-ex \"file {}\" ".format(elf_file_path), "-ex \"target remote localhost:{}\" ".format(gdb_port), "-ex \"load\" ", "-ex \"monitor reset init\" "]
            if gdb_commands:
                if program_name in gdb_commands.keys():
                    for command in gdb_commands[program_name]:
                        gdb_list.append("-ex \"{}\" ".format(command.strip()))
            gdb_list.append("-ex \"continue\" ")

            # Copy the current environment which must include WEZTERM_UNIX_SOCKET
            env = os.environ.copy()
            
            if enable_openocd_output:
                # Assuming WezTerm GUI is already running, spawn new tabs with your commands:
                openocd_startup = (
                    "echo -ne '\\033]2;{title}\\007'; "
                    "echo '{root_pw}' | sudo -S openocd -f interface/cmsis-dap.cfg -f target/{target_arch}.cfg -c 'adapter serial {serial}' -c 'adapter speed 5000' -c 'gdb port {gdb_port}' -c 'tcl port {tcl_port}' -c 'telnet port {telnet_port}' -c 'program {elf} verify reset'; "
                 "exec bash"
                ).format(title="OCD {}".format(program_name), serial=picoprobe_serial, gdb_port=gdb_port, tcl_port=tcl_port, telnet_port=telnet_port, root_pw=config["root_pw"], elf=elf_file_path, target_arch=target_arch)

                spawn_cmd_1 = ["wezterm", "cli", "spawn", "--", "bash", "-c", openocd_startup]
                ocd_tasks.append(subprocess.Popen(spawn_cmd_1, env=env))
            else:
                openocd_startup = (
                    "echo '{root_pw}' | sudo -S openocd -f interface/cmsis-dap.cfg -f target/{target_arch}.cfg "
                    "-c 'adapter serial {serial}' "
                    "-c 'adapter speed 5000'"                  
                    "-c 'gdb port {gdb_port}'"
                    "-c 'tcl port {tcl_port}'"
                    "-c 'telnet port {telnet_port}'"
                    "-c 'program {elf} verify reset'"
                ).format(serial=picoprobe_serial, gdb_port=gdb_port, tcl_port=tcl_port, telnet_port=telnet_port, root_pw=config["root_pw"], elf=elf_file_path, target_arch=target_arch)

                spawn_cmd_1 = ["bash", "-c", openocd_startup]
                ocd_tasks.append(subprocess.Popen(spawn_cmd_1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env))
            
            print("Starting OpenOCD...")
            time.sleep(OPENOCD_INIT_TIMEOUT)            
    
            gdb_startup = (
                "echo -ne '\\033]2;{title}\\007'; "
                "gdb-multiarch {gdb_list}; "
                "exec bash"
            ).format(title="GDB {}".format(program_name), gdb_list=" ".join(gdb_list))
            spawn_cmd_2 = ["wezterm", "cli", "spawn", "--", "bash", "-c", gdb_startup]
            gdb_tasks.append(subprocess.Popen(spawn_cmd_2, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            gdb_tasks_ports.append(int(gdb_port))

print("Done.")
while True:
    answer = input("Type 'stop' or 's' to finish\n").strip().lower()
    if answer in ('stop', 's'):
        for gdb_port in gdb_tasks_ports:
            while True:
                time.sleep(0.5)
                if send_gdb_command_remote(gdb_port, "delete"):
                    print("Sent delete command to GDB.")
                    break
                else:   
                    print("Trying again.")
            while True:
                time.sleep(0.5)
                if send_gdb_command_remote(gdb_port, "delete"):
                    print("Sent continue command to GDB.")
                    break
                else:   
                    print("Trying again.")
        break
time.sleep(1)
#subprocess.run(["killall", "-9", "wezterm"])
#subprocess.run(["killall", "-9", "wezterm-gui"])
