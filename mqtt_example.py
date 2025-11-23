"""
MQTT 구독 예제
rPPG 프로그램에서 전송하는 심박수 데이터를 수신하는 예제입니다.
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime


def on_connect(client, userdata, flags, rc):
    """연결 콜백"""
    if rc == 0:
        print("✅ MQTT 브로커에 연결되었습니다.")
        # 토픽 구독
        client.subscribe("rppg/heart_rate")
        print("📡 'rppg/heart_rate' 토픽을 구독합니다...")
    else:
        print(f"❌ 연결 실패 (코드: {rc})")


def on_message(client, userdata, msg):
    """메시지 수신 콜백"""
    try:
        # JSON 메시지 파싱
        data = json.loads(msg.payload.decode())
        
        timestamp = data.get("timestamp")
        dt = data.get("datetime")
        
        print(f"\n📊 생체 신호 데이터 수신:")
        print(f"   시간: {dt}")
        
        # 심박수 데이터
        if "hr" in data:
            heart_rate = data.get("hr")
            hr_confidence = data.get("q", 0.0)
            print(f"   심박수: {heart_rate} BPM (신뢰도: {hr_confidence*100:.1f}%)")
        
        # 호흡률 데이터
        if "rr" in data:
            respiration_rate = data.get("rr")
            print(f"   호흡률: {respiration_rate} RPM")
        
    except Exception as e:
        print(f"❌ 메시지 파싱 오류: {e}")


def main():
    """메인 함수"""
    print("=" * 50)
    print("MQTT 생체 신호 데이터 수신기")
    print("=" * 50)
    print("\n이 프로그램은 rPPG 측정 프로그램에서 전송하는")
    print("심박수 및 호흡률 데이터를 MQTT를 통해 수신합니다.\n")
    
    # MQTT 브로커 설정
    broker_host = input("MQTT 브로커 주소 (기본값: localhost): ").strip() or "localhost"
    broker_port = int(input("MQTT 브로커 포트 (기본값: 1883): ").strip() or "1883")
    
    # MQTT 클라이언트 생성
    client = mqtt.Client(client_id="rppg_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # 브로커 연결
        print(f"\n연결 중... ({broker_host}:{broker_port})")
        client.connect(broker_host, broker_port, 60)
        
        # 메시지 루프 시작
        print("\n데이터 수신 대기 중... (Ctrl+C로 종료)\n")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        client.disconnect()
    except Exception as e:
        print(f"\n❌ 오류: {e}")


if __name__ == "__main__":
    main()

