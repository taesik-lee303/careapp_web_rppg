"""
MQTT 클라이언트 유틸리티
rPPG 측정 데이터를 MQTT 브로커로 전송합니다.
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
import paho.mqtt.client as mqtt
from typing import Optional, Callable, Dict, Any


class MQTTClient:
    def __init__(self, broker_host: str = "203.250.148.52", 
                 broker_port: int = 20516,
                 topic: str = "rppg/heart_rate",
                 client_id: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 qos: int = 0):
        """
        MQTT 클라이언트 초기화
        
        Args:
            broker_host: MQTT 브로커 호스트 주소
            broker_port: MQTT 브로커 포트
            topic: 메시지를 발행할 토픽
            client_id: 클라이언트 ID (None이면 자동 생성)
            username: MQTT 인증 사용자명 (선택사항)
            password: MQTT 인증 비밀번호 (선택사항)
            qos: Quality of Service 레벨 (0, 1, 2)
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.qos = qos
        self.connected = False
        
        # MQTT 클라이언트 생성
        if client_id is None:
            client_id = f"rppg_client_{int(time.time())}"
        
        self.client = mqtt.Client(client_id=client_id)
        
        # 인증 설정
        if username and password:
            self.client.username_pw_set(username, password)
        
        # 콜백 함수 설정
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # 연결 상태 추적
        self.last_publish_time = None
        self.publish_count = 0
    
    def _on_connect(self, client, userdata, flags, rc):
        """연결 콜백"""
        if rc == 0:
            self.connected = True
            print(f"✅ MQTT 브로커에 연결되었습니다: {self.broker_host}:{self.broker_port}")
        else:
            self.connected = False
            error_messages = {
                1: "잘못된 프로토콜 버전",
                2: "잘못된 클라이언트 식별자",
                3: "서버를 사용할 수 없음",
                4: "잘못된 사용자명 또는 비밀번호",
                5: "인증되지 않음"
            }
            error_msg = error_messages.get(rc, f"알 수 없는 오류 (코드: {rc})")
            print(f"❌ MQTT 연결 실패: {error_msg}")
    
    def _on_disconnect(self, client, userdata, rc):
        """연결 해제 콜백"""
        self.connected = False
        if rc != 0:
            print(f"⚠️  MQTT 연결이 예기치 않게 끊어졌습니다. 재연결 시도 중...")
    
    def _on_publish(self, client, userdata, mid):
        """발행 콜백"""
        self.publish_count += 1
    
    def connect(self, timeout: int = 5):
        """
        MQTT 브로커에 연결
        
        Args:
            timeout: 연결 타임아웃 (초)
            
        Returns:
            연결 성공 여부
        """
        try:
            print(f"MQTT 브로커 연결 중... ({self.broker_host}:{self.broker_port})")
            self.client.connect(self.broker_host, self.broker_port, timeout)
            self.client.loop_start()  # 백그라운드 스레드 시작
            
            # 연결 확인을 위해 잠시 대기
            time.sleep(0.5)
            
            if self.connected:
                return True
            else:
                print("⚠️  MQTT 연결에 실패했습니다. 데이터 전송 없이 계속 진행합니다.")
                return False
        except Exception as e:
            print(f"⚠️  MQTT 연결 오류: {e}")
            print("⚠️  MQTT 없이 프로그램을 계속 실행합니다.")
            return False
    
    def disconnect(self):
        """MQTT 브로커 연결 해제"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("MQTT 연결이 해제되었습니다.")
    
    def publish_heart_rate(self, heart_rate: float, confidence: float = 0.0, 
                          timestamp: Optional[float] = None):
        """
        심박수 데이터를 MQTT로 전송
        
        Args:
            heart_rate: 심박수 (BPM)
            confidence: 신뢰도 (0.0-1.0)
            timestamp: 타임스탬프 (None이면 현재 시간)
        """
        if not self.connected:
            return False
        
        if timestamp is None:
            timestamp = time.time()
        
        # JSON 메시지 생성
        message = {
            "heart_rate": round(heart_rate, 2),
            "confidence": round(confidence, 3),
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "unit": "BPM"
        }
        
        try:
            result = self.client.publish(
                self.topic,
                json.dumps(message, ensure_ascii=False),
                qos=self.qos
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.last_publish_time = timestamp
                return True
            else:
                print(f"⚠️  MQTT 발행 실패 (코드: {result.rc})")
                return False
        except Exception as e:
            print(f"⚠️  MQTT 발행 오류: {e}")
            return False
    
    def publish_vital_signs(self, heart_rate: Optional[float] = None, 
                           respiration_rate: Optional[float] = None,
                           heart_confidence: float = 0.0,
                           respiration_confidence: float = 0.0,
                           timestamp: Optional[float] = None):
        """
        생체 신호 데이터(심박수, 호흡률)를 MQTT로 전송
        심박수 신뢰도만 전송합니다.
        
        Args:
            heart_rate: 심박수 (BPM)
            respiration_rate: 호흡률 (RPM)
            heart_confidence: 심박수 신뢰도 (0.0-1.0)
            respiration_confidence: 호흡률 신뢰도 (사용 안 함)
            timestamp: 타임스탬프 (None이면 현재 시간)
        """
        if not self.connected:
            return False
        
        if timestamp is None:
            timestamp = time.time()
        
        # JSON 메시지 생성
        message = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat()
        }
        
        if heart_rate is not None:
            message["hr"] = round(heart_rate, 2)  # heart_rate → hr
            message["q"] = round(heart_confidence, 4)  # heart_rate_confidence → q (심박수 신뢰도만)
            message["hr_unit"] = "BPM"
        
        if respiration_rate is not None:
            message["rr"] = round(respiration_rate, 2)  # respiration_rate → rr
            message["rr_unit"] = "RPM"
        
        try:
            result = self.client.publish(
                self.topic,
                json.dumps(message, ensure_ascii=False),
                qos=self.qos
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.last_publish_time = timestamp
                return True
            else:
                print(f"⚠️  MQTT 발행 실패 (코드: {result.rc})")
                return False
        except Exception as e:
            print(f"⚠️  MQTT 발행 오류: {e}")
            return False
    
    def get_status(self):
        """MQTT 연결 상태 반환"""
        return {
            "connected": self.connected,
            "broker": f"{self.broker_host}:{self.broker_port}",
            "topic": self.topic,
            "publish_count": self.publish_count,
            "last_publish": self.last_publish_time
        }


def load_mqtt_config(config_path: str = "mqtt_config.json") -> Optional[Dict[str, Any]]:
    """
    MQTT 설정 파일을 읽어옵니다.
    
    Args:
        config_path: 설정 파일 경로
        
    Returns:
        설정 딕셔너리 또는 None
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"⚠️  설정 파일을 찾을 수 없습니다: {config_path}")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"❌ 설정 파일 JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 설정 파일 읽기 오류: {e}")
        return None


