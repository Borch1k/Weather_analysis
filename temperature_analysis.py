
# stds = pd.read_pickle('stds.pkl')
# means = pd.read_pickle('means.pkl')

def compute_anomalies_on_chunk(chunk):
  import numpy as np
  import pandas as pd
  chunk, mean, std = chunk
  anomalies = np.argwhere(np.abs(chunk-mean) > std*2)
  np.savetxt('tests/'+str(np.random.randint(0,1000))+'.txt', anomalies)
  # return anomalies


def compute_anomalies_on_chunk_old(chunk):
  import numpy as np
  import pandas as pd
  chunk, mean, std = chunk
  anomalies = chunk[(np.abs(chunk['temperature']-mean) > std*2)].index
  return anomalies
