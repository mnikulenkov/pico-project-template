import json
import sys
import subprocess
import os

BOARD_TYPES = {"pico", "pico_w", "pico2", "pico2_w"}
BUILD_TYPES = {"debug", "release"}
BEHAVIOUR_TYPES = {"run", "build_only"}
OPENOCD_DEBUG = {"enable", "disable"}

def err(text):
    print(text)
    sys.exit(1)

def run_shell_split(args):
    print(" ".join(args))
    res = subprocess.run(args, stdout=subprocess.PIPE)
    return_code = res.returncode
    #shell_output = res.stdout.decode('utf-8')
    if res.returncode != 0:
        err("Shell command '{v1}' exited with code '{v2}'".format(v1=" ".join(args), v2=return_code))

def run_shell(shell_str):
    run_shell_split(shell_str.split())

if len(sys.argv) <= 1:
    err("An error occurred: No config path passed.")

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = sys.argv[1]

try:
    with open(config_path, 'r') as file:
        config = json.loads(file.read())
    file.close()
except IOError as e:
    err("An error occurred: {}".format(e))

gdb_commands = []
if len(sys.argv) > 2:
    gdb_commands_path = sys.argv[2]
    try:
        with open(gdb_commands_path, 'r') as file:
            gdb_commands = json.loads(file.read())
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
if "openocd_debug" not in config.keys():
    err("An error occurred: No 'openocd_debug' in json structure.")

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

config["behaviour"] = config["behaviour"].lower().strip()
config["build_path"] = config["build_path"].strip()
if config["build_path"][0] != '/':
        config["build_path"] = "{v1}/{v2}".format(v1=script_dir, v2=config["build_path"])
config["build_nproc"] = config["build_nproc"].strip()
config["pico_sdk_path"] = config["pico_sdk_path"].strip()
if config["pico_sdk_path"][0] != '/':
        config["pico_sdk_path"] = "{v1}/{v2}".format(v1=script_dir, v2=config["pico_sdk_path"])
config["openocd_debug"] = config["openocd_debug"].strip()

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

try:
    int(config["build_nproc"])
except ValueError:
    err("An error occurred: incorrect build_nproc value '" + config["build_nproc"] + "'.".format())

behaviour = config["behaviour"]
if behaviour not in ("run", "build_only"):
    err("Behaviour {} is not supported.".format(behaviour))
if config["openocd_debug"] not in OPENOCD_DEBUG:
    err("An error occurred: incorrect openocd_debug parameter '{}' found.".format(config["openocd_debug"]))

do_write = True
do_build = True
do_debug = (config["openocd_debug"] == "enable")
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

        run_shell("cmake -DPICO_BOARD={v1} -DCMAKE_BUILD_TYPE={v2} -DPICO_SDK_PATH={v3} -B {v4} -S {v5}".format(v1=board_arg, v2=build_type_arg, v3=pico_sdk_path_arg, v4=make_path, v5=src_path))
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

#if do_write:
#    files = [f for f in os.listdir(bin_path) if os.path.isfile("{v1}/{v2}".format(v1=bin_path, v2=f)) and ".uf2" in f]
#    for f in files:
#        uf_path = "{v1}/{v2}".format(v1=bin_path, v2=f)
#        serial = f.split("-")[-1][:-4]
#        run_shell("picotool load {v1} --ser {v2} -f".format(v1=uf_path, v2=serial))

if do_debug: 
    openocd_startup_commands = []
    gdb_startup_commands = []

    debug_path = "{}/debug".format(bin_path)
    run_shell("mkdir -p {}".format(debug_path))
    run_shell("mkdir -p {}/config".format(debug_path))    
    run_shell("mkdir -p {}/elf".format(debug_path))
    debug_path = "{}/debug".format(bin_path)
    config_path = "{}/config".format(debug_path)
    
    #kill all present gdb and openocd tasks

    tasks = []
    gdb_port_counter = 3333
    for program in config["programs"]:
        if program["debug_device_name"] != "":
            program_name = program["name"]
            debug_device = next(d for d in config["devices"] if d["name"] == program["debug_device_name"])
            picoprobe_serial = debug_device["serial"] 
            elf_file_path = "{v1}/elf/{v2}.elf".format(v1=debug_path, v2=program_name)
            gdb_port = str(gdb_port_counter)
            gdb_port_counter = gdb_port_counter + 1;
            
            gdb_list = ["-ex file \" {}\" ".format(elf_file_path), "-ex \" target remote localhost:{}\" ".format(gdb_port), "-ex \" load\" ", "-ex \" monitor reset init\" "]
            if gdb_commands:
                if program_name in gdb_commands.keys():
                    for command in gdb_commands[program_name]:
                        gdb_list.append("-ex \" {}\" ".format(command.strip()))
            gdb_list.append("-ex \" continue\" ")

            # Copy the current environment which must include WEZTERM_UNIX_SOCKET
            env = os.environ.copy()

            # Assuming WezTerm GUI is already running, spawn new tabs with your commands:
            openocd_startup = (
                "echo -ne '\\033]2;{title}\\007'; "
                "openocd -f board/pico-debug.cfg -c 'adapter serial {serial}' -c 'gdb port {port}'; "
                "exec bash"
            ).format(title="OCD {}".format(program_name), serial=picoprobe_serial, port=gdb_port)

            spawn_cmd_1 = ["wezterm", "cli", "spawn", "--", "bash", "-c", openocd_startup]
            tasks.append(subprocess.Popen(spawn_cmd_1, env=env))

            gdb_startup = (
                "echo -ne '\\033]2;{title}\\007'; "
                "gdb-multiarch {gdb_list}; "
                "exec bash"
            ).format(title="GDB {}".format(program_name), gdb_list=" ".join(gdb_list))
            spawn_cmd_2 = ["wezterm", "cli", "spawn", "--", "bash", "-c", gdb_startup]
            tasks.append(subprocess.Popen(spawn_cmd_2, env=env))
    
