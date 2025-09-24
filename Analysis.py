# Analysis Script
# mainly plots reconstructed hittimes of the files in elec2rec 

import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__))) #important for importing from utils

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
#proc.communicate()

#endregion
import ROOT as R
import ctypes
import numpy as np
import matplotlib.pyplot as plt
#from lib.analysis.tools import Hist, Graph, Scatter
from utils.ana_tools import Hist
#from lib.analysis import hit_time_utils as htu
from utils import hit_time_utils as htu
#from lib.plotting.tools import Plot, ColorIterator
from utils.plot_tools import Plot, ColorIterator
#from lib.plotting.constants import *
from utils.plot_constants import *





#Settings
dir_nm = "Simulation_Muon" #has to be changed correctly!
TUTORIALROOT = os.environ["TUTORIALROOT"]

#region input and output
TUTORIALROOT = os.environ["TUTORIALROOT"]
workspace = os.environ.get("WORKSPACE")

if workspace is None:
    raise RuntimeError("Umgebungsvariable WORKSPACE ist nicht gesetzt!")

input_dir_det = os.path.join(workspace, dir_nm, "detsim")
if not os.path.isdir(input_dir_det):
    raise RuntimeError(f"Input-Ordner existiert nicht: {input_dir_det}")


input_dir_elec2rec = os.path.join(workspace, dir_nm, "elec2rec")
if not os.path.isdir(input_dir_elec2rec):
    raise RuntimeError(f"Input-Ordner existiert nicht: {input_dir_elec2rec}")

input_dir_det2rec = os.path.join(workspace, dir_nm, "det2rec")
if not os.path.isdir(input_dir_det2rec):
    raise RuntimeError(f"Input-Ordner existiert nicht: {input_dir_det2rec}")

input_dirs = [input_dir_det,input_dir_elec2rec,input_dir_det2rec] 

output_dir_plots = os.path.join(workspace, dir_nm, "plots")
os.makedirs(output_dir_plots, exist_ok=True)

output_dir_analysis = os.path.join(workspace, dir_nm, "analysis")
os.makedirs(output_dir_analysis, exist_ok=True)


input_files_det = sorted([f for f in os.listdir(input_dir_det) if f.endswith(".root") and "user" not in f])
input_user_files_det = sorted([f for f in os.listdir(input_dir_det) if f.endswith(".root") and "user" in f])

input_files_elec2rec = sorted([f for f in os.listdir(input_dir_elec2rec) if f.endswith(".root") and "user" not in f])
input_user_files_elec2rec = sorted([f for f in os.listdir(input_dir_elec2rec) if f.endswith(".root") and "user" in f])

input_files_det2rec = sorted([f for f in os.listdir(input_dir_det2rec) if f.endswith(".root") and "user" not in f])
input_user_files_det2rec = sorted([f for f in os.listdir(input_dir_det2rec) if f.endswith(".root") and "user" in f])

#endregion


#region functions
def plot_hittimes(hittimes,titel,plot_typ): 
    x_min, x_max = 0, 1000
    hist = Hist()
    hist.set_bins(x_max-x_min, x_min, x_max)
    hist.fill(hittimes)
    ### Plot histogram in plots 
    plt = Plot(figsize=(12, 8.11))
    plt.add(hist, color=MAIN_COLOR)
    plt.set_xlim(max(x_min, 1), x_max)
    plt.set_ylim(0, None)
    plt.set_xscale('log')
    plt.set_xlabel("t [ns]")
    plt.set_ylabel("Counts / ns")
    #plt.set_title(f'{titel}_{parts_out[6]}_{plot_typ}')
    output_path_plot= os.path.join(output_dir_plots, f"{output_filename_plot_base}_{plot_typ}.pdf")
    plt.savefig(output_path_plot) #, bbox_inches = "tight"

def get_hits(hit_times, hit_pmt_ids, pmt_typ):  #gets the hittimes for a pmt_typ 
    hit_times, hit_pmt_ids = htu.select_pmts(hit_times, hit_pmt_ids, pmt_typ=pmt_typ)
    mask = ~np.isnan(hit_times) & ~np.isnan(hit_pmt_ids)
    hit_times = hit_times[mask]
    hit_pmt_ids = hit_pmt_ids[mask]
    return hit_times, hit_pmt_ids
#endregion


