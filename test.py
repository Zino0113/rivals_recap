import cv2
import numpy as np
import os

def extract_tiers(image_path):
    # 1. 이미지 불러오기
    img = cv2.imread(image_path)
    if img is None:
        print("이미지를 찾을 수 없어! 경로를 확인해줘.")
        return

    # 2. 결과 저장할 폴더 생성
    if not os.path.exists('cropped_tiers'):
        os.makedirs('cropped_tiers')

    # 3. 그레이스케일 변환 및 이진화 (배경과 아이콘 분리)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 배경이 어둡고 아이콘이 밝으니까 임계값(Threshold) 처리
    # 숫자를 조절해서 감도를 맞출 수 있어 (지금은 50 정도면 적당해 보임)
    _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

    # 4. 윤곽선(Contours) 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    count = 0
    for cnt in contours:
        # 5. 너무 작은 노이즈나 글씨(BRONZE 등)는 무시하기 (면적 기준)
        area = cv2.contourArea(cnt)
        if area < 1000: # 이 숫자로 크기 필터링 (너무 작으면 글자임)
            continue

        # 6. 아이콘 영역 좌표 구하기
        x, y, w, h = cv2.boundingRect(cnt)
        
        # 7. 아이콘 부분만 잘라내기
        icon = img[y:y+h, x:x+w]

        # 8. 배경 투명하게 만들기 (검은 배경 제거)
        # 알파 채널 추가
        b, g, r = cv2.split(icon)
        alpha = np.zeros_like(b)
        
        # 밝은 부분만 불투명하게, 어두운 배경은 투명하게
        # 아이콘 내부의 어두운 부분 보존을 위해 마스크 정교화가 필요할 수 있음
        # 간단하게는 Grayscale 변환 후 Threshold를 마스크로 사용
        icon_gray = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(icon_gray, 30, 255, cv2.THRESH_BINARY)

        rgba = cv2.merge([b, g, r, alpha])

        # 9. 저장하기
        save_name = f"cropped_tiers/tier_{count}.png"
        cv2.imwrite(save_name, rgba)
        print(f"저장 완료: {save_name}")
        count += 1

    print(f"총 {count}개의 티어 아이콘을 분리했어!")

# 여기에 다운받은 이미지 파일 이름을 넣어줘!
extract_tiers('ranks.jpg')