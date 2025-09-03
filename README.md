# Short Explanation: How to Use the Scripts

### The workflow is fully set up so that running do_everything.py will:
- Generate 3 muons,
- Perform two reconstruction paths: det2elec2rec and det2rec,
- Carry out a basic analysis afterwards.


## DetSim.py:
Configure the following variables:
- dir_nm: Target directory where all data will be stored in your workspace.
- N: A list where each entry specifies the number of particles with the same position and momentum.
- positions: A list of initial positions (in detector coordinates).
- momentums: A list of initial momenta.


## det2rec.py:(uses the tut_elec2rec.py script)
- Set dir_nm to the directory containing the DetSim output on which the reconstruction should be performed.


## det2elec.py: (uses the tut_det2elec.py script)
- Set dir_nm to the directory containing the DetSim output for which the electronics simulation should be performed.


## elec2rec.py: (uses the tut_rtraw2rec.py script)
- Set dir_nm to the directory containing the electronics simulation output on which the reconstruction should be performed.


## Analysis.py:
- Set dir_nm to the directory on which the analysis should be performed.

### This script generates:
#### A plots/ folder containing:
- Hit time plots after DetSim for LPMTs and SPMTs,
- First reconstructed hit time plots for LPMTs and SPMTs for both reconstruction paths 
- (6 plots per particle).

#### An analysis/ folder containing:
- One .txt file per particle,

Each file includes:
- Position, hit times, and PMT IDs for SPMTs and LPMTs after DetSim,
- Reconstructed position, hit times, and PMT IDs for both PMT types and both reconstruction paths.


## do_everything.py
- Running this script executes the full chain: simulation, reconstruction, and analysis.


## Important: Ensure that the correct dir_nm is set consistently in all scripts.
(Yes, this is currently a bit manual — sorry!)

## utils:
Contains Imports for better plotting and functions for better analysis
