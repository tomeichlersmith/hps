# HPS General Notes

## June 15, 2022 hps-java Chat with PF

### Example run command
```bash
java \ # base java command
  -DdisableSvtAlignmentConstants \ # extra parameter PF is using for hist tracking work
  -Djna.library.path="/sdf/group/hps/users/bravo/src/GeneralBrokenLines/cpp/install/lib/" \ # allowing PF to use a C++ library within java
  -XX:+UseSerialGC \ # java argument - define type of Garbage Collector
  -Xmx6500m \ # java argument - set memory limit
  -jar /sdf/group/hps/users/pbutti/sw/hps-java/distribution/target/hps-distribution-5.1-SNAPSHOT-bin.jar \ # define compilation of hps-java to use
  \ # everything after the jar are inputs to the java "run manager"
  -R 10104 \ # run number, should match input 
  -d HPS_Nominal_iter19 \ # detector defining global->local conversion and conditions
  -D outputFile=data_events_aliRecon \ # parameter passted to steering file
  /sdf/group/hps/users/pbutti/run/alignmentDriver_gblplots_fee.lcsim \ # steering file
  -n 10000 \ # max number of events to process 
  -i /sdf/group/hps/data/physrun2019/hps_010104_slcio_pf/hps_010104_15.slcio # input file
```

### Vocab
- "driver" = "processor"

### Steering File
General outline is two parts: order of drivers and then definition of drivers
```xml
<lcsim xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" 
       xs:noNamespaceSchemaLocation="http://www.lcsim.org/schemas/lcsim/1.0/lcsim.xsd">
  <execute>
    <driver name="MyDriverInstance">
    <!-- other drivers in execute order -->
  </execute>
  <drivers>
    <driver name="MyDriverInstance" type="org.hps.full.class.spec.MyDriverClass">
      <myParameter>value</myParameter>
    </driver>
  </drivers>
</lcsim>
```
**Warning**: `myParameter` must have a matching `public void setMyParameter` in `MyDriverClass`
(Notice difference in capitalization of the first letter.)

## June 1, 2022 Analysis Meeting
Cameron Bravo

_Admin_ Poke Nathan for access to GitHub and maybe help JLab account move along.

Two Major Categories for 2016 Analysis
1. deciding on calibration and recon upgrades to use and run reco on full dataset
2. MC tools for simulating iDM signal

### iDM MC
- Need cards for MG for generating iDM (Philip/Natalia probably have these or close to them)

### Re-Recon 2016 Data
- Check on how updated calibrations affect reconstruction of 2016 data
- Update tracking algorithm
- Look at specific calibration style events

### Quality Analysis of Current Calibration
- `/sdf/group/hps/data/physrun2016/hps_007800` with reco and ntuples available
- 2.3GeV beam at 2016
- Looking for events with _clean_ one positron track and two electron tracks
- Sum their momenta, get ones where total energy is close to beam energy in peak
- Inspect these tracks and their vertices
  - chi^2 of fit
  - tan-lambda, phi, d0, z0, momentum 
- `AnaVertex` Processor in hpstr
  - Only looking for two tracks, one in each half
  - Make a copy of this and then make a "Trident" processor
  - WAB where one electron track, compared to energy in electron cluster in ECal 
- Matt G had Trident + Track Eff processors from ~2yrs ago to be updated
- selection
  - events with one positron and two electrons
  - tracks matched to clusters
  - look at E/p for these tracks

## May 3, 2022 Recon/Analysis Workshop

### SIMPs Analysis Sensitivity Calculation
Alic Spellman and Cameron Bravo

- MC? Technical how-to incoming from Alic...
- Lots of references to Cosmological SIMP paper
- Why not fold more of expected signal rate into MC e.g. using G4 weights?

### Vertex Analysis Ideas
Matt Solt <- not on HPS anymore
(recorded)

- Some can be implemented for 2016 data
- Kalman filter helps reduce track multiplicity (Cameron)
- Biasing of low-rate events _very_ necessary to reach higher lumi
- Simple ML algorithm seems to show improvement (Matts Thesis)
  - Used ggplot??
  - Systematic uncertainties are more difficult and simulation must be closer matched to data
  - Adversarial to prevent correlation with z since that is heavily depended on mixing parameter epsilon
- Mis-tracking issues require a rough isolation cut
  - Hit efficiency effects ==> improved pulse fitting
  - Tracking algo issues ==> Kalman filter will fix
- _Ignored upgraded detector corresponding to 2019+ data sets_
- e+e- systematic is dominated by WAB uncertainties
  - difficult (Cameron) - Natalia attempted to dig into MG and gave up
