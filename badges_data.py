# badges_data.py
# 뱃지 목록, 획득 조건, 그리고 '이미지 파일 경로'를 관리합니다.

BADGE_LIST = [
    # --- [랭크/피지컬 관련] ---
    {
        "id": "giant_slayer",
        "name": "🔪 거인 학살자",
        "desc": "100연승 이상 유저 저지",
        "condition": lambda d, m: d['duels_played'].get('streak_ended', 0) >= 100,
        "priority": 100, # 카드에 표시될 우선순위 (높을수록 위)
        "image": "assets/badges/badge_ice.png"
    },
    {
        "id": "streak_breaker",
        "name": "🗡️ 연승 브레이커",
        "desc": "50연승 이상 유저 저지",
        "condition": lambda d, m: 50 <= d['duels_played'].get('streak_ended', 0) < 100,
        "priority": 80,
        "image": "assets/badges/badge_ice.png"
    },
    {
        "id": "rank_warrior",
        "name": "😎 실전 압축 근육",
        "desc": "일반전보다 랭크 승률이 더 높음",
        "condition": lambda d, m: m['gap'] >= 0 and m['total_ranked'] >= 10,
        "priority": 60,
        "image": "assets/badges/badge_ice.png"
    },
    
    # --- [재미/특수 스탯 관련] (AI가 추출했다고 가정하거나, 수동 입력 데이터 활용) ---
    # 실제로는 AI 프롬프트에서 이 데이터들을 'custom_stats' 등으로 뽑아와야 정확합니다.
    # 여기서는 예시 로직으로 구현합니다.
    {
        "id": "ice_king",
        "name": "❄️ 얼음땡 마스터",
        "desc": "얼음 광선으로 적을 많이 얼림 (가정)",
        "condition": lambda d, m: d.get('damage_dealt', 0) > 1000000, # 예시 조건
        "priority": 50,
        "image": "assets/badges/badge_ice.png"
    },
    {
        "id": "tanker",
        "name": "🛡️ 넌 못 지나간다",
        "desc": "방패로 막은 피해량 상위권 (가정)",
        "condition": lambda d, m: d.get('deaths', 1) > 100 and (d.get('damage_dealt', 0)/d.get('deaths', 1)) < 200, # 딜 효율은 낮은데 많이 맞음
        "priority": 40,
        "image": "assets/badges/badge_ice.png"
    },
    {
        "id": "heart_strong",
        "name": "❤️‍🔥 강심장",
        "desc": "서든데스 승률 50% 이상",
        "condition": lambda d, m: (
            d['duels_played'].get('sudden_death_wins', 0) + d['duels_played'].get('sudden_death_losses', 0) >= 10 
            and (d['duels_played'].get('sudden_death_wins', 0) / (d['duels_played'].get('sudden_death_wins', 0) + d['duels_played'].get('sudden_death_losses', 0))) >= 0.5
        ),
        "priority": 70,
        "image": "assets/badges/badge_ice.png"
    },
    {
        "id": "living_legend",
        "name": "👿 리빙 레전드",
        "desc": "K/D 5.0 이상",
        "condition": lambda d, m: m['kd'] >= 5.0,
        "priority": 90,
        "image": "assets/badges/badge_ice.png"
    }
]