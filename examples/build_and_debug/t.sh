#!/bin/bash

# Find all running GDB process IDs
gdb_pids=$(pgrep gdb)

for gdb_pid in $gdb_pids; do
    echo "Processing GDB PID $gdb_pid"

    # Try to find the debuggee PID if GDB is attached to a running process
    debuggee_pid=$(lsof -p "$gdb_pid" 2>/dev/null | grep -Po 'mem\s+\K\d+' | head -n1)

    # Validate debuggee PID is numeric and non-empty
    if [[ -n "$debuggee_pid" && "$debuggee_pid" =~ ^[0-9]+$ ]]; then
        echo "Found debuggee PID $debuggee_pid for GDB PID $gdb_pid"
        gdb --pid "$debuggee_pid" --batch -ex "delete" -ex "continue"
        continue
    fi

    # If no debuggee PID, try to find executable file from GDB command line
    gdb_cmdline=$(ps -p "$gdb_pid" -o args=)

    # Extract the executable name skipping all option flags and their arguments
    # Options starting with '-' and one argument after them are skipped
    gdb_exec=$(echo "$gdb_cmdline" | awk '
    {
        skip=0;
        execname="";
        for(i=2;i<=NF;i++) {
            if(skip>0) { skip--; next }
            if($i ~ /^-/) { skip=1; next }
            if(execname=="") { execname=$i }
        }
        print execname
    }')

    # If executable found, check if file exists (consider relative path)
    if [[ -n "$gdb_exec" ]]; then
        # Try to resolve relative path with proc cwd of GDB process
        gdb_cwd=$(readlink -f /proc/$gdb_pid/cwd)
        if [[ -f "$gdb_exec" ]]; then
            gdb_exec_full="$gdb_exec"
        elif [[ -f "$gdb_cwd/$gdb_exec" ]]; then
            gdb_exec_full="$gdb_cwd/$gdb_exec"
        else
            gdb_exec_full=""
        fi

        if [[ -n "$gdb_exec_full" ]]; then
            echo "Found executable file '$gdb_exec_full' for GDB PID $gdb_pid"
            gdb "$gdb_exec_full" --batch -ex "delete" -ex "continue"
            continue
        else
            echo "Executable file '$gdb_exec' not found for GDB PID $gdb_pid"
        fi
    else
        echo "No executable found for GDB PID $gdb_pid"
    fi

    echo "No valid debuggee PID or executable to process for GDB PID $gdb_pid"
done

