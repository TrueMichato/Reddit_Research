import csv
import pandas as pd
import pandasql
import duckdb

from defaults import *


df = pd.read_csv(FILEPATH, delimiter=",")