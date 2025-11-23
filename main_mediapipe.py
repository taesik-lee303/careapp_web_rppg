"""
rPPG 심박수 측정 메인 프로그램 (MediaPipe 버전)
로지텍 웹캠을 통해 실시간으로 심박수를 측정합니다.
"""

import cv2
import numpy as np
from rppg_mediapipe import RPPGDetector
from camera_utils import find_external_webcam, select_camera_interactive
from mqtt_client import MQTTClient, create_mqtt_client_from_config, create_mqtt_client_from_env
import time
import sys
import argparse


def draw_text_with_background(img, text, position, font_scale=0.7, 
                              font_color=(255, 255, 255), 
                              bg_color=(0, 0, 0), thickness=2):
    """
    배경이 있는 텍스트 그리기
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )
    
    # 배경 사각형 그리기
    cv2.rectangle(
        img,
        (position[0], position[1] - text_height - 10),
        (position[0] + text_width + 10, position[1] + baseline + 5),
        bg_color,
        -1
    )
    
    # 텍스트 그리기
    cv2.putText(
        img, text, (position[0] + 5, position[1] - 5),
        font, font_scale, font_color, thickness
    )


def main():
    """
    메인 함수
    """
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description='rPPG 심박수 측정 프로그램 (MediaPipe 버전)')
    parser.add_argument('camera_index', type=int, nargs='?', default=None,
                        help='카메라 인덱스 (기본값: 자동 선택)')
    parser.add_argument('--mqtt-host', type=str, default=None,
                        help='MQTT 브로커 호스트 (기본값: localhost)')
    parser.add_argument('--mqtt-port', type=int, default=None,
                        help='MQTT 브로커 포트 (기본값: 1883)')
    parser.add_argument('--mqtt-topic', type=str, default=None,
                        help='MQTT 토픽 (기본값: rppg/heart_rate)')
    parser.add_argument('--mqtt-username', type=str, default=None,
                        help='MQTT 사용자명')
    parser.add_argument('--mqtt-password', type=str, default=None,
                        help='MQTT 비밀번호')
    parser.add_argument('--no-mqtt', action='store_true',
                        help='MQTT 전송 비활성화')
    
    args = parser.parse_args()
    
    print("rPPG 심박수 측정 프로그램 시작 (MediaPipe 버전)")
    print("=" * 50)
    print("사용법:")
    print("- 웹캠 앞에 얼굴을 위치시키세요")
    print("- 조명이 충분한 환경에서 사용하세요")
    print("- 움직임을 최소화하세요")
    print("- 'q' 키를 눌러 종료하세요")
    print("=" * 50)
    
    # MQTT 클라이언트 초기화
    mqtt_client = None
    if not args.no_mqtt:
        # 우선순위: 명령줄 인수 > 설정 파일 > 환경 변수
        
        # 명령줄 인수가 있으면 직접 생성
        if args.mqtt_host or args.mqtt_port or args.mqtt_topic:
            mqtt_host = args.mqtt_host or "localhost"
            mqtt_port = args.mqtt_port or 1883
            mqtt_topic = args.mqtt_topic or "rppg/vital_signs"
            
            mqtt_client = MQTTClient(
                broker_host=mqtt_host,
                broker_port=mqtt_port,
                topic=mqtt_topic,
                username=args.mqtt_username,
                password=args.mqtt_password
            )
        else:
            # 설정 파일에서 읽기 시도
            mqtt_client = create_mqtt_client_from_config("mqtt_config.json")
            
            # 설정 파일이 없으면 환경 변수에서 읽기
            if mqtt_client is None:
                mqtt_client = create_mqtt_client_from_env()
        
        # MQTT 연결 시도
        if mqtt_client:
            mqtt_client.connect()
    
    # 카메라 선택
    camera_index = args.camera_index
    
    # 외부 웹캠 자동 찾기
    if camera_index is None:
        camera_index, available_cameras = find_external_webcam()
        if camera_index is None:
            print("❌ 오류: 사용 가능한 카메라를 찾을 수 없습니다.")
            return
        if len(available_cameras) > 1:
            print(f"\n💡 팁: 특정 카메라를 선택하려면 다음 명령어를 사용하세요:")
            print(f"   python main_mediapipe.py [카메라_인덱스]")
            print(f"   예: python main_mediapipe.py {available_cameras[0]}")
    
    # 웹캠 초기화
    print(f"\n📹 카메라 인덱스 {camera_index}를 사용합니다...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ 오류: 카메라 인덱스 {camera_index}를 열 수 없습니다.")
        print("\n사용 가능한 카메라를 확인하려면:")
        print("  python list_cameras.py")
        return
    
    # 웹캠 해상도 설정 (1080p)
    print("해상도 설정 중...")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # 실제 설정된 값 확인
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"웹캠 해상도: {width}x{height}, FPS: {fps}")
    
    # 카메라 초기화 대기 (몇 프레임 버리기)
    print("카메라 초기화 중...")
    for i in range(10):
        ret, _ = cap.read()
        if ret:
            break
        time.sleep(0.1)
    
    if not ret:
        print("❌ 오류: 카메라에서 초기 프레임을 읽을 수 없습니다.")
        print("\n가능한 원인:")
        print("- 다른 프로그램에서 웹캠을 사용 중입니다")
        print("- 웹캠 드라이버 문제")
        print("- 웹캠이 제대로 연결되지 않았습니다")
        cap.release()
        return
    
    print("✅ 카메라가 준비되었습니다.")
    
    # rPPG 감지기 초기화
    rppg = RPPGDetector(buffer_size=300, fps=fps)
    
    # 심박수 및 호흡률 표시를 위한 변수
    heart_rate_history = []
    respiration_rate_history = []
    last_update_time = time.time()
    last_mqtt_send_time = time.time()
    update_interval = 1.0  # 1초마다 업데이트
    mqtt_send_interval = 1.0  # MQTT 전송 간격: 1초
    
    print("\n측정을 시작합니다...")
    print("얼굴을 웹캠 앞에 위치시키고 조명이 충분한지 확인하세요.\n")
    
    frame_count = 0
    consecutive_failures = 0
    max_failures = 10
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    print(f"\n❌ 오류: {max_failures}번 연속으로 프레임을 읽을 수 없습니다.")
                    print("\n가능한 원인:")
                    print("- 다른 프로그램에서 웹캠을 사용 중입니다")
                    print("- 웹캠 연결이 끊어졌습니다")
                    print("- 웹캠 드라이버 문제")
                    print("\n해결 방법:")
                    print("1. 다른 프로그램에서 웹캠을 닫으세요")
                    print("2. 웹캠을 다시 연결하세요")
                    print("3. 프로그램을 재시작하세요")
                    break
                else:
                    # 일시적 오류는 무시하고 계속 시도
                    time.sleep(0.1)
                    continue
            
            # 성공적으로 프레임을 읽었으면 실패 카운터 리셋
            consecutive_failures = 0
            
            frame_count += 1
            
            # 프레임 처리
            processed_frame, roi_points, signal_value = rppg.process_frame(frame)
            
            # 신호 추가
            if signal_value is not None:
                rppg.add_signal(signal_value)
            
            # 주기적으로 심박수 및 호흡률 계산
            current_time = time.time()
            if current_time - last_update_time >= update_interval:
                heart_rate, hr_confidence = rppg.calculate_heart_rate()
                respiration_rate, rr_confidence = rppg.calculate_respiration_rate()
                
                # 심박수 처리
                if heart_rate is not None:
                    heart_rate_history.append(heart_rate)
                    if len(heart_rate_history) > 10:
                        heart_rate_history.pop(0)
                    avg_heart_rate = np.mean(heart_rate_history)
                else:
                    avg_heart_rate = None
                
                # 호흡률 처리
                if respiration_rate is not None:
                    respiration_rate_history.append(respiration_rate)
                    if len(respiration_rate_history) > 10:
                        respiration_rate_history.pop(0)
                    avg_respiration_rate = np.mean(respiration_rate_history)
                else:
                    avg_respiration_rate = None
                
                # MQTT 전송: 정확히 1초에 한번씩만 전송
                if mqtt_client and mqtt_client.connected:
                    if current_time - last_mqtt_send_time >= mqtt_send_interval:
                        mqtt_client.publish_vital_signs(
                            heart_rate=avg_heart_rate,
                            respiration_rate=avg_respiration_rate,
                            heart_confidence=hr_confidence if avg_heart_rate else 0.0,
                            respiration_confidence=0.0  # 호흡률 신뢰도는 사용 안 함
                        )
                        last_mqtt_send_time = current_time
                
                # 화면에 표시할 정보
                mqtt_status = "MQTT: ON" if mqtt_client and mqtt_client.connected else "MQTT: OFF"
                info_text = []
                
                if avg_heart_rate is not None:
                    info_text.append(f"Heart Rate: {avg_heart_rate:.1f} BPM (Conf: {hr_confidence*100:.0f}%)")
                else:
                    info_text.append("Heart Rate: 측정 중...")
                
                if avg_respiration_rate is not None:
                    info_text.append(f"Respiration: {avg_respiration_rate:.1f} RPM (Conf: {rr_confidence*100:.0f}%)")
                else:
                    info_text.append("Respiration: 측정 중... (6초 이상 필요)")
                
                info_text.extend([
                    f"Buffer: {len(rppg.signal_buffer)}/{rppg.buffer_size}",
                    f"Frame: {frame_count}",
                    mqtt_status
                ])
                
                # 정보 표시
                y_offset = 30
                for i, text in enumerate(info_text):
                    if i == 0:  # 심박수
                        color = (0, 255, 0)
                    elif i == 1:  # 호흡률
                        color = (0, 255, 255)
                    else:
                        color = (255, 255, 255)
                    draw_text_with_background(
                        processed_frame, text, (10, y_offset + i * 30),
                        font_scale=0.6, font_color=color
                    )
                
                last_update_time = current_time
            
            # 안내 메시지 표시
            if len(rppg.signal_buffer) < 60:
                progress = len(rppg.signal_buffer) / 60 * 100
                status_text = f"심박수 측정 중... {progress:.0f}%"
                draw_text_with_background(
                    processed_frame, status_text, 
                    (width // 2 - 120, height - 50),
                    font_scale=0.7, font_color=(0, 255, 255)
                )
            elif len(rppg.signal_buffer) < 180:
                progress = len(rppg.signal_buffer) / 180 * 100
                status_text = f"호흡률 측정 중... {progress:.0f}%"
                draw_text_with_background(
                    processed_frame, status_text,
                    (width // 2 - 120, height - 50),
                    font_scale=0.7, font_color=(0, 255, 255)
                )
            else:
                status_parts = []
                if len(heart_rate_history) > 0:
                    avg_hr = np.mean(heart_rate_history)
                    status_parts.append(f"HR: {avg_hr:.1f} BPM")
                if len(respiration_rate_history) > 0:
                    avg_rr = np.mean(respiration_rate_history)
                    status_parts.append(f"RR: {avg_rr:.1f} RPM")
                
                if status_parts:
                    status_text = " | ".join(status_parts)
                    draw_text_with_background(
                        processed_frame, status_text,
                        (width // 2 - 150, height - 50),
                        font_scale=0.7, font_color=(0, 255, 0)
                    )
            
            # 프레임 표시
            cv2.imshow('rPPG Heart Rate Monitor', processed_frame)
            
            # 'q' 키로 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
    
    finally:
        # 정리
        cap.release()
        cv2.destroyAllWindows()
        
        # MQTT 연결 해제
        if mqtt_client:
            mqtt_client.disconnect()
            if mqtt_client.publish_count > 0:
                print(f"\n📤 총 {mqtt_client.publish_count}개의 메시지를 MQTT로 전송했습니다.")
        
        # 최종 결과 출력
        if len(heart_rate_history) > 0:
            final_hr = np.mean(heart_rate_history)
            print(f"\n최종 평균 심박수: {final_hr:.1f} BPM")
        
        if len(respiration_rate_history) > 0:
            final_rr = np.mean(respiration_rate_history)
            print(f"최종 평균 호흡률: {final_rr:.1f} RPM")
        
        print("프로그램을 종료합니다.")


if __name__ == "__main__":
    main()

