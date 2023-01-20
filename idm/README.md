# iDM
**i**elastic **D**ark **M**atter

Credit to Stefania Gori from UCSC for original development of MadGraph5 Model
for [ArXiV:1804.00661](https://arxiv.org/abs/1804.00661).

## Set Up
Playing with this model requires a local copy of MadGraph5.
1. Download MG5 from [its launchpad](https://launchpad.net/mg5amcnlo).
2. Unpack it somewhere `tar xzvf MG5_aMC_v3.4.2.tar.gz && rm MG5_aMC_v3.4.2.tar.gz`
3. Symlink this directory into the `models` directory of MG5.
    - The name of the model to use with the `import model` command in MG5
      is the same as the name of the directory in `models`, for this README,
      I will assume that this model has been linked without changing its name.
4. Import the model into MG5 `MG5_aMC>import model --modelname idm`

## Brief MG/ME Primer
The general flow is
1. Define model (particles and interactions between particles): `import model <sub-dir-of-models>`
2. Use model to define diagrams (MadGraph - MG part): `generate` command
3. Output model into MadEvent (ME) code: `output` command
4. Run ME code to generate events and compute cross sections: 
   `launch` command or `./bin/generate_events` directly

