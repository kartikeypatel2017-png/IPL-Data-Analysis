"""
Cleaning utilities for the IPL matches and deliveries datasets.

These functions centralise the team-name, venue-name and null-value
fixes that used to be repeated inline in the cleaning notebook, so
they can be reused (and unit tested) instead of copy-pasted.
"""

import pandas as pd

# Franchises that have been renamed / rebranded over the years.
# Keys = old name in the raw data, values = current name.
TEAM_NAME_MAP = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
}

# Venue names that appear under several spellings/formats across seasons.
VENUE_NAME_MAP = {
    "Eden Gardens, Kolkata": "Eden Gardens",
    "Wankhede Stadium, Mumbai": "Wankhede Stadium",
    "MA Chidambaram Stadium, Chepauk, Chennai": "MA Chidambaram Stadium, Chepauk",
    "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "Arun Jaitley Stadium, Delhi": "Arun Jaitley Stadium",
    "Dr DY Patil Sports Academy, Mumbai": "Dr DY Patil Sports Academy",
    "Rajiv Gandhi International Stadium, Uppal": "Rajiv Gandhi International Stadium",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Rajiv Gandhi International Stadium",
    "Maharashtra Cricket Association Stadium, Pune": "Maharashtra Cricket Association Stadium",
    "Brabourne Stadium, Mumbai": "Brabourne Stadium",
    "M Chinnaswamy Stadium, Bengaluru": "M Chinnaswamy Stadium",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam": "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
    "Punjab Cricket Association IS Bindra Stadium, Mohali": "Punjab Cricket Association Stadium, Mohali",
    "Himachal Pradesh Cricket Association Stadium, Dharamsala": "Himachal Pradesh Cricket Association Stadium",
    "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium",
    "Sawai Mansingh Stadium, Jaipur": "Sawai Mansingh Stadium",
    "Punjab Cricket Association IS Bindra Stadium": "Punjab Cricket Association Stadium, Mohali",
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh": "Punjab Cricket Association Stadium, Mohali",
}


def clean_matches(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Standardise team/venue names, fix dtypes, and fill nulls in the matches table."""
    df = matches_df.copy()

    df["date"] = pd.to_datetime(df["date"])

    team_cols = ["team1", "team2", "toss_winner", "winner"]
    df[team_cols] = df[team_cols].replace(TEAM_NAME_MAP)

    df["venue"] = df["venue"].replace(VENUE_NAME_MAP)

    df["city"] = df["city"].fillna("unknown")
    df["method"] = df["method"].fillna("normal")

    return df


def clean_deliveries(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Standardise team names and fill event-related nulls in the deliveries table."""
    df = deliveries_df.copy()

    team_cols = ["batting_team", "bowling_team"]
    df[team_cols] = df[team_cols].replace(TEAM_NAME_MAP)

    df["extras_type"] = df["extras_type"].fillna("no extras")
    df["player_dismissed"] = df["player_dismissed"].fillna("Nan")
    df["dismissal_kind"] = df["dismissal_kind"].fillna("Nan")
    df["fielder"] = df["fielder"].fillna("Nan")

    return df
