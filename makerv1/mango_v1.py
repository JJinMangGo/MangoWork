import os
import shutil

# --- [설정 구간] ---
origin_dir = 'origin'  # 원본 이미지가 있는 곳
result_dir = 'result'  # 품번별로 정리될 결과 폴더
# ------------------


def start_maker():
    # 1. 결과 폴더가 없으면 생성
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    print("=" * 40)
    print(" 🥭 찐망고의 스마트 폴더 메이커 🥭 ")
    print("=" * 40)

    if not os.path.exists(origin_dir):
        print(f"'{origin_dir}' 폴더를 찾을 수 없습니다.")
        input("엔터 키를 누르면 종료됩니다.")
        return

    # 2. 만들 사이즈 폴더 이름 입력 (예: 1440-1890, 1732-2000)
    folder_input = input("생성할 폴더명을 입력하세요 (여러 개면 쉼표로 구분): ")
    target_folders = [f.strip() for f in folder_input.split(',') if f.strip()]

    # 3. origin 폴더의 이미지들을 품번별로 분류
    for filename in os.listdir(origin_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue

        # 품번 추출 (예: MG123_01_1.jpg -> MG123_01)
        parts = filename.split('_')
        item_code = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]

        item_path = os.path.join(result_dir, item_code)
        os.makedirs(item_path, exist_ok=True)

        src = os.path.join(origin_dir, filename)

        if 'tag' in filename.lower():
            # TAG 이미지는 품번 폴더 바로 아래에 복사
            shutil.copy(src, os.path.join(item_path, filename))
            print(f"[TAG] {filename} -> 품번 폴더로 복사됨")
        else:
            # 일반 이미지는 입력한 사이즈 폴더마다 복사
            for folder_name in target_folders:
                target_path = os.path.join(item_path, folder_name)
                os.makedirs(target_path, exist_ok=True)
                shutil.copy(src, os.path.join(target_path, filename))
            print(f"[IMG] {filename} -> 사이즈 폴더들로 복사됨")

    print("\n" + "=" * 40)
    print(" 분류 작업이 완벽하게 끝났습니다!")
    print("=" * 40)
    input("엔터 키를 누르면 종료됩니다.")


if __name__ == "__main__":
    start_maker()
