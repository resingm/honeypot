# The setup-pd.py assumes that the data is available offline
# This should ensure a quick import into Jupyter.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

df_log = pd.read_csv(csv_log, parse_dates=['sync_ts', 'timestamp'])
df_log = df_log[df_log.origin_id != 2]
df_dataplane = pd.read_csv(csv_dataplane, parse_dates=['sync_ts', 'timestamp'])
df_ip = pd.read_csv(csv_ip)
