"""
로지텍 웹캠 연결 테스트 프로그램
웹캠이 제대로 연결되어 있고 작동하는지 확인합니다.
"""

import cv2
import sys


def test_webcam():
    """
    웹캠 연결 및 작동 상태를 테스트합니다.
    """
    print("=" * 50)
    print("로지텍 웹캠 연결 테스트")
    print("=" * 50)
    
    # 카메라 선택
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
            print(f"\n명령줄 인수로 카메라 인덱스 {camera_index}를 지정했습니다.")
        except ValueError:
            print(f"\n⚠️  경고: 잘못된 카메라 인덱스. 기본값 0을 사용합니다.")
    
    # 웹캠 초기화
    print(f"\n1. 웹캠 초기화 중 (인덱스 {camera_index})...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("❌ 오류: 웹캠을 열 수 없습니다.")
        print("\n가능한 원인:")
        print("- 웹캠이 USB 포트에 제대로 연결되지 않았습니다")
        print("- 다른 프로그램에서 웹캠을 사용 중입니다")
        print("- 웹캠 드라이버가 설치되지 않았습니다")
        return False
    
    print("✅ 웹캠이 성공적으로 열렸습니다!")
    
    # 웹캠 정보 확인
    print("\n2. 웹캠 정보 확인 중...")
    
    # 기본 해상도 확인
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"   현재 해상도: {width}x{height}")
    print(f"   현재 FPS: {fps}")
    
    # 1080p로 설정 시도
    print("\n3. 1080p 해상도 설정 시도 중...")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # 실제 설정된 값 확인
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"   설정된 해상도: {actual_width}x{actual_height}")
    print(f"   설정된 FPS: {actual_fps}")
    
    if actual_width == 1920 and actual_height == 1080:
        print("   ✅ 1080p 해상도가 성공적으로 설정되었습니다!")
    else:
        print(f"   ⚠️  경고: 1080p 설정이 지원되지 않습니다. 현재 해상도: {actual_width}x{actual_height}")
        print("   (이 해상도로도 rPPG 측정은 가능합니다)")
    
    # 프레임 읽기 테스트
    print("\n4. 프레임 읽기 테스트 중...")
    ret, frame = cap.read()
    
    if not ret:
        print("❌ 오류: 프레임을 읽을 수 없습니다.")
        cap.release()
        return False
    
    print(f"   ✅ 프레임 읽기 성공! 프레임 크기: {frame.shape}")
    
    # 웹캠 미리보기 표시
    print("\n5. 웹캠 미리보기 시작...")
    print("   - 웹캠 화면이 표시됩니다")
    print("   - 'q' 키를 눌러 종료하세요")
    print("   - ESC 키를 눌러도 종료됩니다\n")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ 오류: 프레임을 읽을 수 없습니다.")
                break
            
            frame_count += 1
            
            # 정보 텍스트 추가
            info_text = [
                f"Webcam Test - Frame: {frame_count}",
                f"Resolution: {actual_width}x{actual_height}",
                f"FPS: {actual_fps}",
                "Press 'q' or ESC to exit"
            ]
            
            y_offset = 30
            for i, text in enumerate(info_text):
                cv2.putText(
                    frame, text, (10, y_offset + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )
            
            # 프레임 표시
            cv2.imshow('Webcam Test - Press Q or ESC to exit', frame)
            
            # 'q' 또는 ESC 키로 종료
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 27 is ESC
                break
    
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    
    finally:
        # 정리
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 50)
        print("테스트 완료!")
        print("=" * 50)
        print(f"총 {frame_count}개 프레임을 읽었습니다.")
        print("\n✅ 웹캠이 정상적으로 작동하고 있습니다!")
        print("이제 rPPG 측정 프로그램을 실행할 수 있습니다:")
        print("  python main_mediapipe.py")
        print("=" * 50)
    
    return True


if __name__ == "__main__":
    try:
        success = test_webcam()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

