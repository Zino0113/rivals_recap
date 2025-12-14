# badges_data.py
# 뱃지 목록과 획득 조건을 관리하는 파일입니다.

# 가중치 설정
WEIGHT_FROZEN = 50      
WEIGHT_EMPOWERED = 50   
WEIGHT_ABSORBED = 10000 

# [1] 연승 칭호 티어 정의
STREAK_TIERS = [
    (500, "👑 전설의 출현", "assets/badges/RecapCard_legend.png"),
    (300, "👹 전장의 화신", "assets/badges/RecapCard_masin.png"),
    (100, "💯 백전백승", "assets/badges/RecapCard_100.png"),
    (50, "🏆 무패신화", "assets/badges/RecapCard_nl.png"),
    (30, "⚔️ 전장의 지배자", "assets/badges/RecapCard_ruler.png"),
    (10, "🔥 연전연승", "assets/badges/RecapCard_10.png"),
]

# [2] 연승 저지 칭호 티어 정의
SLAYER_TIERS = [
    (100, "🗡️ 신화 파괴자", "assets/badges/RecapCard_gk.png"),
    (50, "🔪 거인 학살자", "assets/badges/RecapCard_giant.png"),
    (30, "🚫 셧다운", "assets/badges/RecapCard_sd.png"),
    (10, "🛑 여기까지입니다", "assets/badges/RecapCard_kiro.png"),
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

    # --- [연승 관련: 동적 생성] ---
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

    # --- [거인 학살자 시리즈: 동적 생성] ---
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

    # --- [동적 우선순위 칭호 (루트 경로로 변경됨)] ---
    # players_empowered 등은 이제 d['duels_played']가 아니라 d 바로 아래에 있음
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
    },
    {
        "id": "test1",
        "name": "🛡️ 넌 못 지나간다",
        "condition": lambda d, m: 1 > 0,
        "desc_func": lambda d, m: f"방패로 막은 피해: {d['duels_played'].get('damage_absorbed', 0):,}",
        "priority": 1,
        "image": "assets/badges/RecapCard_shld.png"
    },
    {
        "id": "test2",
        "name": "🛡️ 넌 못 지나간다2",
        "condition": lambda d, m: 1 > 0,
        "desc_func": lambda d, m: f"방패로 막은 피해: {d['duels_played'].get('damage_absorbed', 0):,}",
        "priority": 1,
        "image": "assets/badges/RecapCard_shld.png"
    },
    {
        "id": "test3",
        "name": "🛡️ 넌 못 지나간다3",
        "condition": lambda d, m: 1 > 0,
        "desc_func": lambda d, m: f"방패로 막은 피해: {d['duels_played'].get('damage_absorbed', 0):,}",
        "priority": 1,
        "image": "assets/badges/RecapCard_shld.png"
    }
]