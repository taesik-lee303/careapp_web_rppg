"""
사용 가능한 카메라 목록 확인 프로그램
연결된 모든 카메라를 찾아서 표시합니다.
"""

import cv2
import sys


def list_available_cameras():
    """
    사용 가능한 모든 카메라를 찾아서 목록을 표시합니다.
    """
    print("=" * 60)
    print("사용 가능한 카메라 검색 중...")
    print("=" * 60)
    print()
    
    available_cameras = []
    
    # 0부터 10까지 카메라 인덱스 테스트
    print("카메라 인덱스 0-10을 확인 중...")
    for i in range(11):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # 카메라 정보 가져오기
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # 카메라 이름 가져오기 시도
            backend = cap.getBackendName()
            
            # 프레임 읽기 테스트
            ret, frame = cap.read()
            if ret:
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'backend': backend,
                    'working': True
                })
                print(f"✅ 카메라 인덱스 {i}: {width}x{height} @ {fps}fps ({backend})")
            else:
                print(f"⚠️  카메라 인덱스 {i}: 연결됐지만 프레임 읽기 실패")
            
            cap.release()
        else:
            print(f"❌ 카메라 인덱스 {i}: 사용 불가")
    
    print()
    print("=" * 60)
    print("검색 결과")
    print("=" * 60)
    
    if len(available_cameras) == 0:
        print("❌ 사용 가능한 카메라를 찾을 수 없습니다.")
        return None
    
    print(f"\n총 {len(available_cameras)}개의 카메라를 찾았습니다:\n")
    
    for i, cam in enumerate(available_cameras):
        print(f"  [{cam['index']}] 해상도: {cam['width']}x{cam['height']}, FPS: {cam['fps']}, 백엔드: {cam['backend']}")
    
    print()
    print("=" * 60)
    print("사용 방법")
    print("=" * 60)
    print("\n프로그램에서 카메라를 선택하려면:")
    print("1. main_mediapipe.py 또는 main.py 파일을 열고")
    print("2. VideoCapture(0) 부분을 VideoCapture(카메라_인덱스)로 변경하세요")
    print("\n예시:")
    if len(available_cameras) > 1:
        print(f"   로지텍 웹캠이 인덱스 {available_cameras[-1]['index']}라면:")
        print(f"   cap = cv2.VideoCapture({available_cameras[-1]['index']})")
    print()
    
    return available_cameras


def test_camera(camera_index):
    """
    특정 카메라 인덱스를 테스트합니다.
    """
    print(f"\n카메라 인덱스 {camera_index} 테스트 중...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ 카메라 인덱스 {camera_index}를 열 수 없습니다.")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print(f"❌ 카메라 인덱스 {camera_index}에서 프레임을 읽을 수 없습니다.")
        cap.release()
        return False
    
    print(f"✅ 카메라 인덱스 {camera_index}가 정상적으로 작동합니다!")
    print(f"   프레임 크기: {frame.shape}")
    
    cap.release()
    return True


if __name__ == "__main__":
    try:
        cameras = list_available_cameras()
        
        if cameras and len(cameras) > 1:
            print("\n" + "=" * 60)
            print("추천: 가장 높은 인덱스가 외부 웹캠일 가능성이 높습니다")
            print("=" * 60)
            print(f"\n로지텍 웹캠을 사용하려면 인덱스 {cameras[-1]['index']}를 사용하세요.")
            print(f"\n테스트하려면 다음 명령어를 실행하세요:")
            print(f"  python -c \"from list_cameras import test_camera; test_camera({cameras[-1]['index']})\"")
        
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

