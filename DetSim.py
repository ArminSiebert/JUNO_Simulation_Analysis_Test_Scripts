#This script does the detector simulation 
# example: You can simulate 3x e- (100 MeV , pos: ["0", "0", "0"]) and 2x e- (10 MeV, pos: ["1", "2", "3"] ) 
# N = [3,2], particles = "e-",  positions = [["0","0","0"],["1","2","3"]]

import subprocess
import os
import random

#region JUNOSW
# Pfad zu deinem Setupscript
SETUP_SCRIPT = "/storage/gpfs_data/juno/junofs/users/siebert/setupscript.sh"

# Befehl: sourcen und dann alle Umgebungsvariablen ausgeben
cmd = f"source {SETUP_SCRIPT} && env"

# Subprozess mit Bash starten
proc = subprocess.Popen(
    cmd,
    shell=True,
    executable="/bin/bash",
    stdout=subprocess.PIPE
)

# Alle Variablen aus subprocess in das aktuelle Python-Environment laden
for line in proc.stdout:
    key, _, value = line.decode("utf-8").partition("=")
    os.environ[key] = value.strip()

TUTORIALROOT = os.environ["TUTORIALROOT"]
print(f'{TUTORIALROOT=}')      
#endregion

#Settings
dir_nm = "Simulation_Muon" #has to be changed correctly! directory where everything should be saved. Doesen't need to exist
#List of number of particles with the same parameters  
N = [1,1,1] 
# Parameter
evtmax = "1"    #these 3 has to stay the same for one run
start_evtid = "0"
particles = "mu-"
positions = [["0", "0", "0"],["0", "0", "0"],["0", "0", "0"]]
momentums = [["1000"],["2000"],["3000"]]


TUTORIALROOT = os.environ["TUTORIALROOT"]
print(f'{TUTORIALROOT=}')
workspace = os.environ.get("WORKSPACE")

os.makedirs(os.path.join(workspace, dir_nm), exist_ok=True) 
if workspace is None:
    raise RuntimeError("environment variable WORKSPACE is not set!")
output_dir = os.path.join(workspace, dir_nm, "detsim")  #declacre the output directory
os.makedirs(output_dir, exist_ok=True)

if len(N)==len(positions)==len(momentums):
    print("parameters work together")
else:
    raise ValueError("parameters don't work together. Check if N, positions and momentums have the same length")

#Simulation  
for j in range(len(N)):
    print(f"Group [{j+1}/{len(N)}]  with {momentums[j][0]}MeV and positions {positions[j]} is Running")
    for i in range(1, N[j] + 1):
        seed = random.randint(0, 32767)
        suffix = f"{particles}_{i}"
        
        output_file = os.path.join(output_dir, f"{suffix}_{momentums[j][0]}MeV_{evtmax}Evts_0to0R_{seed}seed_det.root")
        user_output_file = os.path.join(output_dir, f"{suffix}_{momentums[j][0]}MeV_{evtmax}Evts_0to0R_{seed}seed_det_user.root")

        cmd = [
            "python", f"{TUTORIALROOT}/share/tut_detsim.py",
            "--evtmax", evtmax,
            "--anamgr-normal-hit",
            "--start-evtid", start_evtid,
            "--seed", str(seed),
            "--output", output_file,
            "--user-output", user_output_file,
            "--anamgr-edm",
            "gun",
            "--particles", particles,
            "--positions", *positions[j],
            "--momentums", *momentums[j],
            
        ]

        print(f"[{i}/{N[j]}] Running with seed={seed}")
        subprocess.run(cmd)