#region ID Service Implemantation
R.gInterpreter.AddIncludePath("$JUNOTOP/junosw/Detector/Identifier")
R.gSystem.Load("libIdentifier.so")
R.gInterpreter.Declare("""
    #include "Identifier/Identifier.h"
    #include "Identifier/IDService.h"
    auto getIdServ() {
        auto idService = IDService::getIdServ();
        std::streambuf* oldCout = std::cout.rdbuf();
        std::ostringstream nullStream;
        std::cout.rdbuf(nullStream.rdbuf());
        idService->init();
        std::cout.rdbuf(oldCout);
        return idService;
    }
    auto idService = getIdServ();
    void Ids2CopyNos(unsigned int* pmtIds, int size, int* copyNos) {
        for (int i = 0; i < size; ++i) {
            Identifier id(pmtIds[i]);
            copyNos[i] = idService->id2CopyNo(id);
        }
    }
""")

def id2copyNo(pmt_ids):
    pmt_ids = np.array(pmt_ids, dtype=np.uint32)
    copy_nos = np.zeros(len(pmt_ids), dtype=np.int32)
    pmt_ids_ptr = pmt_ids.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
    copy_nos_ptr = copy_nos.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
    R.Ids2CopyNos(pmt_ids_ptr, len(pmt_ids), copy_nos_ptr)
    return copy_nos
#endregion

