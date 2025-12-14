# prompt_data.py

# 1. 메인 스탯 (랭크 + 일반 통합) 분석용 프롬프트
MAIN_STATS_PROMPT = """
You are a data analyst for 'Roblox Rivals'. Analyze the provided screenshots (Rank Stats & General Stats) and extract data into JSON.

### Rules:
1. 'Season 1' header usually indicates Rank Stats.
2. 'Statistics' header usually indicates General Stats.
3. Convert all time durations to 'total hours' (float).
4. If a value is not found, use 0.

### Required JSON Structure:
{
    "nickname": "String (Find user nickname from image if visible)",
    "season_1_rank_stats": {
        "duels_played": Integer,
        "duels_won": Integer,
        "duels_lost": Integer,
        "win_rate": Float (percentage),
        "final_elo": Integer,
        "highest_elo": Integer,
        "lowest_elo": Integer
    },
    "general_stats": {
        "playtime_hours": Float,
        "favorite_map": "String",
        "damage_dealt": Integer,
        "eliminations": Integer,
        "deaths": Integer,
        "assists": Integer,
        "duels_played": {
            "wins": Integer,
            "losses": Integer,
            "flawless_wins": Integer,
            "sudden_death_wins": Integer,
            "sudden_death_losses": Integer,
            "current_win_streak": Integer,
            "best_streak": Integer,
            "streak_ended": Integer
        },
        "rounds_played": {
            "wins": Integer,
            "losses": Integer
        },
        "players_empowered": Integer,
        "players_frozen": Integer,
        "damage_absorbed": Integer
    }
}
"""

# 2. 무기 스탯 분석용 프롬프트 (수정됨: 중괄호 이스케이프)
WEAPON_STATS_PROMPT = """
Analyze the weapon statistics screenshot for the weapon: {weapon_name}

### Required JSON Structure:
{{
    "weapon_name": "{weapon_name}",
    "playtime_hours": Float,
    "rounds_played": {{
        "wins": Integer,
        "losses": Integer,
        "win_rate": Float
    }},
    "ranked_rounds_played": {{
        "wins": Integer,
        "losses": Integer,
        "win_rate": Float
    }},
    "damage_dealt": Integer,
    "eliminations": Integer,
    "deaths": Integer
}}
"""