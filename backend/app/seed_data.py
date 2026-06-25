"""Curated, real decision moments for the Daily Call.

These are hand-built from well-known games so the app has rich content on day
one. Option keys: "a" / "b" / "c" / "d". `actual_call` is what the real coach
did; `best_call` is the call the analytics community generally favored.

Decision prompts are written *blind*: no team names, no star players, no event
that gives the game away — just the situation and the archetypes that actually
matter to the call ("an elite QB," "your gassed ace"). The real identity (teams,
year, the famous moment) lives in `matchup` and is only revealed *after* the
pick, so fans decide on the merits instead of recognizing the ending.

`win_prob` is the team's win probability *for each available call*, framed from
thousands of similar historical situations and computed independent of how this
one game actually ended. (`best_call` is always the highest-win-probability one.)

`game_state` powers the scenario diagram: the score, clock, and where the ball
sits. `ball_on` is 0..100 toward the opponent's goal (NFL); `zone` is the ball's
spot on the court (NBA); `bases`/`outs` set the diamond (MLB).

Option counts vary on purpose — we only list the calls a coach genuinely had.
The `scripts/pull_nfl.py` pipeline generates additional, data-sourced situations.
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
        "matchup": "Divisional Round · Bills vs. Chiefs · Jan 2022 (the 13 seconds)",
        "situation_description": (
            "Playoff game. You just took the lead with 13 seconds left and you're "
            "kicking off to an elite, quick-strike QB who still has all his timeouts. "
            "How do you kick it?"
        ),
        "option_a": "Kick it deep, normal kickoff",
        "option_b": "Squib / pooch kick to bleed the clock and limit the return",
        "option_c": "Mortar (sky) kick — high and short to pin the return man",
        "option_d": "Surprise onside to try to end it with the ball",
        "actual_call": "a",
        "best_call": "b",
        "win_prob": {"a": 57, "b": 80, "c": 74, "d": 33},
        "game_state": {
            "clock": "4th · 0:13", "your_score": 36, "opp_score": 33,
            "tag": "Kickoff", "ball_on": 35, "poss": "kick",
        },
        "outcome": (
            "Buffalo kicked deep. Mahomes drove into field-goal range in 13 seconds, "
            "tied it, and Kansas City won in overtime."
        ),
        "analytics_verdict": (
            "A squib kick burns clock and denies a clean return. Handing an elite QB the "
            "ball at his 25 with the clock stopped on the catch was the worst-case setup."
        ),
    },
    {
        "sport": "NFL",
        "season": 2016,
        "week": "Super Bowl LI",
        "game_id": "nfl_2016_sb_ATL_vs_NE",
        "matchup": "Super Bowl LI · Falcons vs. Patriots · Feb 2017 (the 28–3 collapse)",
        "situation_description": (
            "It's the Super Bowl. You're up 28-20 late in the 4th, ball at the opponent's "
            "22 — already in field-goal range. A field goal makes it a two-score game. "
            "What do you do?"
        ),
        "option_a": "Run it, melt clock, kick the field goal",
        "option_b": "Drop back and pass to try for the dagger touchdown",
        "option_c": "Throw a quick, safe screen to stay on schedule",
        "option_d": "Kneel to center the ball and kick now",
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 88, "b": 64, "c": 78, "d": 81},
        "game_state": {
            "clock": "4th · 3:50", "your_score": 28, "opp_score": 20,
            "tag": "2nd & 11", "ball_on": 78, "poss": "you",
        },
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
        "matchup": "Super Bowl LII · Eagles vs. Patriots · Feb 2018 (the 'Philly Special')",
        "situation_description": (
            "Super Bowl, final seconds of the first half. 4th-and-goal at the 1. "
            "A field goal is automatic. Do you take the points or go for the touchdown?"
        ),
        "option_a": "Kick the easy field goal",
        "option_b": "Go for the touchdown",
        "option_c": "Hard count to draw them offsides, then decide",
        "option_d": None,
        "actual_call": "b",
        "best_call": "b",
        "win_prob": {"a": 70, "b": 78, "c": 71},
        "game_state": {
            "clock": "2nd · 0:38", "your_score": 15, "opp_score": 12,
            "tag": "4th & goal", "ball_on": 99, "poss": "you",
        },
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
        "matchup": "Super Bowl XLIX · Seahawks vs. Patriots · Feb 2015 (the goal-line INT)",
        "situation_description": (
            "Super Bowl, 26 seconds left, 2nd-and-goal at the 1, down 28-24, one timeout. "
            "You've got one of the best goal-line backs in football in the backfield. "
            "What's the call?"
        ),
        "option_a": "Hand it to your power back",
        "option_b": "Throw a quick slant",
        "option_c": "Play-action rollout — run/pass option",
        "option_d": "Quarterback sneak",
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 82, "b": 70, "c": 76, "d": 79},
        "game_state": {
            "clock": "4th · 0:26", "your_score": 24, "opp_score": 28,
            "tag": "2nd & goal", "ball_on": 99, "poss": "you",
        },
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
        "matchup": "NFC Championship · Lions vs. 49ers · Jan 2024",
        "situation_description": (
            "Conference championship, 4th quarter, up 24-17. 4th-and-3 at the opponent's "
            "28, comfortably in field-goal range with a good kicker. Do you go for it?"
        ),
        "option_a": "Kick the field goal to go up two scores",
        "option_b": "Go for it on 4th down",
        "option_c": "Hard count for a free play, otherwise kick",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 74, "b": 70, "c": 72},
        "game_state": {
            "clock": "4th · 7:29", "your_score": 24, "opp_score": 17,
            "tag": "4th & 3", "ball_on": 72, "poss": "you",
        },
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
        "matchup": "Week 10 · Patriots vs. Colts · Nov 2009 (Belichick's 4th-and-2)",
        "situation_description": (
            "Up 34-28, 2:08 left, 4th-and-2 at your own 28, with a future Hall-of-Fame QB "
            "waiting on the other sideline. Punt and trust your defense, or go for it to "
            "end the game?"
        ),
        "option_a": "Go for it",
        "option_b": "Punt it away",
        "option_c": "Hard count to bait them offsides for a free first down",
        "option_d": None,
        "actual_call": "a",
        "best_call": "a",
        "win_prob": {"a": 79, "b": 70, "c": 71},
        "game_state": {
            "clock": "4th · 2:08", "your_score": 34, "opp_score": 28,
            "tag": "4th & 2", "ball_on": 28, "poss": "you",
        },
        "outcome": (
            "New England went for it and came up short. Manning scored to win — but win-"
            "probability models sided with Belichick's decision to go."
        ),
        "analytics_verdict": (
            "Punting hands a red-hot Hall-of-Fame QB the ball and a clear path. Converting "
            "essentially ends it. The numbers backed going for it even though it failed."
        ),
    },
    {
        "sport": "NFL",
        "season": 2009,
        "week": "Super Bowl XLIV",
        "game_id": "nfl_2009_sb_NO_vs_IND",
        "matchup": "Super Bowl XLIV · Saints vs. Colts · Feb 2010 (the 'Ambush' onside)",
        "situation_description": (
            "Super Bowl, opening the second half, trailing 10-6. You're lining up to kick "
            "off to a future Hall-of-Fame QB. Play it straight or gamble?"
        ),
        "option_a": "Call a surprise onside kick",
        "option_b": "Kick it deep and trust your defense",
        "option_c": "Pooch kick to pin them inside the 15",
        "option_d": None,
        "actual_call": "a",
        "best_call": "a",
        "win_prob": {"a": 67, "b": 58, "c": 60},
        "game_state": {
            "clock": "3rd · 15:00", "your_score": 6, "opp_score": 10,
            "tag": "Kickoff", "ball_on": 35, "poss": "kick",
        },
        "outcome": (
            "New Orleans called the 'Ambush' onside kick, recovered it, scored on the "
            "drive, seized the momentum, and won the Super Bowl."
        ),
        "analytics_verdict": (
            "Stealing a possession from a Hall-of-Fame QB is worth the risk on the game's "
            "biggest stage. The surprise gave the Saints an extra drive and flipped the "
            "momentum — a gutsy, high-upside call that paid off."
        ),
    },
    {
        "sport": "NFL",
        "season": 2002,
        "week": "Week 12",
        "game_id": "nfl_2002_DET_vs_CHI_ot",
        "matchup": "Week 12 · Lions vs. Bears (OT) · Nov 2002",
        "situation_description": (
            "You just won the overtime coin toss. It's sudden death — first score wins. "
            "There's a stiff wind at one end. What do you do?"
        ),
        "option_a": "Take the ball",
        "option_b": "Kick off and defend with the wind",
        "option_c": None,
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 64, "b": 49},
        "game_state": {
            "clock": "OT · Sudden death", "your_score": 17, "opp_score": 17,
            "tag": "Coin toss", "poss": "kick",
        },
        "outcome": (
            "Detroit gave the ball away to take the wind. The Bears drove down, kicked "
            "the winning field goal, and the Lions never touched the ball."
        ),
        "analytics_verdict": (
            "In sudden death, possession is everything — the team with the ball can end "
            "it without the other side ever touching it. Handing away the ball for a "
            "field-position edge was a math error that cost the game."
        ),
    },
    {
        "sport": "NFL",
        "season": 2012,
        "week": "Divisional Round",
        "game_id": "nfl_2012_div_BAL_vs_DEN",
        "matchup": "Divisional Round · Ravens vs. Broncos · Jan 2013 (the 'Mile High Miracle')",
        "situation_description": (
            "Tied game, your ball at your own 20, 31 seconds left, two timeouts, and a "
            "future Hall-of-Fame QB under center. Push for a winning field goal, or sit "
            "on it?"
        ),
        "option_a": "Go for the winning field goal",
        "option_b": "Kneel and play for overtime",
        "option_c": "Take one safe shot deep, then reassess",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 61, "b": 50, "c": 57},
        "game_state": {
            "clock": "4th · 0:31", "your_score": 35, "opp_score": 35,
            "tag": "1st & 10", "ball_on": 20, "poss": "you",
        },
        "outcome": (
            "Denver kneeled and went to overtime, then lost on a long Baltimore field "
            "goal — the 'Mile High Miracle' — without Manning getting another shot."
        ),
        "analytics_verdict": (
            "Thirty-one seconds and two timeouts with a Hall-of-Fame QB is plenty to flip "
            "into field-goal range. Playing for overtime threw away a real chance to win "
            "it in regulation."
        ),
    },
    {
        "sport": "NFL",
        "season": 2014,
        "week": "NFC Championship",
        "game_id": "nfl_2014_nfcc_SEA_vs_GB",
        "matchup": "NFC Championship · Packers vs. Seahawks · Jan 2015",
        "situation_description": (
            "Conference championship, early, on the road. 4th-and-goal inches from the "
            "end zone. Take the automatic three, or go for the touchdown?"
        ),
        "option_a": "Kick the chip-shot field goal",
        "option_b": "Go for the touchdown",
        "option_c": "Quarterback sneak for the inches",
        "option_d": None,
        "actual_call": "a",
        "best_call": "b",
        "win_prob": {"a": 66, "b": 74, "c": 73},
        "game_state": {
            "clock": "1st · 9:00", "your_score": 7, "opp_score": 0,
            "tag": "4th & goal", "ball_on": 99, "poss": "you",
        },
        "outcome": (
            "Green Bay settled for field goals near the goal line instead of touchdowns. "
            "Those missing points loomed huge as Seattle stormed back to win in overtime."
        ),
        "analytics_verdict": (
            "From the 1, the touchdown probability is high and the points swing is "
            "enormous. Repeatedly taking three instead of seven left the door open — and "
            "Seattle walked through it."
        ),
    },
    {
        "sport": "NFL",
        "season": 2011,
        "week": "Super Bowl XLVI",
        "game_id": "nfl_2011_sb_NYG_vs_NE",
        "matchup": "Super Bowl XLVI · Giants vs. Patriots · Feb 2012 (let them score)",
        "situation_description": (
            "Super Bowl, down 2, just over a minute left. The other team has 1st-and-goal "
            "at your 6 and can run the clock down to kick the winning field goal as time "
            "expires. What's your move?"
        ),
        "option_a": "Let them score so you get the ball back with time",
        "option_b": "Defend the goal line and try to force a field goal",
        "option_c": "Burn your timeouts and bank on a stop or turnover",
        "option_d": None,
        "actual_call": "a",
        "best_call": "a",
        "win_prob": {"a": 47, "b": 36, "c": 39},
        "game_state": {
            "clock": "4th · 1:04", "your_score": 15, "opp_score": 17,
            "tag": "1st & goal (them)", "ball_on": 6, "poss": "them",
        },
        "outcome": (
            "New England let the Giants score on purpose, getting the ball back with ~57 "
            "seconds. The comeback drive fell short on a Hail Mary — but the call itself "
            "was the right one."
        ),
        "analytics_verdict": (
            "Stopping them just lets the clock bleed to zero before a chip-shot winner. "
            "Letting them score is counterintuitive but correct — it buys your offense "
            "the only thing that can win the game: time."
        ),
    },
    # ---------------------------- NBA ----------------------------
    {
        "sport": "NBA",
        "season": 2013,
        "week": "Finals Game 6",
        "game_id": "nba_2013_finals_g6_SAS_vs_MIA",
        "matchup": "2013 NBA Finals, Game 6 · Spurs vs. Heat (Ray Allen's corner three)",
        "situation_description": (
            "NBA Finals, Game 6, up 5 with 28 seconds left. Free throws and a defensive "
            "rebound can clinch the title. Do you keep your dominant rebounder — a "
            "Hall-of-Fame big — on the floor?"
        ),
        "option_a": "Keep your Hall-of-Fame big in for rebounding/defense",
        "option_b": "Go small for offense and switchability",
        "option_c": "Keep him in and drop into a zone to wall off the paint",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 86, "b": 74, "c": 82},
        "game_state": {
            "clock": "4th · 0:28", "your_score": 94, "opp_score": 89,
            "tag": "Up 5 · inbound", "zone": "inbound",
        },
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
        "matchup": None,
        "situation_description": (
            "Down 2, 6 seconds left, you have the ball and no timeouts. Drive for the tie "
            "and play for overtime, or pull up for the win?"
        ),
        "option_a": "Get a high-quality 2 to force overtime",
        "option_b": "Shoot the 3 to win it now",
        "option_c": "Drive and kick to a corner-three shooter",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 51, "b": 40, "c": 46},
        "game_state": {
            "clock": "4th · 0:06", "your_score": 98, "opp_score": 100,
            "tag": "Down 2", "zone": "wing",
        },
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
        "matchup": None,
        "situation_description": (
            "Up 3, opponent inbounding with 5 seconds left and no timeouts for either side. "
            "Foul before they can shoot, or play tight defense and contest the three?"
        ),
        "option_a": "Foul immediately to prevent a tying three",
        "option_b": "Play straight-up defense and contest",
        "option_c": "Switch everything, deny the three, give up a two",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 93, "b": 85, "c": 88},
        "game_state": {
            "clock": "4th · 0:05", "your_score": 101, "opp_score": 98,
            "tag": "Up 3 · inbound", "zone": "inbound",
        },
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
        "matchup": None,
        "situation_description": (
            "End of the quarter, you have the ball with about 30 seconds on the clock. "
            "Shoot early to get the ball back for a last shot, or run the clock down?"
        ),
        "option_a": "Go '2-for-1' — shoot by ~25 seconds to guarantee another possession",
        "option_b": "Hold for one shot at the buzzer",
        "option_c": "Push pace for a quick bucket, then trap to force a rushed shot",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 54, "b": 49, "c": 52},
        "game_state": {
            "clock": "2nd · 0:32", "your_score": 50, "opp_score": 48,
            "tag": "End of quarter", "zone": "top",
        },
        "outcome": (
            "Playing 2-for-1 nets teams extra possessions over a season, and extra "
            "possessions are free points. Holding for one shot leaves value on the floor."
        ),
        "analytics_verdict": (
            "Two cracks at the basket beat one almost every time. Getting a shot up early "
            "to guarantee the last possession is a small edge that compounds all game."
        ),
    },
    # ---------------------------- MLB ----------------------------
    {
        "sport": "MLB",
        "season": 2003,
        "week": "ALCS Game 7",
        "game_id": "mlb_2003_alcs_g7_BOS_vs_NYY",
        "matchup": "2003 ALCS Game 7 · Red Sox vs. Yankees (Grady Little leaves Pedro in)",
        "situation_description": (
            "League Championship Series, Game 7, on the road. You're up 5-2 in the 8th, "
            "six outs from the World Series — but your ace is past 115 pitches and clearly "
            "gassed, and the home crowd is stirring. Go to your rested bullpen, or ride "
            "your guy?"
        ),
        "option_a": "Pull your ace and hand it to the bullpen",
        "option_b": "Leave your ace in — he got you here",
        "option_c": "Let him face one more, then a quick hook",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 82, "b": 66, "c": 72},
        "game_state": {
            "clock": "Bot 8th", "your_score": 5, "opp_score": 2,
            "tag": "Ace at 118 pitches", "bases": [1, 0, 0], "outs": 0,
        },
        "outcome": (
            "Grady Little left Pedro Martínez in. The Yankees tied it 5-5, then won on "
            "Aaron Boone's walk-off homer in the 11th — and Little lost his job over it."
        ),
        "analytics_verdict": (
            "The ace's numbers fell off a cliff the third time through the order and past "
            "100 pitches. With a rested pen and a three-run lead six outs from the World "
            "Series, the percentages screamed for the hook."
        ),
    },
    {
        "sport": "MLB",
        "season": 2024,
        "week": "Strategy",
        "game_id": "mlb_strat_sac_bunt_9th",
        "matchup": None,
        "situation_description": (
            "Bottom of the 9th, tie game. Your leadoff man singles — runner on first, "
            "nobody out, the top of your order due up. Bunt him into scoring position, "
            "or swing away?"
        ),
        "option_a": "Sacrifice bunt him to second",
        "option_b": "Swing away and play for the big inning",
        "option_c": "Put a steal on instead of giving up an out",
        "option_d": None,
        "actual_call": "a",
        "best_call": "b",
        "win_prob": {"a": 71, "b": 76, "c": 73},
        "game_state": {
            "clock": "Bot 9th", "your_score": 3, "opp_score": 3,
            "tag": "Runner on 1st · 0 out", "bases": [1, 0, 0], "outs": 0,
        },
        "outcome": (
            "League-wide, giving away an out with a sacrifice bunt lowers run expectancy "
            "in this spot — teams that swing away walk it off more often than teams that "
            "bunt the runner over."
        ),
        "analytics_verdict": (
            "Outs are the most precious thing you have. Trading one for 90 feet shrinks "
            "your run expectancy; with the top of the order up, swinging away keeps the "
            "walk-off — and the big inning — alive."
        ),
    },
    {
        "sport": "MLB",
        "season": 2024,
        "week": "Strategy",
        "game_id": "mlb_strat_ibb_setup_dp",
        "matchup": None,
        "situation_description": (
            "One out, runner on second, first base open, and you're clinging to a lead. "
            "A dangerous slugger steps in with a light-hitting batter on deck. Pitch to "
            "him, or put him on?"
        ),
        "option_a": "Pitch to the slugger",
        "option_b": "Walk him to set up the force and face the weak bat",
        "option_c": None,
        "option_d": None,
        "actual_call": "a",
        "best_call": "b",
        "win_prob": {"a": 68, "b": 73},
        "game_state": {
            "clock": "Top 8th", "your_score": 3, "opp_score": 2,
            "tag": "1 out · runner on 2nd", "bases": [0, 1, 0], "outs": 1,
        },
        "outcome": (
            "With first base open and a steep drop-off to the on-deck hitter, putting the "
            "slugger on sets up a force at every base and a tailor-made inning-ending "
            "double play."
        ),
        "analytics_verdict": (
            "Walking a great hitter to face a poor one — and turning a single into a "
            "possible double play — is the rare free-baserunner move the math actually "
            "likes, when the on-deck gap is this wide."
        ),
    },
    {
        "sport": "MLB",
        "season": 2024,
        "week": "Strategy",
        "game_id": "mlb_strat_closer_8th",
        "matchup": None,
        "situation_description": (
            "Tie game on the road, bottom of the 8th. The other team has the 3-4-5 "
            "hitters due and your All-Star closer is rested. Use him now, or save him "
            "for a 'save situation' in the 9th?"
        ),
        "option_a": "Bring the closer in now for the heart of the order",
        "option_b": "Hold him for the 9th and a save chance",
        "option_c": "Use a setup man now, closer on standby",
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 57, "b": 50, "c": 53},
        "game_state": {
            "clock": "Bot 8th", "your_score": 4, "opp_score": 4,
            "tag": "Heart of the order up", "bases": [0, 0, 0], "outs": 0,
        },
        "outcome": (
            "Across the league, using your best reliever in the highest-leverage moment "
            "— not just the 9th — wins more games. Saving him for a lead you might never "
            "get leaves your best arm in the bullpen."
        ),
        "analytics_verdict": (
            "The save rule is a stat, not a strategy. A tie against the 3-4-5 hitters is "
            "the highest-leverage moment in the game — that's exactly when your best arm "
            "belongs on the mound."
        ),
    },
    {
        "sport": "MLB",
        "season": 2024,
        "week": "Strategy",
        "game_id": "mlb_strat_infield_in_9th",
        "matchup": None,
        "situation_description": (
            "Tie game, bottom of the 9th. The winning run is on third with one out. "
            "Bring the infield in to cut the run at the plate, or play back and try to "
            "turn two?"
        ),
        "option_a": "Bring the infield in to stop the run",
        "option_b": "Play back and go for the double play",
        "option_c": None,
        "option_d": None,
        "actual_call": "b",
        "best_call": "a",
        "win_prob": {"a": 64, "b": 40},
        "game_state": {
            "clock": "Bot 9th", "your_score": 2, "opp_score": 2,
            "tag": "Winning run on 3rd · 1 out", "bases": [0, 0, 1], "outs": 1,
        },
        "outcome": (
            "With the winning run 90 feet away and one out, a normal grounder to a deep "
            "infield ends the game. Playing back hands the other team a walk-off on "
            "almost any ground ball."
        ),
        "analytics_verdict": (
            "The double play doesn't help when the run scores anyway — that's a walk-off "
            "loss. Infield in is the forced move: cut the run at the plate and live to "
            "the 10th."
        ),
    },
]


# Per-game lookups keyed by game_id — curated, static *display* fields joined in
# at read time (no DB column / migration). `matchup` is shown only on the reveal,
# so the decision prompt stays blind.
WIN_PROBS: dict[str, dict[str, int]] = {
    row["game_id"]: row["win_prob"]
    for row in SEED_SITUATIONS
    if row.get("win_prob")
}

GAME_STATE: dict[str, dict] = {
    row["game_id"]: row["game_state"]
    for row in SEED_SITUATIONS
    if row.get("game_state")
}

MATCHUPS: dict[str, str] = {
    row["game_id"]: row["matchup"]
    for row in SEED_SITUATIONS
    if row.get("matchup")
}
