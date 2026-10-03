import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 IPL Analytics & Performance Dashboard")

st.markdown(
    """
    **Interactive IPL analysis using Python, Pandas, Plotly and Streamlit**

    Explore team performance, player statistics, match trends,
    toss decisions and historical IPL data.
    """
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent

    matches_path = base_dir / "data" / "processed" / "matches_c.csv"
    deliveries_path = base_dir / "data" / "processed" / "deliveries_c.csv"

    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)

    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")

    return matches, deliveries
matches, deliveries = load_data()
# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("🔎 Filters")

seasons = sorted(matches["season"].dropna().unique())

selected_season = st.sidebar.selectbox(
    "Select Season",
    ["All"] + [str(s) for s in seasons]
)

teams = sorted(
    set(matches["team1"].dropna().unique())
    | set(matches["team2"].dropna().unique())
)

selected_team = st.sidebar.selectbox(
    "Select Team",
    ["All"] + teams
)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_matches = matches.copy()

if selected_season != "All":
    filtered_matches = filtered_matches[
        filtered_matches["season"].astype(str) == selected_season
    ]

if selected_team != "All":
    filtered_matches = filtered_matches[
        (filtered_matches["team1"] == selected_team)
        | (filtered_matches["team2"] == selected_team)
    ]

filtered_match_ids = filtered_matches["id"].tolist()

filtered_deliveries = deliveries[
    deliveries["match_id"].isin(filtered_match_ids)
]

# ---------------------------------------------------
# KPI METRICS
# ---------------------------------------------------

total_matches = len(filtered_matches)

total_teams = len(
    set(filtered_matches["team1"].dropna().unique())
    | set(filtered_matches["team2"].dropna().unique())
)

total_players = len(
    set(filtered_deliveries["batter"].dropna().unique())
    | set(filtered_deliveries["bowler"].dropna().unique())
)

total_runs = int(filtered_deliveries["total_runs"].sum())

total_wickets = int(filtered_deliveries["is_wicket"].sum())

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("🏏 Matches", f"{total_matches:,}")
col2.metric("👥 Teams", f"{total_teams:,}")
col3.metric("🧑 Players", f"{total_players:,}")
col4.metric("🏃 Runs", f"{total_runs:,}")
col5.metric("🎯 Wickets", f"{total_wickets:,}")

st.divider()

# ---------------------------------------------------
# DASHBOARD CHARTS
# ---------------------------------------------------

# =========================
# ROW 1
# =========================

col1, col2 = st.columns(2)

# ---------------------------------------------------
# MATCHES BY SEASON
# ---------------------------------------------------

with col1:

    st.subheader("📅 Matches by Season")

    season_matches = (
        filtered_matches
        .groupby("season")
        .size()
        .reset_index(name="matches")
    )

    fig_season = px.bar(
        season_matches,
        x="season",
        y="matches",
        title="Number of Matches by Season",
        labels={
            "season": "Season",
            "matches": "Matches"
        }
    )

    fig_season.update_layout(
        xaxis=dict(type="category"),
        height=400
    )

    st.plotly_chart(
        fig_season,
        use_container_width=True
    )


# ---------------------------------------------------
# TEAM WINS
# ---------------------------------------------------

with col2:

    st.subheader("🏆 Team Wins")

    team_wins = (
        filtered_matches["winner"]
        .dropna()
        .value_counts()
        .reset_index()
    )

    team_wins.columns = ["Team", "Wins"]

    fig_wins = px.bar(
        team_wins.head(10),
        x="Wins",
        y="Team",
        orientation="h",
        title="Top 10 Teams by Wins"
    )

    fig_wins.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_wins,
        use_container_width=True
    )


# =========================
# ROW 2
# =========================

col1, col2 = st.columns(2)


# ---------------------------------------------------
# TOP RUN SCORERS
# ---------------------------------------------------

with col1:

    st.subheader("🏏 Top Run Scorers")

    top_batters = (
        filtered_deliveries
        .groupby("batter")["batsman_runs"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    top_batters.columns = ["Player", "Runs"]

    fig_batting = px.bar(
        top_batters,
        x="Runs",
        y="Player",
        orientation="h",
        title="Top 10 Run Scorers"
    )

    fig_batting.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_batting,
        use_container_width=True
    )


# ---------------------------------------------------
# TOP WICKET TAKERS
# ---------------------------------------------------

with col2:

    st.subheader("🎯 Top Wicket Takers")

    bowler_wickets = filtered_deliveries[
        (filtered_deliveries["is_wicket"] == 1)
        & (~filtered_deliveries["dismissal_kind"].isin([
            "run out",
            "retired hurt",
            "obstructing the field"
        ]))
    ]

    top_bowlers = (
        bowler_wickets
        .groupby("bowler")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="Wickets")
    )

    top_bowlers.columns = ["Player", "Wickets"]

    fig_bowling = px.bar(
        top_bowlers,
        x="Wickets",
        y="Player",
        orientation="h",
        title="Top 10 Wicket Takers"
    )

    fig_bowling.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_bowling,
        use_container_width=True
    )