def create_mqtt_client_from_config(config_path: str = "mqtt_config.json") -> Optional[MQTTClient]:
    """
    설정 파일에서 MQTT 설정을 읽어 클라이언트 생성
    
    Args:
        config_path: 설정 파일 경로
        
    Returns:
        MQTTClient 인스턴스 또는 None
    """
    config = load_mqtt_config(config_path)
    
    if config is None:
        return None
    
    # MQTT 활성화 여부 확인
    if not config.get("enabled", True):
        print("ℹ️  MQTT가 설정 파일에서 비활성화되어 있습니다.")
        return None
    
    # 브로커 설정
    broker_config = config.get("broker", {})
    broker_host = broker_config.get("host", "localhost")
    broker_port = broker_config.get("port", 1883)
    username = broker_config.get("username")
    password = broker_config.get("password")
    
    # 토픽 설정
    topic_config = config.get("topic", {})
    topic_name = topic_config.get("name", "rppg/vital_signs")
    
    # QoS 설정
    qos = config.get("qos", 0)
    
    return MQTTClient(
        broker_host=broker_host,
        broker_port=broker_port,
        topic=topic_name,
        username=username,
        password=password,
        qos=qos
    )


def create_mqtt_client_from_env():
    """
    환경 변수에서 MQTT 설정을 읽어 클라이언트 생성
    
    환경 변수:
        MQTT_BROKER_HOST: 브로커 호스트 (기본값: localhost)
        MQTT_BROKER_PORT: 브로커 포트 (기본값: 1883)
        MQTT_TOPIC: 토픽 (기본값: rppg/heart_rate)
        MQTT_USERNAME: 사용자명 (선택사항)
        MQTT_PASSWORD: 비밀번호 (선택사항)
        MQTT_ENABLED: MQTT 사용 여부 (true/false, 기본값: false)
    
    Returns:
        MQTTClient 인스턴스 또는 None
    """
    # MQTT 활성화 여부 확인
    mqtt_enabled = os.getenv("MQTT_ENABLED", "false").lower() == "true"
    if not mqtt_enabled:
        return None
    
    broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
    broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    topic = os.getenv("MQTT_TOPIC", "rppg/heart_rate")
    username = os.getenv("MQTT_USERNAME", None)
    password = os.getenv("MQTT_PASSWORD", None)
    
    return MQTTClient(
        broker_host=broker_host,
        broker_port=broker_port,
        topic=topic,
        username=username,
        password=password
    )

