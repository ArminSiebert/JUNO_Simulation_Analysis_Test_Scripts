import subprocess
import os
import shutil
from lib.sim.validation import delete_failed_runs, move_excess_runs
from lib.sim.metadata import create_metadata_file


#Settings
dir_nm = "Simulation_Muon_J24" #has to be changed correctly!
elec_type = "_"+"det2elec"
rec_type = "_"+"det2elec2rec"
#rec_type = "_"+"det2rec"
TUTORIALROOT = os.environ["TUTORIALROOT"]
workspace = os.environ.get("WORKSPACE")

if workspace is None:
    raise RuntimeError("environment variable WORKSPACE is not set!")

input_dir_det = os.path.join(workspace, dir_nm, "detsim")
if not os.path.isdir(input_dir_det):
    raise RuntimeError(f"Input directory doesn't exist: {input_dir_det}")
print(f'{input_dir_det=}\n')
input_dir_elec = os.path.join(workspace, dir_nm, "det2elec")
if not os.path.isdir(input_dir_elec):
    raise RuntimeError(f"Input directory doesn't exist: {input_dir_elec}")
print(f'{input_dir_elec=}\n')
input_dir_rec = os.path.join(workspace, dir_nm, "elec2rec")
if not os.path.isdir(input_dir_rec):
    raise RuntimeError(f"Input directory doesn't exist: {input_dir_rec}")

if rec_type == "_det2rec":
    input_dir_rec = os.path.join(workspace, dir_nm, "det2rec")
    if not os.path.isdir(input_dir_rec):
        raise RuntimeError(f"Input directory doesn't exist: {input_dir_rec}")
    else:
        print(f'det2rec conversion => input_dir_rec is changed to {input_dir_rec}\n')
else:
    print(f"{rec_type} conversion {input_dir_rec=}\n")
     


# output_dir = os.path.join(workspace, dir_nm, f"{dir_nm}_{rec_type}_EvtLoader")
# os.makedirs(output_dir, exist_ok=True)
data_dir = os.path.join(workspace,"data","sim",f"{dir_nm}{rec_type}_EvtLoader")
os.makedirs(data_dir, exist_ok=True)

output_dir_det = os.path.join(data_dir, "det")
os.makedirs(output_dir_det, exist_ok=True)

if rec_type == "_det2elec2rec":
    output_dir_elec = os.path.join(data_dir, "elec")
    os.makedirs(output_dir_elec, exist_ok=True)

output_dir_rec = os.path.join(data_dir, "rec")
os.makedirs(output_dir_rec, exist_ok=True)

output_path_log = os.path.join(data_dir,"convert_log.txt")



def extract_basename(filename):
    name = filename.replace('_user', '')
    if name.endswith('.root'):
        name = name[:-5]
    seed_pos = name.find('seed')
    if seed_pos != -1:
        name = name[:seed_pos + len('seed')]
    return name

input_files_det_edm = [extract_basename(f) for f in os.listdir(input_dir_det) if f.endswith(".root") and "user" not in f]
input_files_det_usr = [extract_basename(f) for f in os.listdir(input_dir_det) if f.endswith(".root") and "user"  in f]
input_files_elec_edm = [extract_basename(f) for f in os.listdir(input_dir_elec) if f.endswith(".root") and "user" not in f]
input_files_elec_usr = [extract_basename(f) for f in os.listdir(input_dir_elec) if f.endswith(".root") and "user"  in f]
input_files_rec_edm = [extract_basename(f) for f in os.listdir(input_dir_rec) if f.endswith(".root") and "user" not in f]
input_files_rec_usr = [extract_basename(f) for f in os.listdir(input_dir_rec) if f.endswith(".root") and "user"  in f]

input_files_basenames = sorted(
    set(input_files_det_edm)
  & set(input_files_det_usr)
  & set(input_files_elec_edm)
  & set(input_files_elec_usr)
  & set(input_files_rec_edm)
  & set(input_files_rec_usr))


with open(output_path_log, "w") as f:
        f.write(f'Conversion Log of {dir_nm} to {dir_nm}{rec_type}_EvtLoader'+"\n")
        f.write("\n")

error_count = 0 

for i, basename in enumerate(input_files_basenames, start=1):
    print(f"[{i}/{len(input_files_basenames)}] doing conversion for {basename}") 

    #original path
    
    det_edm_src = os.path.join(input_dir_det, f"{basename}_det.root")
    det_usr_src = os.path.join(input_dir_det, f"{basename}_det_user.root")
    if rec_type == "_det2elec2rec":
        elec_edm_src = os.path.join(input_dir_elec, f"{basename}{elec_type}.root")
        elec_usr_src = os.path.join(input_dir_elec, f"{basename}{elec_type}_user.root")
    rec_edm_src = os.path.join(input_dir_rec, f"{basename}{rec_type}.root")
    rec_usr_src = os.path.join(input_dir_rec, f"{basename}{rec_type}_user.root")

    #destination path
    det_edm_dst = os.path.join(output_dir_det, f"det_edm_{i-1-error_count}.root")
    det_usr_dst = os.path.join(output_dir_det, f"det_usr_{i-1-error_count}.root")
    if rec_type == "_det2elec2rec":
        elec_edm_dst = os.path.join(output_dir_elec, f"elec_edm_{i-1-error_count}.root")
        elec_usr_dst = os.path.join(output_dir_elec, f"elec_usr_{i-1-error_count}.root")
    rec_edm_dst = os.path.join(output_dir_rec, f"rec_edm_{i-1-error_count}.root")
    rec_usr_dst = os.path.join(output_dir_rec, f"rec_usr_{i-1-error_count}.root")

    try:
        shutil.copy2(det_edm_src, det_edm_dst)
        shutil.copy2(det_usr_src, det_usr_dst)
        print('      det converted')
        if rec_type == "_det2elec2rec":
            shutil.copy2(elec_edm_src, elec_edm_dst)
            shutil.copy2(elec_usr_src, elec_usr_dst)
            print('      elec converted')
        shutil.copy2(rec_edm_src, rec_edm_dst)
        shutil.copy2(rec_usr_src, rec_usr_dst)
        print('      rec converted')

        with open(output_path_log, "a") as f:
            f.write(f"{basename} → Simulation Number {i-1-error_count} as {rec_type}\n")

    except Exception as e:
        error_count += 1
        with open(output_path_log, "a") as f:
            f.write(f"Error with {basename}: {e}\n")
        print("an error occured") 

with open(output_path_log, "a") as f:
            f.write(f"Run_num: {len(input_files_basenames)-error_count}\n")

#print('copy to data')

#shutil.copytree(output_dir, data_dir, dirs_exist_ok=True)
print('check simulation')
delete_failed_runs(f"{dir_nm}{rec_type}_EvtLoader", run_num=len(input_files_basenames)-error_count, deleting = False )
print('create metadata file')
create_metadata_file(f"{dir_nm}{rec_type}_EvtLoader")
