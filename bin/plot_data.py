import argparse
import os
import datetime
import pandas as pd
import altair as alt

AFFILIATIONS_ORDERED = [
    "employees",
    "campus employees",
    "off-campus employees",
    "CCC employees",
    "external affiliates",
    "postdocs",
    "faculty",
    "students",
    "undergraduate students",
    "graduate students",
]
COLORS_ORDERED = [
    "#87aac0",
    "#4384b1",
    "#326386",
    "#1c374a",
    "#9e9e9e",
    "#b38c00",
    "#8a5500",
    "#e75a0d",
    "#f47e3e",
    "#ca6702",
]
CALTECH_AVG_COLOR = "#f2cc44"

PLOT_WIDTH = 664
PLOT_HEIGHT = 300


def plot_daily_cases(df: pd.DataFrame, df_rolling: pd.DataFrame, outdir: str):
    """
    Create daily cases chart with 90-day interval selection.
    Saves to JSON.
    """

    end_date = df.iloc[-1]["date"].to_pydatetime()

    # Create initial date range (last 90 days)
    date_range = (end_date - datetime.timedelta(days=90), end_date)

    # Create selection interval
    brush = alt.selection_interval(encodings=["x"], value={"x": date_range})

    # Base for upper bar chart
    upper_bars = (
        alt.Chart(df, width=PLOT_WIDTH, height=PLOT_HEIGHT)
        .mark_bar()
        .encode(
            x="date:T",
            y=alt.Y("case:Q").title("cases"),
            color=alt.Color(
                "affiliation:N",
                scale=alt.Scale(domain=AFFILIATIONS_ORDERED, range=COLORS_ORDERED),
            ).legend(orient="top-left"),
            tooltip=["affiliation", "case"],
        )
    )

    # Rolling average chart
    rolling_avg = (
        alt.Chart(df_rolling, width=PLOT_WIDTH, height=PLOT_HEIGHT)
        .mark_line(color=CALTECH_AVG_COLOR)
        .encode(x=alt.X("date:T"), y=alt.Y("case:Q").title(""))
    )

    # Create upper chart -- upper bars with rolling average, scaled to the selection interval
    upper = (upper_bars + rolling_avg).encode(alt.X("date:T").scale(domain=brush))

    # Base for lower bar chart
    lower_bars = (
        alt.Chart(df, width=PLOT_WIDTH, height=PLOT_HEIGHT)
        .mark_bar(color="grey", width=2)
        .encode(
            x="date:T",
            y=alt.Y("case:Q").title(""),
        )
    )

    # Create lower chart -- lower bars with rolling average, with the brush
    lower = (lower_bars + rolling_avg).properties(height=60).add_params(brush)

    # Combine upper and lower
    final = upper & lower

    # Save to JSON
    final.save(os.path.join(outdir, "daily_cases.json"))


def plot_weekly_cases(df_weekly: pd.DataFrame, outdir: str):
    """
    Create weekly cases chart with interval selection.
    Saves to JSON.
    """
    # Create selection interval
    brush = alt.selection_interval(encodings=["x"])

    upper_bars = (
        alt.Chart(df_weekly, width=PLOT_WIDTH, height=PLOT_HEIGHT)
        .mark_bar(width=4)
        .encode(
            x=alt.X("week of:T"),
            y=alt.Y("total cases:Q").title("weekly cases"),
            color=alt.Color(
                "affiliation:N",
                scale=alt.Scale(domain=AFFILIATIONS_ORDERED, range=COLORS_ORDERED),
            ).legend(orient="top-left"),
            tooltip=["week of", "affiliation", "total cases"],
        )
    )

    # Create upper chart -- upper bars with rolling average, scaled to the selection interval
    upper = (upper_bars).encode(alt.X("week of:T").scale(domain=brush).title("date"))

    # Base for lower bar chart
    lower_bars = (
        alt.Chart(df_weekly, width=PLOT_WIDTH, height=PLOT_HEIGHT)
        .mark_bar(color="grey")
        .encode(
            x=alt.X("week of:T").title("date"),
            y=alt.Y("total cases:Q").title(""),
        )
    )

    # Create lower chart -- lower bars with rolling average, with the brush
    lower = lower_bars.properties(height=60).add_params(brush)

    # Combine upper and lower
    final = upper & lower

    # Save to JSON
    final.save(os.path.join(outdir, "weekly_cases.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Create interactive plots of Caltech COVID cases by day and by week.
        """
    )
    parser.add_argument(
        "raw_data",
        type=str,
        help="Path to CSV containing raw Caltech COVID data by date and affiliation.",
    )
    parser.add_argument(
        "weekly_data",
        type=str,
        help="Path to CSV containing Caltech COVID data by week and affiliation.",
    )
    parser.add_argument(
        "rolling_avg_data",
        type=str,
        help="Path to CSV containing 7-day rolling average Caltech COVID data.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to directory where output files should be placed.",
        default="../",
        required=False,
    )
    args = parser.parse_args()

    # Read in data
    print(f"Reading in {args.raw_data}...")
    df = pd.read_csv(args.raw_data).astype({"date": "datetime64[ns]"})
    print(f"Reading in {args.weekly_data}...")
    df_weekly = pd.read_csv(args.weekly_data).astype({"week of": "datetime64[ns]"})
    print(f"Reading in {args.rolling_avg_data}...")
    df_rolling_avg = pd.read_csv(args.rolling_avg_data).astype(
        {"date": "datetime64[ns]"}
    )

    # Create output directory if needed
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    # Create plots
    print(f"Plotting daily cases...")
    plot_daily_cases(df, df_rolling_avg, args.output_dir)
    print("Plotting weekly cases...")
    plot_weekly_cases(df_weekly, args.output_dir)

    print("Done!")