#Analysis Loop
for i, analysis_files in enumerate(zip(input_files_det,input_files_elec2rec,input_files_det2rec), start=1):
    basename = os.path.splitext(analysis_files[0])[0]  # without .root
    parts = basename.split("_")
    sim_nm = "_".join(parts[:6])
    print(f"[{i}/{len(input_files_elec2rec)}] doing analysis for {sim_nm}")
    
    titel = "_".join(parts[:3])  # e.g. e-_1
    
    parts[-1] = "analysis"
    output_filename_analysis = "_".join(parts) + ".txt"
    output_path_analysis = os.path.join(output_dir_analysis, output_filename_analysis)

    with open(output_path_analysis, "w") as f:
         f.write(f'Data of {titel}:'+"\n")
         f.write(f'{TUTORIALROOT=}'+"\n")
         f.write("\n")

    print(f'{TUTORIALROOT=}')

    #region Analysis in detsim 
    print(f'analysis of {analysis_files[0]}\n')
    with open(output_path_analysis, "a") as f:
        f.write(f'analysis of {analysis_files[0]}:\n')
        f.write(f'->\n')
    user_filename = f"{basename}_user.root"
    user_file_path = os.path.join(input_dirs[0], user_filename)
    with open(output_path_analysis, "a") as f:
        f.write(f'{user_file_path=}:\n')
    print(f'{user_file_path=}\n')
    parts_out = basename.split("_")
    output_filename_plot_base = "_".join(parts_out) + "_plot"

    user_file = R.TFile(user_file_path)
    evt = user_file.Get("evt")
    geninfo = user_file.Get("geninfo")
    evt.GetEntry(0)
    geninfo.GetEntry(0)
    hit_times = np.asarray(evt.hitTime)
    hit_pmt_ids = np.asarray(evt.pmtID)
    #pos = (geninfo.InitX[0], geninfo.InitY[0], geninfo.InitZ[0])
    pos = (evt.edepX, evt.edepY, evt.edepZ)
    with open(output_path_analysis, "a") as f:
        f.write(f"{pos=}\n")
    print(f"{pos=}")

    pmt_typs = ['spmt','lpmt']
    for pmt_typ in pmt_typs:
        try:
            hit_times_n, hit_pmt_ids_n = get_hits(hit_times,hit_pmt_ids,pmt_typ)
            hit_times_n = htu.correct_tof(hit_times_n, hit_pmt_ids_n, pos)
            hit_times_n, hit_pmt_ids_n = htu.remove_nan(hit_times_n, hit_pmt_ids_n)
            hit_times_n = htu.align(hit_times_n, prominence=20)
            
            with open(output_path_analysis, "a") as f:
                f.write(f"hit_times_{pmt_typ}[:10]:{hit_times_n[:10]}\n")
                f.write(f"hit_pmt_ids_{pmt_typ}[:10]:{hit_pmt_ids_n[:10]}\n\n")
            #print(f'{hit_times[:10]=}\n')
            plot_hittimes(hit_times_n,titel,f"hit_time_{pmt_typ}")
        except Exception as e:
            with open(output_path_analysis, "a") as f:
                f.write(f"Fehler {e} bei {pmt_typ}\n")
            print(f"Fehler {e} bei {pmt_typ}\n")
    user_file.Close()
    #endregion


    #region Analysis in reconstruction
    for j, rec_typ in enumerate(analysis_files[1:], start=1): #analysis for elec2rec and then for det2rec 
        print(f'analysis of {rec_typ}\n')
        with open(output_path_analysis, "a") as f:
            f.write(f'analysis of {rec_typ}:\n')
            f.write(f'->\n')

        file_path = os.path.join(input_dirs[j], rec_typ)
        print(f'{file_path=}\n')
        basenm = os.path.splitext(rec_typ)[0]
        user_filename = f"{basenm}_user.root"
        user_file_path = os.path.join(input_dirs[j], user_filename)
        print(f'{user_file_path=}\n')
        parts_out = basenm.split("_")
        output_filename_plot_base = "_".join(parts_out) + "_plot"

        
        
        #read date in rec file
        file = R.TFile(file_path)
        cdLpmtCalibEvt = file.Get("Event/CdLpmtCalib/CdLpmtCalibEvt")
        cdSpmtCalibEvt = file.Get("Event/CdSpmtCalib/CdSpmtCalibEvt")
        cdLpmtCalibEvt.GetEntry(0)
        cdSpmtCalibEvt.GetEntry(0)
        cdLpmtHitTimes = [calibPmtChannel.firstHitTime() for calibPmtChannel in cdLpmtCalibEvt.CdLpmtCalibEvt.calibPMTCol()] #maybe .time() and not .firstHitTime
        cdSpmtHitTimes = [calibPmtChannel.firstHitTime() for calibPmtChannel in cdSpmtCalibEvt.CdSpmtCalibEvt.calibPMTCol()]
        cdLpmtIds = [calibPmtChannel.pmtId() for calibPmtChannel in cdLpmtCalibEvt.CdLpmtCalibEvt.calibPMTCol()]
        cdSpmtIds = [calibPmtChannel.pmtId() for calibPmtChannel in cdSpmtCalibEvt.CdSpmtCalibEvt.calibPMTCol()]
        rec_hit_times_spmt = np.array(cdSpmtHitTimes) 
        rec_hit_times_lpmt = np.array(cdLpmtHitTimes)
        hit_pmt_ids_spmt = np.array(id2copyNo(cdSpmtIds))
        hit_pmt_ids_lpmt = np.array(id2copyNo(cdLpmtIds))
        file.Close()
        #read data in user file 
        user_file = R.TFile(user_file_path)
        tRec = user_file.Get("TRec")
        tRec.GetEntry(0)
        rec_pos = (tRec.recx, tRec.recy, tRec.recz)
        user_file.Close()
        with open(output_path_analysis, "a") as f:
            f.write(f"{rec_pos=}\n")
            f.write(f'before_tof {rec_hit_times_spmt[:10]=}\n')
            f.write(f'before_tof {rec_hit_times_lpmt[:10]=}\n')
        print(f"{rec_pos=}")


        #reconstructed hittime 
        rec_hit_times_spmt = htu.correct_tof(rec_hit_times_spmt, hit_pmt_ids_spmt, rec_pos)
        rec_hit_times_spmt, rec_hit_pmt_ids = htu.remove_nan(rec_hit_times_spmt, hit_pmt_ids_spmt)
        rec_hit_times_spmt = htu.align(rec_hit_times_spmt, prominence=20)
        with open(output_path_analysis, "a") as f:
            f.write(f'after_tof {rec_hit_times_spmt[:10]=}\n')
            f.write(f'{rec_hit_pmt_ids[:10]=}\n\n')   
        print(f'{rec_hit_times_spmt[:10]=}\n')
        plot_hittimes(rec_hit_times_spmt,titel,"rec_hit_time_spmt")

        rec_hit_times_lpmt = htu.correct_tof(rec_hit_times_lpmt, hit_pmt_ids_lpmt, rec_pos)
        rec_hit_times_lpmt, rec_hit_pmt_ids = htu.remove_nan(rec_hit_times_lpmt, hit_pmt_ids_lpmt)
        rec_hit_times_lpmt = htu.align(rec_hit_times_lpmt, prominence=20)
        with open(output_path_analysis, "a") as f:
            f.write(f'after_tof {rec_hit_times_lpmt[:10]=}\n')
            f.write(f'{rec_hit_pmt_ids[:10]=}\n\n')   
        print(f'{rec_hit_times_lpmt[:10]=}\n')
        plot_hittimes(rec_hit_times_lpmt,titel,"rec_hit_time_lpmt")
    #endregion
        

   