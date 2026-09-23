"""
Player performance scoring for the IPL deliveries dataset.

Builds normalised batting, bowling and all-rounder scores from
ball-by-ball data. All three build_* functions take the cleaned
deliveries dataframe and return one row per player.
"""

import pandas as pd


def _minmax_norm(series: pd.Series) -> pd.Series:
    """Min-max normalise a series to the 0-1 range."""
    return (series - series.min()) / (series.max() - series.min())


def build_batting_stats(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs, balls faced, strike rate and a 0-1 batting_score per batter.

    batting_score = 0.6 * normalised runs + 0.4 * normalised strike rate
    """
    batsman = deliveries_df.groupby("batter").agg(
        runs=("batsman_runs", "sum"),
        balls=("ball", "count"),
    )
    batsman["strike_rate"] = (batsman["runs"] / batsman["balls"]) * 100

    batsman["runs_norm"] = _minmax_norm(batsman["runs"])
    batsman["sr_norm"] = _minmax_norm(batsman["strike_rate"])
    batsman["batting_score"] = 0.6 * batsman["runs_norm"] + 0.4 * batsman["sr_norm"]

    return batsman


def build_bowling_stats(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Wickets, overs, economy and a 0-1 bowling_score per bowler.

    bowling_score = 0.7 * normalised economy (inverted, lower is better)
                  + 0.3 * normalised overs bowled
    """
    wickets = (
        deliveries_df[deliveries_df["is_wicket"] == 1]
        .groupby("bowler")
        .agg(wickets=("is_wicket", "count"))
    )

    balls_bowled = deliveries_df.groupby("bowler").size()
    runs_conceded = deliveries_df.groupby("bowler")["total_runs"].sum()

    bowler = pd.DataFrame({"balls": balls_bowled, "runs_conceded": runs_conceded})
    bowler["overs"] = bowler["balls"] / 6
    bowler["economy"] = bowler["runs_conceded"] / bowler["overs"]
    bowler = bowler.join(wickets["wickets"]).fillna({"wickets": 0})

    bowler["wickets_norm"] = _minmax_norm(bowler["wickets"])
    # Lower economy is better, so invert the normalisation.
    bowler["econ_norm"] = (bowler["economy"].max() - bowler["economy"]) / (
        bowler["economy"].max() - bowler["economy"].min()
    )
    bowler["bowling_score"] = 0.7 * bowler["econ_norm"] + 0.3 * _minmax_norm(bowler["overs"])

    return bowler


def build_all_rounder_stats(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combines batting and bowling stats into a single all-rounder table.

    ar_score = 0.5 * batting_score + 0.5 * bowling_score
    """
    batsman = build_batting_stats(deliveries_df)
    bowler = build_bowling_stats(deliveries_df)

    all_rounders = batsman.merge(bowler, left_index=True, right_index=True)
    all_rounders["ar_score"] = (
        0.5 * all_rounders["batting_score"] + 0.5 * all_rounders["bowling_score"]
    )

    return all_rounders


def top_n(df: pd.DataFrame, score_col: str, n: int = 10) -> pd.DataFrame:
    """Convenience helper: top-n rows by a given score column, sorted descending."""
    return df.sort_values(score_col, ascending=False).head(n)
