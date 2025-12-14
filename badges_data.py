# badges_data.py

# 가중치 설정
WEIGHT_FROZEN = 50      
WEIGHT_EMPOWERED = 50   
WEIGHT_ABSORBED = 10000 

# [1] 연승 칭호 티어 정의
STREAK_TIERS = [
    (500, "👑 전설의 출현", "assets/badges/ws_500.png"),
    (300, "👹 전장의 화신", "assets/badges/ws_300.png"),
    (100, "💯 백전백승", "assets/badges/ws_100.png"),
    (50, "🏆 무패신화", "assets/badges/ws_50.png"),
    (30, "⚔️ 전장의 지배자", "assets/badges/ws_30.png"),
    (10, "🔥 연전연승", "assets/badges/ws_10.png"),
]

# [2] 연승 저지 칭호 티어 정의
SLAYER_TIERS = [
    (100, "🗡️ 신화 파괴자", "assets/badges/RecapCard_gk.png"),
    (50, "🔪 거인 학살자", "assets/badges/RecapCard_giant.png"),
    (30, "🚫 셧다운", "assets/badges/RecapCard_sd.png"),
    (10, "🛑 여기까지입니다", "assets/badges/RecapCard_kiro.png"),
]

# [3] 등반자 티어 정의 (차이 > 400 + 600a)
CLIMBER_TIERS = [
    (2800, "⛰️ 신화급 등반자", "assets/badges/climber_myth.png"),
    (2200, "🏔️ 전설의 등반자", "assets/badges/climber_legend.png"),
    (1600, "🧗 엄청난 등반자", "assets/badges/climber_epic.png"),
    (1000, "🏃 훌륭한 등반자", "assets/badges/climber_great.png"),
    (400, "🥾 등반자", "assets/badges/climber_normal.png"),
]

# [4] 꽉잡아(추락) 티어 정의
DROPPER_TIERS = [
    (2800, "⚓ 심해 탐사", "assets/badges/drop_deep.png"),
    (2200, "🎢 지옥행 급행열차", "assets/badges/drop_hell.png"),
    (1600, "☄️ 중력 실험", "assets/badges/drop_gravity.png"),
    (1000, "🪂 자유낙하", "assets/badges/drop_freefall.png"),
    (400, "🍌 미끄덩", "assets/badges/drop_slip.png"),
]

def get_tier_info(value, tiers):
    for limit, name, img in tiers:
        if value >= limit:
            return name, img
    return None, None

