# prompt_data.py

MAIN_STATS_PROMPT = """
You are a data analyst for 'Roblox Rivals'. Analyze the provided screenshots (Rank Stats & General Stats) and extract data into JSON.

### Rules:
1. 'Season 1' header usually indicates Rank Stats.
2. 'Statistics' header usually indicates General Stats.
3. Convert all time durations to 'total hours' (float).
4. If a value is not found, use 0.

### CRITICAL FORMATTING RULES:
- **Percentages:** Extract the number EXACTLY as shown before the '%'. 
  - Example: "71.2%" -> 71.2
  - Example: "0.5%" -> 0.5
  - **DO NOT** convert to decimal (e.g., DO NOT write 0.712 for 71.2%).
- **Numbers:** Remove commas (e.g., "3,104" -> 3104).

### Required JSON Structure:
{
    "season_1_rank_stats": {
        "duels_played": Integer,
        "duels_won": Integer,
        "duels_lost": Integer,
        "win_rate": Float (e.g. 72.5),
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

WEAPON_STATS_PROMPT = """
Analyze the weapon statistics screenshot for the weapon: {weapon_name}

### CRITICAL FORMATTING RULES:
- **Percentages:** Extract the number EXACTLY as shown before the '%'. 
  - Example: "30.6%" -> 30.6
  - Example: "0.4%" -> 0.4
  - **DO NOT** convert to decimal.

### Required JSON Structure:
{{
    "weapon_name": "{weapon_name}",
    "playtime_hours": Float,
    "rounds_played": {{
        "total": Integer,
        "wins": Integer,
        "losses": Integer,
        "win_rate": Float (e.g. 58.4)
    }},
    "ranked_rounds_played": {{
        "total": Integer,
        "wins": Integer,
        "losses": Integer,
        "win_rate": Float (e.g. 73.7)
    }},
    "damage_dealt": Integer,
    "eliminations": Integer,
    "deaths": Integer,
    "accuracy_stats": {{
        "hit_percentage": Float (e.g. 30.2),
        "critical_hit_percentage": Float (e.g. 28.6)
    }}
}}
"""