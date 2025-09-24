#This script can perform multiple scripts
#executing this script performs hole simualtion and analysis 
# Settings have to be correct before executing!!
#  
# Things to do before executing this script
# 1. define simulation parameters in DetSim 
# 2. define the directory 'dir_nm' in every scrip
# 3. check that evtmax is the same in every script

# import subprocess
# import os 
# workspace = os.environ.get("WORKSPACE")
# dir_nm = "SimulationScripts"
# base_dir = os.path.join(workspace,dir_nm)

# scripts = [
#     #os.path.join(base_dir, "DetSim.py"), 
#     os.path.join(base_dir, "det2rec.py"),
#     os.path.join(base_dir, "det2elec.py"),
#     os.path.join(base_dir, "elec2rec.py"),
#     os.path.join(base_dir, "Analysis.py")
#     ] 


# for i, script in enumerate(scripts, start=1):
#     print(f"[{i}/{len(scripts)}] Running {script} ...")
#     result = subprocess.run(["python", script])
#     if result.returncode != 0:
#         print(f"Script {script} failed with exit code {result.returncode}")
#         break  # stop execution on failure



import subprocess
import os

setup_script = "/storage/gpfs_data/juno/junofs/users/siebert/setupscript.sh"

workspace = os.environ.get("WORKSPACE")
dir_nm = "SimulationScripts"
base_dir = os.path.join(workspace, dir_nm)

scripts = [
    os.path.join(base_dir, "DetSim.py"),
    os.path.join(base_dir, "det2rec.py"),
    os.path.join(base_dir, "det2elec.py"),
    os.path.join(base_dir, "elec2rec.py"),
    os.path.join(base_dir, "Analysis.py"),
]

for i, script in enumerate(scripts, start=1):
    print(f"[{i}/{len(scripts)}] Running {script} ...")
    # Hier wird zuerst das Setup-Script gesourced, dann das Python-Script gestartet
    #cmd = f"bash -c 'source {setup_script} && python {script}'"
    cmd = f"python {script}"
    result = subprocess.run(cmd, shell=True, executable="/bin/bash")
    if result.returncode != 0:
        print(f"Script {script} failed with exit code {result.returncode}")
        break
