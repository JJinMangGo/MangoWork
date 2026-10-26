import os
import re
import sys

# --- [설정 구간] ---
origin_dir = 'origin'      # tag로 바꿀 이미지만 넣는 곳
IMG_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
# ------------------


def base_dir():
    # exe로 실행하면 exe가 있는 폴더, py로 실행하면 py가 있는 폴더 기준
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def split_name(filename):
    # BE26A3FRK02_99_06.JPG -> ('BE26A3FRK02_99', '06', '.JPG')
    stem, ext = os.path.splitext(filename)
    if '_' not in stem:
        return None
    code, num = stem.rsplit('_', 1)
    if not re.fullmatch(r'\d+', num):
        return None
    return code, num, ext


def main():
    print("=" * 50)
    print("  찐망고의 태그 이름 바꾸기")
    print("=" * 50)

    folder = os.path.join(base_dir(), origin_dir)
    if not os.path.isdir(folder):
        print(f"'{origin_dir}' 폴더를 찾을 수 없습니다.")
        input("\n엔터 키를 누르면 종료됩니다.")
        return

    # 1. 품번별로 묶기
    groups = {}
    skipped = []
    for f in os.listdir(folder):
        if not f.lower().endswith(IMG_EXT):
            continue
        info = split_name(f)
        if info is None:
            skipped.append(f)
            continue
        code, num, ext = info
        groups.setdefault(code, []).append((int(num), f, ext))

    # 2. 품번마다 번호 작은 순서대로 tag1, tag2...
    plan = []
    existing = set(os.listdir(folder))
    for code in sorted(groups):
        for k, (_, f, ext) in enumerate(sorted(groups[code]), 1):
            new = f"{code}_tag{k}{ext}"
            if new in existing:
                print(f"  ! {new} 이(가) 이미 있어서 {f} 은(는) 건너뜀")
                continue
            plan.append((f, new))

    # 3. 미리보기
    print("\n 이렇게 바꿀게요\n")
    for old, new in plan:
        print(f"  {old}  ->  {new}")
    if skipped:
        print("\n 이름 규칙이 안 맞아서 건너뛴 파일 (예: 품번_색상_06.jpg)")
        for f in skipped:
            print(f"   - {f}")

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
