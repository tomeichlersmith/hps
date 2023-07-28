from hpsmc.tools import JobManager
job.description = 'readout reco from a slic sim (post filter_bunches)'
job.add([
  JobManager(steering='readout'),
  JobManager(steering='recon')
])
