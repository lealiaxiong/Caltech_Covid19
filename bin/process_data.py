import argparse

import os

import pandas as pd
import datetime

# WHO declares pandemic
START_DATE = datetime.date(2020, 3, 11)
# Start on a Sunday
START_DATE -= datetime.timedelta(days=START_DATE.weekday()) + datetime.timedelta(days=1)


def sum_by_week(df: pd.DataFrame, outdir: str):
    """Sums data by week resulting in DataFrame of affiliations and weekly totals. Saves to CSV."""

    # Shift dates back by 7 days because of how the weekly grouping works
    df_copy = df.copy()
    df_copy["date"] = df_copy["date"] - pd.to_timedelta(7, unit="d")

    # Group by affiliation and week and sum
    df_weekly_sum = (
        df_copy.groupby(["affiliation", pd.Grouper(key="date", freq="W")])["case"]
        .sum()
        .reset_index()
        .sort_values("date")
        .rename(columns={"date": "week of", "case": "total cases"})
    )

    # Save to CSV
    df_weekly_sum.to_csv(
        os.path.join(outdir, "caltech_covid_cases_weekly.csv"), index=False
    )


def calculate_rolling_avg(df, outdir):
    """Calculates 7-day rolling average for the whole Caltech community"""

    # Date of last update
    end_date = df.iloc[-1]["date"].to_pydatetime()

    df_all_groups = df.groupby("date")["case"].sum().reset_index()

    # Convert to datetime and set as index
    df_all_groups.set_index("date", inplace=True)

    # Reindex to include all dates, filling missing dates with 0
    df_all_groups = df_all_groups.reindex(
        pd.date_range(start=START_DATE, end=end_date, freq="D"), fill_value=0
    )

    # Calculate 7-day rolling average
    df_total_rolling = df_all_groups.rolling(window=7).mean().reset_index(names="date")

    # Save to CSV
    df_total_rolling.to_csv(
        os.path.join(outdir, "caltech_covid_cases_7_day_avg.csv"), index=False
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Process raw caltech_covid_cases data to produce weekly total by affiliation 
        and total community 7-day rolling average.
        """
    )
    parser.add_argument(
        "raw_data",
        type=str,
        help="Path to CSV containing raw Caltech COVID data by date and affiliation.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to directory where output files should be placed.",
        default="../data",
        required=False,
    )
    args = parser.parse_args()

    # Read in raw data
    print(f"Reading in {args.raw_data}...")
    df = pd.read_csv(args.raw_data).astype({"date": "datetime64[ns]"})

    # Create output directory if needed
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    # Process
    print(f"Preparing weekly totals...")
    sum_by_week(df, args.output_dir)
    print("Preparing 7-day rolling average...")
    calculate_rolling_avg(df, args.output_dir)

    print("Done!")
