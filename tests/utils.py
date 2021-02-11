from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import numpy as np

def modify_time_stamp(input_dir, output_dir, offset):
    
    data = pd.read_csv(input_dir, names=[""])