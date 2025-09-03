"""
The parameter paths to access data in the simulation files.
"""

__all__ = ["PAR_PTHS"]

import ctypes

import ROOT as R
import numpy as np


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


def _id2copyNo(pmt_ids):
    pmt_ids = np.array(pmt_ids, dtype=np.uint32)
    copy_nos = np.zeros(len(pmt_ids), dtype=np.int32)
    pmt_ids_ptr = pmt_ids.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
    copy_nos_ptr = copy_nos.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
    R.Ids2CopyNos(pmt_ids_ptr, len(pmt_ids), copy_nos_ptr)
    return copy_nos


PAR_PTHS = [
    {
        "par_nm":       "pos",
        "evt_type":     "phys",
        "file_type":    "usr",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "geninfo": lambda tree: (tree.InitX, tree.InitY, tree.InitZ)
        }
    },
    {
        "par_nm":       "mom",
        "evt_type":     "phys",
        "file_type":    "usr",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "geninfo": lambda tree: (tree.InitPX, tree.InitPY, tree.InitPZ)
        }
    },
    {
        "par_nm":       "dep_e",
        "evt_type":     "phys",
        "file_type":    "usr",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "evt": lambda tree: tree.edep
        }
    },
    {
        "par_nm":       "pdg_ids",
        "evt_type":     "phys",
        "file_type":    "edm",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "Event/Sim/SimEvt": lambda tree: np.asarray([track.getPDGID() for track in tree.SimEvt.getTracksVec()])
        }
    },
    {
        "par_nm":       "track_ids",
        "evt_type":     "phys",
        "file_type":    "edm",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "Event/Sim/SimEvt": lambda tree: np.asarray([track.getTrackID() for track in tree.SimEvt.getTracksVec()])
        }
    },
    {
        "par_nm":       "hit_times",
        "evt_type":     "phys",
        "file_type":    "usr",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "evt": lambda tree: np.asarray(tree.hitTime)
        }
    },
    {
        "par_nm":       "hit_pmt_ids",
        "evt_type":     "phys",
        "file_type":    "usr",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "evt": lambda tree: np.asarray(tree.pmtID)
        }
    },
    {
        "par_nm":       "hit_track_ids",
        "evt_type":     "phys",
        "file_type":    "usr",
        "sim_part_nms": ["det"],
        "get_funcs": {
            "evt": lambda tree: np.asarray(tree.PETrackID)
        }
    },
    {
        "par_nm":       "trig_time",
        "evt_type":     "trig",
        "file_type":    "edm",
        "sim_part_nms": ["elec", "calib", "rec"],
        "get_funcs": {
            "Meta/navigator": lambda tree: tree.EvtNavigator.TimeStamp().GetNanoSec()
        }
    },
    {
        "par_nm":       "rec_hit_times",
        "evt_type":     "trig",
        "file_type":    "edm",
        "sim_part_nms": ["calib", "rec"],
        "get_funcs": {
            "Event/CdLpmtCalib/CdLpmtCalibEvt": lambda tree: np.asarray([calibPmtChannel.time() for calibPmtChannel in tree.CdLpmtCalibEvt.calibPMTCol()]),
            "Event/CdSpmtCalib/CdSpmtCalibEvt": lambda tree: np.asarray([calibPmtChannel.time() for calibPmtChannel in tree.CdSpmtCalibEvt.calibPMTCol()])
        }
    },
    {
        "par_nm":       "rec_hit_pmt_ids",
        "evt_type":     "trig",
        "file_type":    "edm",
        "sim_part_nms": ["calib", "rec"],
        "get_funcs": {
            "Event/CdLpmtCalib/CdLpmtCalibEvt": lambda tree: _id2copyNo([calibPmtChannel.pmtId() for calibPmtChannel in tree.CdLpmtCalibEvt.calibPMTCol()]),
            "Event/CdSpmtCalib/CdSpmtCalibEvt": lambda tree: _id2copyNo([calibPmtChannel.pmtId() for calibPmtChannel in tree.CdSpmtCalibEvt.calibPMTCol()])
        }
    },
    {
        "par_nm":       "rec_hit_charges",
        "evt_type":     "trig",
        "file_type":    "edm",
        "sim_part_nms": ["calib", "rec"],
        "get_funcs": {
            "Event/CdLpmtCalib/CdLpmtCalibEvt": lambda tree: np.asarray([calibPmtChannel.charge() for calibPmtChannel in tree.CdLpmtCalibEvt.calibPMTCol()]),
            "Event/CdSpmtCalib/CdSpmtCalibEvt": lambda tree: np.asarray([calibPmtChannel.charge() for calibPmtChannel in tree.CdSpmtCalibEvt.calibPMTCol()])
        }
    },
    {
        "par_nm":       "rec_pos",
        "evt_type":     "trig",
        "file_type":    "usr",
        "sim_part_nms": ["rec"],
        "get_funcs": {
            "TRec": lambda tree: (tree.recx, tree.recy, tree.recz)
        }
    },
    {
        "par_nm":       "rec_vis_e",
        "evt_type":     "trig",
        "file_type":    "usr",
        "sim_part_nms": ["rec"],
        "get_funcs": {
            "TRec": lambda tree: tree.m_QTEn
        }
    },
    {
        "par_nm":       "rec_chisq",
        "evt_type":     "trig",
        "file_type":    "edm",
        "sim_part_nms": ["rec"],
        "get_funcs": {
            "Event/CdVertexRec/CdVertexRecEvt": lambda tree: tree.CdVertexRecEvt.getVertex(0).chisq()
        }
    }
]