# =========================
# ROW 3
# =========================

col1, col2 = st.columns(2)


# ---------------------------------------------------
# TOSS DECISION
# ---------------------------------------------------

with col1:

    st.subheader("🪙 Toss Decision Analysis")

    toss_data = (
        filtered_matches["toss_decision"]
        .value_counts()
        .reset_index()
    )

    toss_data.columns = ["Decision", "Count"]

    fig_toss = px.pie(
        toss_data,
        names="Decision",
        values="Count",
        title="Toss Decision Distribution"
    )

    fig_toss.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_toss,
        use_container_width=True
    )


# ---------------------------------------------------
# TOSS WINNER VS MATCH WINNER
# ---------------------------------------------------

with col2:

    st.subheader("🪙 Toss Winner vs Match Winner")

    toss_match = filtered_matches.dropna(
        subset=["toss_winner", "winner"]
    ).copy()

    toss_match["toss_won_match"] = (
        toss_match["toss_winner"]
        == toss_match["winner"]
    )

    toss_success = (
        toss_match["toss_won_match"]
        .value_counts()
        .reset_index()
    )

    toss_success.columns = ["Result", "Count"]

    toss_success["Result"] = toss_success["Result"].map({
        True: "Toss Winner Also Won",
        False: "Toss Winner Lost"
    })

    fig_toss_success = px.pie(
        toss_success,
        names="Result",
        values="Count",
        title="Does Toss Winner Win the Match?"
    )

    fig_toss_success.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_toss_success,
        use_container_width=True
    )
# ---------------------------------------------------
# PLAYER PERFORMANCE
# ---------------------------------------------------

st.subheader("👤 Player Performance")

players = sorted(
    filtered_deliveries["batter"]
    .dropna()
    .unique()
)

if players:

    selected_player = st.selectbox(
        "Select Player",
        players
    )

    player_data = filtered_deliveries[
        filtered_deliveries["batter"] == selected_player
    ]

    player_runs = int(player_data["batsman_runs"].sum())

    player_balls = len(player_data)

    player_fours = int(
        (player_data["batsman_runs"] == 4).sum()
    )

    player_sixes = int(
        (player_data["batsman_runs"] == 6).sum()
    )

    strike_rate = (
        (player_runs / player_balls) * 100
        if player_balls > 0 else 0
    )

    p1, p2, p3, p4, p5 = st.columns(5)

    p1.metric("Runs", player_runs)
    p2.metric("Balls", player_balls)
    p3.metric("4s", player_fours)
    p4.metric("6s", player_sixes)
    p5.metric("Strike Rate", f"{strike_rate:.2f}")

# ---------------------------------------------------
# KEY INSIGHTS
# ---------------------------------------------------

st.divider()

st.subheader("💡 Key Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:

    # Most successful team
    if not team_wins.empty:
        top_team = team_wins.iloc[0]["Team"]
        top_team_wins = int(team_wins.iloc[0]["Wins"])

        st.info(
            f"🏆 **Most Successful Team:** {top_team} "
            f"with {top_team_wins:,} wins in the selected data."
        )

    # Top run scorer
    if not top_batters.empty:
        top_batter = top_batters.iloc[0]["Player"]
        top_runs = int(top_batters.iloc[0]["Runs"])

        st.info(
            f"🏏 **Top Run Scorer:** {top_batter} "
            f"with {top_runs:,} runs in the selected data."
        )


with insight_col2:

    # Top wicket taker
    if not top_bowlers.empty:
        top_bowler = top_bowlers.iloc[0]["Player"]
        top_wickets = int(top_bowlers.iloc[0]["Wickets"])

        st.info(
            f"🎯 **Top Wicket Taker:** {top_bowler} "
            f"with {top_wickets:,} wickets in the selected data."
        )

    # Most common toss decision
    if not toss_data.empty:
        common_toss = toss_data.iloc[0]["Decision"]
        toss_count = int(toss_data.iloc[0]["Count"])

        st.info(
            f"🪙 **Most Common Toss Decision:** {common_toss} "
            f"({toss_count:,} matches)."
        )
# ---------------------------------------------------
# DATA PREVIEW
# ---------------------------------------------------

st.subheader("📊 Match Data Preview")

st.dataframe(
    filtered_matches.head(20),
    use_container_width=True
)
# ---------------------------------------------------
# ABOUT PROJECT
# ---------------------------------------------------

st.divider()

st.subheader("📌 About This Project")

st.markdown(
    """
    This dashboard analyzes historical IPL match and ball-by-ball data
    to identify trends in team performance, player statistics and match outcomes.

    ### 🔧 Technologies Used
    - Python
    - Pandas
    - Plotly
    - Streamlit
    - Data Cleaning
    - Exploratory Data Analysis (EDA)
    - Data Visualization

    ### 📊 Analysis Covered
    - Match trends by season
    - Team win analysis
    - Top run scorers
    - Top wicket takers
    - Toss decision analysis
    - Toss winner vs match winner
    - Individual player performance
    """
)
