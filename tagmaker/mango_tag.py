import os
import re
import sys

import cv2
import numpy as np

# --- [설정 구간] ---
origin_dir = 'origin'      # 이름을 바꿀 이미지가 있는 곳
CHECK_LAST = 4             # 품번마다 뒤에서 몇 장까지 바코드를 찾을지
IMG_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
# ------------------

detector = cv2.barcode.BarcodeDetector()


def base_dir():
    # exe로 실행하면 exe가 있는 폴더, py로 실행하면 py가 있는 폴더 기준
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def read_image(path):
    # 한글 경로도 읽을 수 있게 numpy로 읽기
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def has_barcode(path):
    img = read_image(path)
    if img is None:
        return False
    h, w = img.shape[:2]
    # 큰 이미지는 줄여서 먼저 빠르게 확인, 안 잡히면 원본으로 한 번 더
    scale = 1200 / max(h, w)
    tries = [cv2.resize(img, (int(w * scale), int(h * scale)))] if scale < 1 else []
    tries.append(img)
    for im in tries:
        try:
            ok, _ = detector.detect(im)
            if ok:
                return True
        except cv2.error:
            pass
    return False


def split_name(filename):
    # AFA4QPA5J_BK_09.jpg -> ('AFA4QPA5J_BK', '09', '.jpg')
    stem, ext = os.path.splitext(filename)
    parts = stem.split('_')
    if len(parts) < 3:
        return None
    num = parts[-1]
    if not re.fullmatch(r'\d+', num):
        return None
    return '_'.join(parts[:-1]), num, ext


def main():
    print("=" * 50)
    print(" 🥭 찐망고의 태그 이름 바꾸기 🥭 ")
    print("=" * 50)

    folder = os.path.join(base_dir(), origin_dir)
    if not os.path.isdir(folder):
        print(f"'{origin_dir}' 폴더를 찾을 수 없습니다.")
        input("\n엔터 키를 누르면 종료됩니다.")
        return

    # 1. 품번별로 묶기
    groups = {}
    for f in os.listdir(folder):
        if not f.lower().endswith(IMG_EXT):
            continue
        info = split_name(f)
        if info is None:
            continue
        code, num, ext = info
        groups.setdefault(code, []).append((int(num), f, ext))

    if not groups:
        print("바꿀 이미지가 없습니다. (파일명 예: AFA4QPA5J_BK_09.jpg)")
        input("\n엔터 키를 누르면 종료됩니다.")
        return

    # 2. 품번마다 뒤에서부터 바코드 찾기
    plan = []        # (원래이름, 새이름)
    no_barcode = []  # 바코드를 못 찾은 품번
    existing = set(os.listdir(folder))

    print(f"\n품번 {len(groups)}개에서 바코드 찾는 중...\n")
    for code in sorted(groups):
        files = sorted(groups[code])
        start = None
        for i in range(len(files) - 1, max(len(files) - 1 - CHECK_LAST, -1), -1):
            if has_barcode(os.path.join(folder, files[i][1])):
                start = i  # 더 앞에 바코드가 있으면 계속 앞으로 갱신
        if start is None:
            no_barcode.append(code)
            print(f"  ⚠ {code}  바코드 없음")
            continue

        for k, (_, f, ext) in enumerate(files[start:], 1):
            new = f"{code}_tag{k}{ext}"
            if new in existing and new != f:
                print(f"  ⚠ {code}  {new} 이(가) 이미 있어서 건너뜀")
                break
            plan.append((f, new))
        tags = ', '.join(f for f, _ in plan if f.startswith(code + '_'))
        print(f"  ✓ {code}  → {tags}")

    # 3. 미리보기
    print("\n" + "=" * 50)
    print(" 이렇게 바꿀게요")
    print("=" * 50)
    for old, new in plan:
        print(f"  {old}  →  {new}")
    if no_barcode:
        print(f"\n ⚠ 바코드를 못 찾은 품번 {len(no_barcode)}개 (직접 확인해주세요)")
        for c in no_barcode:
            print(f"   - {c}")

    if not plan:
        input("\n바꿀 파일이 없습니다. 엔터 키를 누르면 종료됩니다.")
        return

    ans = input(f"\n총 {len(plan)}개 파일 이름을 바꿀까요? (엔터 = 진행 / n = 취소) ")
    if ans.strip().lower() == 'n':
        print("취소했습니다. 아무것도 바뀌지 않았어요.")
        input("\n엔터 키를 누르면 종료됩니다.")
        return

    # 4. 이름 바꾸기 + 기록 남기기
    log_path = os.path.join(base_dir(), 'rename_log.txt')
    with open(log_path, 'a', encoding='utf-8') as log:
        for old, new in plan:
            os.rename(os.path.join(folder, old), os.path.join(folder, new))
            log.write(f"{old} -> {new}\n")

    print("\n" + "=" * 50)
    print(f" 완료! {len(plan)}개 파일 이름을 바꿨습니다.")
    print(" 바꾼 기록: rename_log.txt")
    print("=" * 50)
    input("\n엔터 키를 누르면 종료됩니다.")


if __name__ == "__main__":
    main()
