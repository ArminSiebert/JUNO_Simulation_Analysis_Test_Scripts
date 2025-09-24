#Does the electronics simulation
#takes not user .root files in det2elec folder and performs simulation saves the files in elec2rec

import subprocess
import os
import random

#region JUNOSW
# # Pfad zu deinem Setupscript
# SETUP_SCRIPT = "/storage/gpfs_data/juno/junofs/users/siebert/setupscript.sh"

# # Befehl: sourcen und dann alle Umgebungsvariablen ausgeben
# cmd = f"source {SETUP_SCRIPT} && env"

# # Subprozess mit Bash starten
# proc = subprocess.Popen(
#     cmd,
#     shell=True,
#     executable="/bin/bash",
#     stdout=subprocess.PIPE
# )

# # Alle Variablen aus subprocess in das aktuelle Python-Environment laden
# for line in proc.stdout:
#     key, _, value = line.decode("utf-8").partition("=")
#     os.environ[key] = value.strip()

# TUTORIALROOT = os.environ["TUTORIALROOT"]
# print(f'{TUTORIALROOT=}')      
#endregion

#Settings
dir_nm = "Simulation_Muon" #has to be changed correctly!
evtmax = "-1" #has to be checked


TUTORIALROOT = os.environ["TUTORIALROOT"]
print(f'{TUTORIALROOT=}')
workspace = os.environ.get("WORKSPACE")

if workspace is None:
    raise RuntimeError("environment variable WORKSPACE is not set!")

input_dir = os.path.join(workspace, dir_nm, "det2elec")
if not os.path.isdir(input_dir):
    raise RuntimeError(f"Input directory doesn't exist: {input_dir}")
output_dir = os.path.join(workspace, dir_nm, "elec2rec")
os.makedirs(output_dir, exist_ok=True)


input_files = [f for f in os.listdir(input_dir) if f.endswith(".root") and "user" not in f]

error_count = 0

for i, input_filename in enumerate(input_files, start=1):
    input_path = os.path.join(input_dir, input_filename)

    seed = random.randint(0, 32767)

    base, ext = os.path.splitext(input_filename)
    output_filename = f"{base}2rec{ext}"
    user_output_filename = f"{base}2rec_user{ext}"

    output_path = os.path.join(output_dir, output_filename)
    user_output_path = os.path.join(output_dir, user_output_filename)

    

    cmd = [
        "python", f"{TUTORIALROOT}/share/tut_rtraw2rec.py",  #tut_rtraw2rec.py or tut_elec2rec.py: No such file or directory
        "--evtmax", evtmax,
        "--input", input_path,
        #"--Algorithm omilrec",
        #"--seed", str(seed),
        "--output", output_path,
        "--user-output", user_output_path,
        "--EnableUserOutput",
        "--method", "energy-point" 
    ]

    print(f"[{i}/{len(input_files)}] Running elec2rec on {input_filename}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        error_count += 1
        print(f"[ERROR] det2elec failed on {input_filename}: {e}")
    except Exception as e:
        error_count += 1
        print(f"[EXCEPTION] Unexpected error on {input_filename}: {e}")

print(f"Done. Total errors: {error_count}")