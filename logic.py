# logic.py
# 데이터 계산 및 비즈니스 로직을 담당하는 모듈
import badges_data

def calculate_basic_metrics(data, weapons=[]):
    """기본 승률, K/D, 갭 차이 및 뱃지용 파생 지표 계산"""
    
    kills = data.get('eliminations', 0)
    deaths = data.get('deaths', 0)
    kd = kills / deaths if deaths > 0 else kills

    # 일반전 (Duels)
    d_wins = data.get('duels_played', {}).get('wins', 0)
    d_losses = data.get('duels_played', {}).get('losses', 0)
    total_duels = d_wins + d_losses
    wr_pub = (d_wins / total_duels * 100) if total_duels > 0 else 0.0

    # 랭크전 (Ranked) - [수정됨] 키 경로 변경
    r_wins = data.get('ranked_duels_played', {}).get('ranked_wins', 0)
    r_losses = data.get('ranked_duels_played', {}).get('ranked_losses', 0)
    total_ranked = r_wins + r_losses
    wr_rank = (r_wins / total_ranked * 100) if total_ranked > 0 else 0.0

    gap = wr_rank - wr_pub

    # [뱃지용 추가 지표 계산]
    # 1. 서든데스 통계
    sd_wins = data.get('duels_played', {}).get('sudden_death_wins', 0)
    sd_losses = data.get('duels_played', {}).get('sudden_death_losses', 0)
    sd_total = sd_wins + sd_losses
    sd_win_rate = (sd_wins / sd_total * 100) if sd_total > 0 else 0.0

    # 2. 무기 마스터리 (A등급 이상 개수) - KPH 70 이상
    weapon_mastery_a_count = 0
    for w in weapons:
        kph = (w['kills'] / w['hours']) if w['hours'] > 0 else 0
        if kph >= 70:
            weapon_mastery_a_count += 1

    return {
        "kd": round(kd, 2),
        "wr_pub": round(wr_pub, 1),
        "wr_rank": round(wr_rank, 1),
        "gap": round(gap, 1),
        "total_duels": total_duels,
        "total_ranked": total_ranked,
        "total_kills": kills,
        "playtime": data.get('playtime', 0), # [수정됨] playtime_hours -> playtime
        
        # 뱃지 전용 파생 변수
        "sd_total": sd_total,
        "sd_win_rate": sd_win_rate,
        "weapon_mastery_a_count": weapon_mastery_a_count,
        "weapons": weapons
    }

def calculate_season_score(data, metrics):
    score = 0
    score += data.get('eliminations', 0) * 1
    score += data.get('duels_played', {}).get('wins', 0) * 10
    score += int(data.get('playtime', 0) * 50) # [수정됨]
    score += data.get('duels_played', {}).get('flawless_wins', 0) * 20
    score += data.get('ranked_duels_played', {}).get('ranked_wins', 0) * 30 # [수정됨]
    return score

def get_acquired_badges(data, metrics):
    """조건을 만족하는 뱃지를 찾아내고, 우선순위에 따라 정렬하여 반환"""
    acquired = []
    
    for badge in badges_data.BADGE_LIST:
        try:
            # 1. 조건 확인
            if badge['condition'](data, metrics):
                
                badge_info = badge.copy()

                # 2. 동적 이름(name) 생성
                if 'name_func' in badge:
                    badge_info['name'] = badge['name_func'](data, metrics)

                # 3. 동적 이미지(image) 생성
                if 'image_func' in badge:
                    badge_info['image'] = badge['image_func'](data, metrics)

                # 4. 동적 설명(desc) 생성
                if 'desc_func' in badge:
                    badge_info['desc'] = badge['desc_func'](data, metrics)
                
                # 5. 동적 우선순위(priority) 계산
                if 'priority_func' in badge:
                    badge_info['priority'] = badge['priority_func'](data, metrics)
                else:
                    badge_info['priority'] = badge.get('priority', 0)
                
                acquired.append(badge_info)
        except Exception as e:
            # 에러 발생 시 콘솔에 로그만 남기고 다음 뱃지로 진행 (앱 멈춤 방지)
            print(f"뱃지 오류 ({badge.get('name', 'Unknown')}): {e}")
            continue
    
    # 우선순위가 높은 순서대로 정렬 (내림차순)
    acquired.sort(key=lambda x: x['priority'], reverse=True)
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