# import os
# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# import utils.job_submission as js

# workspace = os.environ.get("WORKSPACE")
# dir = os.path.join(workspace,"SimulationScripts")
# scripts = ["do_everything.py","DetSim.py","det2rec.py","det2elec.py","elec2rec.py","Analysis.py"]
# script = scripts[0]
# #script = "Analysis.py"
# script_path = os.path.join(workspace,"SimulationScripts",script)
# cmd = f"python {script}"
# run_num=1
# js.sub_job(dir,cmd,run_num)


import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils.job_submission as js

# --- Pfad zu deinem JUNO-Setup ---
# Falls nötig anpassen, aber so wie du ihn gepostet hast:
setup_script = "/storage/gpfs_data/juno/junofs/users/siebert/setupscript.sh"

workspace = os.environ.get("WORKSPACE")
dir = os.path.join(workspace, "SimulationScripts")

# Liste deiner Python-Jobs
scripts = [
    "do_everything.py",
    "DetSim.py",
    "det2rec.py",
    "det2elec.py",
    "elec2rec.py",
    "Analysis.py"
]

script = scripts[0]  # hier auswählen
script_path = os.path.join(dir, script)

# --- Kommando: Setup sourcen + Python starten ---
# bash -c sorgt dafür, dass beides in derselben Shell läuft
#cmd = f"bash -c 'source {setup_script} && python {script_path}'"
cmd = f"python {script_path}"
# Anzahl der Runs
run_num = 1

# Job absenden
js.sub_job(dir, cmd, run_num)