###################################################################################
# tdms_to_csv.py, KAIST TEMPERATURE DATA CONVERSION
# Converts the temperature channels of raw KAIST current-temp .tdms files into
# CSVs matching the data/publish-data/<dataset>/*.csv layout (plain numeric
# columns, one row per sample, one file per class label).
###################################################################################

import argparse
import pathlib

import pandas as pd
from nptdms import TdmsFile

RAW_DIR = pathlib.Path("../../data/raw_kaist/current-temp_tdms")
OUT_DIR = pathlib.Path("../../data/publish-data/kaist_temperature")


def extract_temperature_channels(tdms_path):
    """Return a DataFrame with one column per Temperature channel in the TDMS file."""
    tdms = TdmsFile.read(tdms_path)

    temp_channels = [
        channel
        for group in tdms.groups()
        for channel in group.channels()
        if channel.properties.get("DAC~Channel~Type") == "Temperature"
    ]
    if not temp_channels:
        raise ValueError(f"No temperature channels found in {tdms_path}")

    data = {i: channel[:] for i, channel in enumerate(temp_channels)}
    return pd.DataFrame(data)


def convert_file(tdms_path, out_dir):
    df = extract_temperature_channels(tdms_path)
    out_path = out_dir / f"{tdms_path.stem}.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path} ({df.shape[0]} rows, {df.shape[1]} columns)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        default=["0Nm_BPFI_03.tdms"],
        help="TDMS filenames (relative to raw dir) to convert",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in args.files:
        convert_file(RAW_DIR / name, OUT_DIR)
