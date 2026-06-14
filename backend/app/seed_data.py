"""Curated, real decision moments for the Daily Call.

These are hand-built from well-known games so the app has rich content on day
one. Option keys: "a" / "b" / "c". `actual_call` is what the real coach did;
`best_call` is the call the analytics community generally favored. The
`scripts/pull_nfl.py` pipeline generates additional, data-sourced situations
straight from nflverse play-by-play.

Curated for demonstration — analytics framings are simplified for a fan audience.
"""
from __future__ import annotations

SEED_SITUATIONS: list[dict] = [
    # ---------------------------- NFL ----------------------------
    {
        "sport": "NFL",
        "season": 2021,
        "week": "Divisional Round",
        "game_id": "nfl_2021_div_BUF_vs_KC",
        "situation_description": (
            "Divisional Round. You just took the lead with 13 seconds left. "
            "Kicking off to Patrick Mahomes, who has all his timeouts. How do you kick it?"
        ),
        "option_a": "Kick it deep, normal kickoff",
        "option_b": "Squib / pooch kick to bleed the clock and limit the return",
        "option_c": None,
        "actual_call": "a",
        "best_call": "b",
        "outcome": (
            "Buffalo kicked deep. Mahomes drove into field-goal range in 13 seconds, "
            "tied it, and Kansas City won in overtime."
        ),
        "analytics_verdict": (
            "A squib kick burns clock and denies a clean return. Handing Mahomes the "
            "ball at his 25 with the clock stopped on the catch was the worst-case setup."
        ),
    },
    {
        "sport": "NFL",
        "season": 2016,
        "week": "Super Bowl LI",
        "game_id": "nfl_2016_sb_ATL_vs_NE",
        "situation_description": (
            "Super Bowl. You're up 28-20 late in the 4th, ball at the Patriots' 22 — "
            "already in field-goal range. A field goal makes it a two-score game. What do you do?"
        ),
        "option_a": "Run it, melt clock, kick the field goal",
        "option_b": "Drop back and pass to try for the dagger touchdown",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "Atlanta passed, took a sack and a holding penalty, fell out of field-goal "
            "range, and punted. New England completed the 28-3 comeback and won in OT."
        ),
        "analytics_verdict": (
            "Up eight in field-goal range, the clock is your friend. Running the ball "
            "guarantees points and drains time; dropping back invited the sack that "
            "swung the game."
        ),
    },
    {
        "sport": "NFL",
        "season": 2017,
        "week": "Super Bowl LII",
        "game_id": "nfl_2017_sb_PHI_vs_NE",
        "situation_description": (
            "Super Bowl, final seconds of the first half. 4th-and-goal at the 1. "
            "A field goal is automatic. Do you take the points or go for the touchdown?"
        ),
        "option_a": "Kick the easy field goal",
        "option_b": "Go for the touchdown",
        "option_c": None,
        "actual_call": "b",
        "best_call": "b",
        "outcome": (
            "Philadelphia ran the 'Philly Special' — a trick-play touchdown to Nick "
            "Foles — going up 22-12 at the half on the way to winning the title."
        ),
        "analytics_verdict": (
            "Against a juggernaut, points are precious and a yard is a coin flip in your "
            "favor. Going for seven instead of three was aggressive and correct."
        ),
    },
    {
        "sport": "NFL",
        "season": 2014,
        "week": "Super Bowl XLIX",
        "game_id": "nfl_2014_sb_SEA_vs_NE",
        "situation_description": (
            "Super Bowl, 26 seconds left, 2nd-and-goal at the 1, down 28-24, one timeout. "
            "Marshawn Lynch in the backfield. What's the call?"
        ),
        "option_a": "Hand it to Marshawn Lynch",
        "option_b": "Pass it",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "Seattle threw a slant. Malcolm Butler jumped it for an interception and "
            "New England won the Super Bowl."
        ),
        "analytics_verdict": (
            "There's a clock case for passing, but handing the ball to one of the best "
            "goal-line backs alive — with a timeout in your pocket — was the higher-"
            "percentage path to the title."
        ),
    },
    {
        "sport": "NFL",
        "season": 2023,
        "week": "NFC Championship",
        "game_id": "nfl_2023_nfcc_DET_vs_SF",
        "situation_description": (
            "NFC Championship, 4th quarter, up 24-17. 4th-and-3 at the 49ers' 28, "
            "comfortably in field-goal range with a good kicker. Do you go for it?"
        ),
        "option_a": "Kick the field goal to go up two scores",
        "option_b": "Go for it on 4th down",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "Detroit went for it and didn't convert. San Francisco rallied to win and "
            "reach the Super Bowl."
        ),
        "analytics_verdict": (
            "Aggression won Detroit a lot of games, but here a field goal makes it a "
            "two-score lead with a strong kicker. The model edge for going was thin — "
            "the points were the steadier play."
        ),
    },
    {
        "sport": "NFL",
        "season": 2009,
        "week": "Week 10",
        "game_id": "nfl_2009_wk10_NE_vs_IND",
        "situation_description": (
            "Up 34-28, 2:08 left, 4th-and-2 at your own 28 against Peyton Manning. "
            "Punt and trust your defense, or go for it to end the game?"
        ),
        "option_a": "Go for it",
        "option_b": "Punt",
        "option_c": None,
        "actual_call": "a",
        "best_call": "a",
        "outcome": (
            "New England went for it and came up short. Manning scored to win — but win-"
            "probability models sided with Belichick's decision to go."
        ),
        "analytics_verdict": (
            "Punting hands a red-hot Manning the ball and a clear path. Converting "
            "essentially ends it. The numbers backed going for it even though it failed."
        ),
    },
    # ---------------------------- NBA ----------------------------
    {
        "sport": "NBA",
        "season": 2013,
        "week": "Finals Game 6",
        "game_id": "nba_2013_finals_g6_SAS_vs_MIA",
        "situation_description": (
            "Finals, Game 6, up 5 with 28 seconds left. Free throws and a defensive "
            "rebound can clinch the title. Do you keep your dominant rebounder on the floor?"
        ),
        "option_a": "Keep Tim Duncan in for rebounding/defense",
        "option_b": "Go small for offense and switchability",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "San Antonio benched Duncan. Miami grabbed an offensive rebound, Ray Allen "
            "hit the corner three to force OT, and the Heat won Game 6 and the title."
        ),
        "analytics_verdict": (
            "Up five in the final seconds, the rebound is the ballgame. Taking your best "
            "rebounder off the floor to chase offense you may not even need was the gamble "
            "that cracked the door open."
        ),
    },
    {
        "sport": "NBA",
        "season": 2022,
        "week": "Strategy",
        "game_id": "nba_strat_down2_last_shot",
        "situation_description": (
            "Down 2, 6 seconds left, you have the ball and no timeouts. Drive for the tie "
            "and play for overtime, or pull up for the win?"
        ),
        "option_a": "Get a high-quality 2 to force overtime",
        "option_b": "Shoot the 3 to win it now",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "League-wide, teams that attack the rim for a tying two win at a higher rate "
            "than those settling for a contested game-winning three."
        ),
        "analytics_verdict": (
            "A clean two and a coin-flip overtime usually beats a low-percentage, "
            "contested three. Take the higher-quality shot unless the three is wide open."
        ),
    },
    {
        "sport": "NBA",
        "season": 2018,
        "week": "Strategy",
        "game_id": "nba_strat_foul_up3",
        "situation_description": (
            "Up 3, opponent inbounding with 5 seconds left and no timeouts for either side. "
            "Foul before they can shoot, or play tight defense and contest the three?"
        ),
        "option_a": "Foul immediately to prevent a tying three",
        "option_b": "Play straight-up defense and contest",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "Across the league, deliberately fouling up three in the final seconds lowers "
            "the opponent's chance of tying — they must make one, miss the second on "
            "purpose, rebound, and score again."
        ),
        "analytics_verdict": (
            "Fouling up three with the clock low is the percentage play: it removes the "
            "one thing that beats you — a tying triple — and forces a low-odds scramble."
        ),
    },
    {
        "sport": "NBA",
        "season": 2019,
        "week": "Strategy",
        "game_id": "nba_strat_2for1",
        "situation_description": (
            "End of the quarter, you have the ball with about 30 seconds on the clock. "
            "Shoot early to get the ball back for a last shot, or run the clock down?"
        ),
        "option_a": "Go '2-for-1' — shoot by ~25 seconds to guarantee another possession",
        "option_b": "Hold for one shot at the buzzer",
        "option_c": None,
        "actual_call": "b",
        "best_call": "a",
        "outcome": (
            "Playing 2-for-1 nets teams extra possessions over a season, and extra "
            "possessions are free points. Holding for one shot leaves value on the floor."
        ),
        "analytics_verdict": (
            "Two cracks at the basket beat one almost every time. Getting a shot up early "
            "to guarantee the last possession is a small edge that compounds all game."
        ),
    },
]
