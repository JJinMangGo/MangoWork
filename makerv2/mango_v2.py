import os
import shutil

# --- [설정 구간] ---
origin_dir = 'origin'  # 원본(사이즈별 폴더들이 있는 곳)
result_dir = 'result'  # 품번별로 모아줄 결과 폴더
# ------------------

def start_collection():
    # 1. 결과 폴더가 없으면 생성
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    print("="*50)
    print(" 찐망고의 '흩어진 이미지 수집기' v1.1 ")
    print("="*50)

    # 2. origin 폴더 안을 훑어보기
    if not os.path.exists(origin_dir):
        print(f"'{origin_dir}' 폴더를 찾을 수 없습니다.")
        return

    items = os.listdir(origin_dir)
    
    for item in items:
        item_path = os.path.join(origin_dir, item)

        # --- [케이스 A] 바깥에 나와있는 'TAG' 이미지 처리 ---
        if os.path.isfile(item_path):
            if item.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) and 'tag' in item.lower():
                # 품번 추출 (예: MG123_01_tag -> MG123_01)
                parts = item.split('_')
                item_code = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]
                
                # 목적지: result/품번 폴더
                target_folder = os.path.join(result_dir, item_code)
                os.makedirs(target_folder, exist_ok=True)
                
                shutil.copy(item_path, os.path.join(target_folder, item))
                print(f"[TAG 수집] {item} -> {item_code}/")

        # --- [케이스 B] 사이즈 이름의 '폴더' 내부 이미지 처리 ---
        elif os.path.isdir(item_path):
            size_folder_name = item  # 예: 2000-2000
            print(f"[{size_folder_name}] 폴더 내 이미지 수집 중...")

            sub_items = os.listdir(item_path)
            for sub_item in sub_items:
                if sub_item.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # 품번 추출
                    parts = sub_item.split('_')
                    item_code = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]
                    
                    # 목적지: result/품번/사이즈폴더
                    final_dest = os.path.join(result_dir, item_code, size_folder_name)
                    os.makedirs(final_dest, exist_ok=True)
                    
                    shutil.copy(os.path.join(item_path, sub_item), os.path.join(final_dest, sub_item))
                    # 너무 많이 뜨면 정신없으니 조용히 작업하도록 출력은 생략하거나 간소화

    print("\n" + "="*50)
    print("모든 이미지를 품번별로 예쁘게 모았습니다!")
    print(f"결과 확인: {os.path.abspath(result_dir)}")
    print("="*50)
    input("\n잠시 검토 후 엔터 키를 누르면 창이 닫힙니다.")

if __name__ == "__main__":
    start_collection()