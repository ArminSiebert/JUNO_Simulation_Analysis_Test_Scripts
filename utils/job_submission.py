"""
Functions to submit jobs to the cluster. This includes the creation and execution of
submission files.
"""

__all__ = ["create_sub_files", "sub_job"]

import os
import subprocess


def create_sub_files(dir, cmd, run_num):
    """
    Creates submission files from a given shell command and run number.
    ---
    Parameters:
    dir (str): The target directory
    cmd (str): The shell command to be executed
    run_num (int): The number of runs
    ---
    Example:
    >>> create_sub_files(dir="$WORKSPACE", cmd="echo 'Job ${RUN}'", run_num=50)
    """
    ### Create submission files directory
    sub_dir = f"{dir}/sub"
    os.makedirs(sub_dir, exist_ok=True)
    ### Create sh file
    sh_file_path = f"{sub_dir}/sub.sh"
    with open(sh_file_path, "w") as f:
        f.write(
            f"#!/bin/bash\n\n"
            f"RUN=$1\n\n"
            f"export LC_ALL=C\n"
            f"export CMTCONFIG=amd64_linux26\n\n"
            f"export WORKSPACE={os.environ['WORKSPACE']}\n"
            f"export PATH={os.environ['PATH']}\n"
            f"export PYTHONPATH={os.environ['PYTHONPATH']}\n\n"
            f"source {os.environ['JUNOTOP']}/setup.sh\n"
            f"cd {dir}\n"
            f"{cmd}\n"
        )
    ### Create sub file
    sub_file_path = f"{sub_dir}/sub.sub"
    with open(sub_file_path, "w") as f:
        f.write(
            f"universe = vanilla\n\n"
            f"executable = {sh_file_path}\n"
            f"arguments = \"$(Process)\"\n\n"
            f"output = {sub_dir}/job_$(Process).out\n"
            f"error  = {sub_dir}/job_$(Process).err\n"
            f"log    = {sub_dir}/job_$(Process).log\n\n"
            f"+MaxRuntime = 1000000\n"
            f"ShouldTransferFiles = YES\n"
            f"WhenToTransferOutput = ON_EXIT\n"
            #f"transfer_output_files = Test_Sim_Job\n"
            #f'transfer_output_remaps = "Test_Sim_Job = Test_Sim_Job_$(Process)"\n\n'
            f"queue {run_num}\n"
)


def sub_job(dir, cmd=None, run_num=None):
    """
    Submits a job from submission files or from a given shell command and run number.
    ---
    Parameters:
    dir (str): The target directory
    cmd (str, optional): The shell command to be executed
    run_num (int, optional): The number of runs
    ---
    Example:
    >>> sub_job(dir="$WORKSPACE")                                       # w sub files
    >>> sub_job(dir="$WORKSPACE", cmd="echo 'Run ${RUN}'", run_num=50)  # w/o sub files
    """
    sub_file_path = f"{dir}/sub/sub.sub"
    if not os.path.isfile(sub_file_path) or (cmd != None and run_num != None):
        create_sub_files(dir, cmd, run_num)
    subprocess.run(["condor_submit", sub_file_path])
