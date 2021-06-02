# The setup-pd.py assumes that the data is available offline
# This should ensure a quick import into Jupyter.

import pandas as pd
import numpy as np


df_log = pd.read_csv(csv_log)
df_dataplane = pd.read_csv(csv_dataplane)
df_ip = pd.read_csv(csv_ip)