- deeper study into analysis cut systematics (currently very conservative)
  - dominated by target position uncertainty (+/- 0.5mm) 
- Optimum Interval Method (OIM)
  - conservative and penalizes number of intervals it searches
- Method we combine L1L1 and L1L2 regions

### Offline Slack Convos
- [x] Need JLab account to access data
  - https://confluence.slac.stanford.edu/display/hpsg/JLAB+registration+and+obtaining+a+JLAB+account
- [x] Omar gave me access to HPS SLAC area on SDF
  - `/sdf/group/hps/`

#### Cameron SW Notes
In principle we have all this documented in [hps-mc](https://github.com/JeffersonLab/hps-mc)

- [does the whole MC chain up to recon for main bkgd](https://github.com/JeffersonLab/hps-mc/blob/master/python/jobs/tritrig_job.py)
- [an example of how to use it in the hps-ms workflow](https://github.com/JeffersonLab/hps-mc/tree/master/examples/tritrig)
- [if you want to do data here is a good example to get you started](https://github.com/JeffersonLab/hps-mc/tree/master/examples/data_cnv)
- [an example of ntuplizing the recon and running an analysis](https://github.com/JeffersonLab/hps-mc/tree/master/examples/hpstr)

all these things can be mixed and matched however you want

it is written in a pretty general way so people can pretty easily spin up jobs that run all of the stuff they want together

it also has different paths to get the same jobs to run on different sorts of systems

## March 16, 2022
Omar, Tim, Jeremy, Me

### Admin Details
What admin details need to be done to get started? i.e. Do I need to email folks? Has Tim gotten the go-ahead from the HPS collab?

- HPS has an Executive Committee (EC) which meets to decide on policy
- Meeting on Monday (March 14) between Tim and EC - different concerns that need to be addressed
- Dissertation analysis on HPS without direct supervisor on HPS precedent set by Omar
- Need a de facto supervisor that _is_ on HPS (Jon Jaros for Omar, Tim has taken on this responsibility for me)
- Bylaws require certain minimums for being a member
  - Performance of some kind of service work (explicit in bylaws)
  - Taking shifts (implicit) doesnt make sense now given HPS wont take data for awhile, EC agrees this wont be much of a problem
- Tim POV: obvious synergy between service and necessary tools for analysis
- More discussion in future about what service work would be necessary
  - Some may relate to analysis, some may be separate
- Process by which someone becomes a member
  - Supervisor applies for membership listing potential service tasks and potential thesis topic
- Jeremy can observe and provide feedback on my work? Not a problem (even with non-public data).
- Formally speaking, I am not listed as HPS student with DOE, so need to maintain a plausible 50% time maximum for work on HPS.
  - EC would like more focus on HPS during actual dissertation research.
- UCSC had money for ops on HPS but no research, so SLAC was paying for Omar via UCSC
  - PI (Alex ?Gridlow)and sub-PI named at UCSC
- Plan B is to actually try to get separate funding to avoid interference with DOE
  - either through folks on HPS at SLAC or through external/UMN fellowship (Doctoral Dissertation Fellowship - DDF) 

### Analysis Options
Which analysis should I focus on?

- Fewer options when focused on shorter/tighter analyses
- Four data sets (2 engineering 2015 and 2016, 2 physics 2019 and 2021)
  - Engineering are lower statistics
  - Physics are still in process of calibration (difficult)
- Analyses using newer data sets are more exciting for HPS but uncertain time scale
- 2016 data has some interesting reach for SIMPs and Inelastic DM (IDM)
  - Slightly different signature than dark photon in LDMX
  - Mediator in HPS decays back to SM leptons after taking most of the energy
  - Decay products make mass peak and displaced vertex
  - SIMPs and IDM create a dark state _as well_ as the visible decay products
    - more complex analysis
  - Minimal dark photon search on 2016 already done
  - 2016 well calibrated and understood, ready for developing new analysis
  - One student already working on SIMPs (Alex Bellman at UCSC)
  - I could work on IDM
- Workflow 
  - Understand model space with Philip and Natalia
  - Develop MadGraph cards for that model space
  - Put LHE files through detector sim
  - Understand acceptance of detector there
  - Look for selections that fit this space
  - No novel reconstruction needed
- Downside of 2016 Analysis
  - Service work with MC and analysis techniques
  - HPS need most help with calib/recon of newer data (Tracking fibers and Lead Tungstate crystals)
- Application for Membership to EC
  - My analysis is X
  - My service work is Y
  - EC discusses with advisor(s) and student to nail down details
- Any construction of priority list would be _very_ helpful
  - MC, Reco/Calib, and Analysis coordinators poking

### HPS SW Chat
Delayed for next time...
