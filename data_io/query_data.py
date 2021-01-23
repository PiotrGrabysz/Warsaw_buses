import os

import json
import pandas as pd


def load_timetable(f_path: str):

    with open(f_path) as file:
        data = json.load(file)

    # I create empty data frame which I append rows to
    df = pd.DataFrame()
    for row in data:
        vals = []
        keys = []
        for d in row["values"]:
            vals.append(d["value"])
            keys.append(d["key"])
        row_series = pd.Series(vals, keys)
        df = df.append(row_series, ignore_index=True)
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--f_path", "-f", type=str, help="")
    args = parser.parse_args()
    df = load_timetable(args.f_path)

    print(df.head())
    print(df.tail())
