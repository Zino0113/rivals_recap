# logic.py
# 데이터 계산 및 비즈니스 로직을 담당하는 모듈
import badges_data

def calculate_basic_metrics(data):
    """기본 승률, K/D, 갭 차이 등을 계산하여 딕셔너리로 반환"""
    
    kills = data.get('eliminations', 0)
    deaths = data.get('deaths', 0)
    kd = kills / deaths if deaths > 0 else kills

    d_wins = data['duels_played'].get('wins', 0)
    d_losses = data['duels_played'].get('losses', 0)
    total_duels = d_wins + d_losses
    wr_pub = (d_wins / total_duels * 100) if total_duels > 0 else 0.0

    r_wins = data['ranked_duels'].get('wins', 0)
    r_losses = data['ranked_duels'].get('losses', 0)
    total_ranked = r_wins + r_losses
    wr_rank = (r_wins / total_ranked * 100) if total_ranked > 0 else 0.0

    gap = wr_rank - wr_pub

    return {
        "kd": round(kd, 2),
        "wr_pub": round(wr_pub, 1),
        "wr_rank": round(wr_rank, 1),
        "gap": round(gap, 1),
        "total_duels": total_duels,
        "total_ranked": total_ranked,
        "total_kills": kills, # 카드 표시용 추가
        "playtime": data.get('playtime_hours', 0) # 카드 표시용 추가
    }

def calculate_season_score(data, metrics):
    """
    시즌 1 종합 점수 계산 (예시 로직)
    점수 = (킬수 * 1) + (승리 * 10) + (플레이타임 * 50) + (무결점승리 * 20)
    """
    score = 0
    score += data.get('eliminations', 0) * 1
    score += data['duels_played'].get('wins', 0) * 10
    score += int(data.get('playtime_hours', 0) * 50)
    score += data['duels_played'].get('flawless_wins', 0) * 20
    
    # 랭크 보너스
    score += data['ranked_duels'].get('wins', 0) * 30
    
    return score

def get_acquired_badges(data, metrics):
    """획득한 뱃지를 우선순위(priority) 순으로 정렬하여 반환"""
    acquired = []
    for badge in badges_data.BADGE_LIST:
        try:
            if badge['condition'](data, metrics):
                acquired.append(badge)
        except Exception:
            continue
    
    # 우선순위가 높은 순서대로 정렬 (내림차순)
    acquired.sort(key=lambda x: x.get('priority', 0), reverse=True)
    return acquired

def calculate_weapon_insights(weapons):
    insights = []
    for w in weapons:
        hours = w['hours']
        kills = w['kills']
        kph = (kills / hours) if hours > 0 else 0
        
        tier = "B"
        if kph >= 120: tier = "GOD"
        elif kph >= 100: tier = "SSS"
        elif kph >= 70: tier = "A"
        
        insights.append({
            "name": w['name'],
            "hours": hours,
            "kills": kills,
            "kph": round(kph, 1),
            "tier": tier
        })
    return insights