BADGE_LIST = [
    # --- [강심장] ---
    {
        "id": "heart_strong",
        "name": "❤️‍🔥 강심장",
        "condition": lambda d, m: m['sd_total'] >= 10 and m['sd_win_rate'] >= 50.0,
        "desc_func": lambda d, m: f"급사 승률: {m['sd_win_rate']:.1f}%",
        "priority": 100,
        "image": "assets/badges/RecapCard_sh.png"
    },

    # --- [연승 관련] ---
    {
        "id": "dynamic_streak",
        "name": "연승 칭호",
        "image": "assets/badges/ws_10.png",
        "condition": lambda d, m: d['duels_played'].get('best_streak', 0) >= 10,
        "name_func": lambda d, m: get_tier_info(d['duels_played'].get('best_streak', 0), STREAK_TIERS)[0],
        "image_func": lambda d, m: get_tier_info(d['duels_played'].get('best_streak', 0), STREAK_TIERS)[1],
        "desc_func": lambda d, m: f"최고 연승 {d['duels_played'].get('best_streak', 0)}회",
        "priority_func": lambda d, m: 100 + min(50, d['duels_played'].get('best_streak', 0) // 10),
    },

    # --- [거인 학살자] ---
    {
        "id": "dynamic_slayer",
        "name": "학살자 칭호",
        "image": "assets/badges/slayer_10.png",
        "condition": lambda d, m: d['duels_played'].get('streak_ended', 0) >= 10,
        "name_func": lambda d, m: get_tier_info(d['duels_played'].get('streak_ended', 0), SLAYER_TIERS)[0],
        "image_func": lambda d, m: get_tier_info(d['duels_played'].get('streak_ended', 0), SLAYER_TIERS)[1],
        "desc_func": lambda d, m: f"저지한 최고 연승: {d['duels_played'].get('streak_ended', 0)}",
        "priority_func": lambda d, m: 100 + min(50, d['duels_played'].get('streak_ended', 0) // 2),
    },

    # --- [웨폰 마스터] ---
    {
        "id": "weapon_master",
        "name": "🔫 웨폰 마스터",
        "condition": lambda d, m: m['weapon_mastery_a_count'] >= 3,
        "desc_func": lambda d, m: f"무기 숙련도 A {m['weapon_mastery_a_count']}개 보유",
        "priority": 100,
        "image": "assets/badges/RecapCard_wm.png"
    },

    # --- [NEW: n인분은 한다] ---
    {
        "id": "kd_carry",
        "name": "1인분", # 기본값
        "condition": lambda d, m: m['kd'] >= 1.0,
        "name_func": lambda d, m: f"🍛 {int(m['kd'])}인분은 한다",
        "desc_func": lambda d, m: f"K/D Ratio: {m['kd']}",
        "priority_func": lambda d, m: 80 + int(m['kd']) * 5, # KD 높을수록 우선순위 증가
        "image": "assets/badges/RecapCard_rice.png" # 밥그릇 아이콘 추천
    },

    # --- [NEW: 등반자 시리즈] ---
    {
        "id": "climber",
        "name": "등반자",
        "image": "assets/badges/climber_normal.png",
        "condition": lambda d, m: (m['final_elo'] - m['lowest_elo']) >= 400,
        "name_func": lambda d, m: get_tier_info(m['final_elo'] - m['lowest_elo'], CLIMBER_TIERS)[0],
        "image_func": lambda d, m: get_tier_info(m['final_elo'] - m['lowest_elo'], CLIMBER_TIERS)[1],
        "desc_func": lambda d, m: f"점수 상승: +{m['final_elo'] - m['lowest_elo']:,}",
        "priority": 90
    },

    # --- [NEW: 꽉잡아(추락) 시리즈] ---
    {
        "id": "dropper",
        "name": "추락",
        "image": "assets/badges/drop_slip.png",
        "condition": lambda d, m: (m['highest_elo'] - m['final_elo']) >= 400,
        "name_func": lambda d, m: get_tier_info(m['highest_elo'] - m['final_elo'], DROPPER_TIERS)[0],
        "image_func": lambda d, m: get_tier_info(m['highest_elo'] - m['final_elo'], DROPPER_TIERS)[1],
        "desc_func": lambda d, m: f"점수 하락: -{m['highest_elo'] - m['final_elo']:,}",
        "priority": 85
    },

    # --- [NEW: 명사수 (스나 헤드 50% 이상)] ---
    {
        "id": "sharpshooter",
        "name": "🎯 명사수",
        "condition": lambda d, m: any("sniper" in w.get('weapon_name', '').lower() and w.get('accuracy_stats', {}).get('critical_hit_percentage', 0) >= 50 for w in m['weapons']),
        "desc_func": lambda d, m: "스나이퍼 헤드샷 50% 이상",
        "priority": 110,
        "image": "assets/badges/RecapCard_sniper.png"
    },

    # --- [NEW: 헤드샷 (일반 무기 헤드 25% 이상)] ---
    {
        "id": "headhunter",
        "name": "🤕 헤드헌터",
        "condition": lambda d, m: any("sniper" not in w.get('weapon_name', '').lower() and w.get('accuracy_stats', {}).get('critical_hit_percentage', 0) >= 25 for w in m['weapons']),
        "desc_func": lambda d, m: "일반 무기 헤드샷 25% 이상",
        "priority": 95,
        "image": "assets/badges/RecapCard_head.png"
    },

    # --- [동적 칭호] ---
    {
        "id": "charge",
        "name": "📢 돌격!",
        "condition": lambda d, m: d.get('players_empowered', 0) > 0,
        "desc_func": lambda d, m: f"격려한 아군 수: {d.get('players_empowered', 0)}명",
        "priority_func": lambda d, m: (d.get('players_empowered', 0) / WEIGHT_EMPOWERED) * 100,
        "image": "assets/badges/RecapCard_horn.png"
    },
    {
        "id": "frozen_hands",
        "name": "❄️ 손이 시려워 꽁!",
        "condition": lambda d, m: d.get('players_frozen', 0) > 0,
        "desc_func": lambda d, m: f"얼린 적: {d.get('players_frozen', 0)}명",
        "priority_func": lambda d, m: (d.get('players_frozen', 0) / WEIGHT_FROZEN) * 100,
        "image": "assets/badges/RecapCard_ice.png"
    },
    {
        "id": "tanker",
        "name": "🛡️ 넌 못 지나간다",
        "condition": lambda d, m: d.get('damage_absorbed', 0) > 0,
        "desc_func": lambda d, m: f"방패로 막은 피해: {d.get('damage_absorbed', 0):,}",
        "priority_func": lambda d, m: (d.get('damage_absorbed', 0) / WEIGHT_ABSORBED) * 100,
        "image": "assets/badges/RecapCard_shld.png"
    }
]