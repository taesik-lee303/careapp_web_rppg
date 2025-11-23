"""
카메라 유틸리티 함수
사용 가능한 카메라를 찾고 선택하는 기능을 제공합니다.
"""

import cv2
import warnings
import os


def find_available_cameras(max_index=10):
    """
    사용 가능한 모든 카메라를 찾습니다.
    
    Args:
        max_index: 검색할 최대 카메라 인덱스
        
    Returns:
        사용 가능한 카메라 인덱스 리스트
    """
    # OpenCV 경고 메시지 억제 (obsensor 등 불필요한 에러 메시지)
    # 환경 변수로 OpenCV 로그 레벨 설정
    os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
    
    available = []
    for i in range(max_index + 1):
        try:
            # 경고 메시지 억제
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Windows에서는 DirectShow 백엔드 사용
        except:
            # VideoCapture 생성 실패 시 다음 인덱스로
            continue
            
        if cap is not None and cap.isOpened():
            try:
                ret, _ = cap.read()
                if ret:
                    available.append(i)
            except:
                # 프레임 읽기 실패 시 무시
                pass
        if cap is not None:
            cap.release()
    return available


def find_external_webcam(preferred_index=None):
    """
    외부 웹캠(로지텍 등)을 찾습니다.
    일반적으로 가장 높은 인덱스가 외부 웹캠입니다.
    
    Args:
        preferred_index: 선호하는 카메라 인덱스 (None이면 자동 선택)
        
    Returns:
        카메라 인덱스, 사용 가능한 카메라 목록
    """
    available = find_available_cameras()
    
    if len(available) == 0:
        return None, []
    
    if preferred_index is not None:
        if preferred_index in available:
            return preferred_index, available
        else:
            print(f"⚠️  경고: 지정한 카메라 인덱스 {preferred_index}를 사용할 수 없습니다.")
            print(f"   사용 가능한 카메라: {available}")
    
    # 여러 카메라가 있으면 가장 높은 인덱스 선택 (일반적으로 외부 웹캠)
    if len(available) > 1:
        selected = max(available)
        print(f"📹 여러 카메라가 감지되었습니다.")
        print(f"   사용 가능한 카메라: {available}")
        print(f"   외부 웹캠으로 추정되는 카메라 인덱스 {selected}를 선택합니다.")
        return selected, available
    else:
        return available[0], available


def select_camera_interactive():
    """
    사용자에게 카메라를 선택하도록 요청합니다.
    
    Returns:
        선택된 카메라 인덱스, 사용 가능한 카메라 목록
    """
    available = find_available_cameras()
    
    if len(available) == 0:
        print("❌ 사용 가능한 카메라를 찾을 수 없습니다.")
        return None, []
    
    if len(available) == 1:
        print(f"✅ 카메라 인덱스 {available[0]}를 사용합니다.")
        return available[0], available
    
    print("\n사용 가능한 카메라:")
    for i, idx in enumerate(available):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap is not None and cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                print(f"  [{i+1}] 카메라 인덱스 {idx} ({width}x{height})")
            else:
                print(f"  [{i+1}] 카메라 인덱스 {idx} (정보 확인 불가)")
        except:
            print(f"  [{i+1}] 카메라 인덱스 {idx} (정보 확인 불가)")
    
    print(f"  [0] 자동 선택 (인덱스 {max(available)} - 외부 웹캠 추정)")
    
    while True:
        try:
            choice = input(f"\n카메라를 선택하세요 (0-{len(available)}): ").strip()
            
            if choice == '0':
                selected = max(available)
                print(f"✅ 카메라 인덱스 {selected}를 선택했습니다.")
                return selected, available
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(available):
                selected = available[choice_num - 1]
                print(f"✅ 카메라 인덱스 {selected}를 선택했습니다.")
                return selected, available
            else:
                print(f"❌ 잘못된 선택입니다. 0-{len(available)} 사이의 숫자를 입력하세요.")
        except ValueError:
            print("❌ 숫자를 입력하세요.")
        except KeyboardInterrupt:
            print("\n취소되었습니다.")
            return None, available

