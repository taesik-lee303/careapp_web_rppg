# rPPG 심박수 측정 프로그램

로지텍 웹캠(1080p)을 사용하여 실시간으로 심박수를 측정하는 프로그램입니다.

## 기능

- 웹캠을 통한 실시간 비디오 캡처
- 얼굴 감지 및 이마 영역(ROI) 자동 추출
- 색상 신호 분석을 통한 **심박수 및 호흡률** 측정
- 실시간 BPM 및 RPM 표시
- **MQTT를 통한 실시간 데이터 전송** (선택사항)

## 요구사항

- Python 3.8 이상
- Windows 10/11, macOS, Linux 지원
- 로지텍 웹캠 (1080p 지원)
- 충분한 조명 환경
- Docker (선택사항, Docker 사용 시)

## 설치 방법

### 방법 0: DevOps 배포 (CI/CD)

프로젝트를 GitHub, GitLab 등에 올리면 자동으로 Docker 이미지가 빌드됩니다.

**GitHub Actions 사용:**
1. GitHub 저장소에 코드 푸시
2. `.github/workflows/ci.yml` 자동 실행
3. Docker 이미지 자동 빌드 및 푸시

자세한 내용은 [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md)를 참고하세요.

### 방법 1: Docker 사용 (권장 - 모든 플랫폼 지원)

Docker를 사용하면 Windows, Mac, Linux에서 동일하게 실행할 수 있습니다.

**빠른 시작:**
```bash
# 이미지 빌드
docker build -t rppg:latest .

# 실행
docker-compose up
```

자세한 내용은 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)를 참고하세요.

### 방법 2: 직접 설치 (MediaPipe 버전 - 권장)

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

이것으로 MediaPipe 버전을 사용할 수 있습니다.

### dlib 버전 설치 (선택사항, 고급 사용자용)

⚠️ **중요**: Windows에서 dlib 설치가 매우 복잡합니다. **MediaPipe 버전을 강력히 권장합니다!**

dlib을 반드시 사용해야 하는 경우, 다음 방법 중 하나를 선택하세요:

#### 방법 1: 미리 빌드된 wheel 파일 사용 (가장 쉬움) ⭐

1. Python 버전 확인:
```bash
python --version
```

2. Python 버전에 맞는 미리 빌드된 wheel 파일 설치:
```bash
# Python 3.8-3.11 (64비트)의 경우
pip install dlib-bin

# 또는 직접 wheel 파일 다운로드
# https://github.com/sachadee/Dlib/releases 에서 Python 버전에 맞는 파일 다운로드
pip install https://github.com/sachadee/Dlib/releases/download/v19.24.2/dlib-19.24.2-cp39-cp39-win_amd64.whl
# (cp39는 Python 3.9, cp38은 Python 3.8 등으로 변경)
```

3. 얼굴 랜드마크 모델 다운로드:
   - 다운로드 링크: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   - 압축 해제 후 프로젝트 루트 디렉토리에 `shape_predictor_68_face_landmarks.dat` 파일을 저장하세요.

#### 방법 2: Conda 사용 (권장)

```bash
conda install -c conda-forge dlib
```

#### 방법 3: 소스에서 빌드 (가장 어려움)

1. **CMake 설치** (필수):
   - https://cmake.org/download/ 에서 Windows용 CMake 다운로드
   - 설치 시 "Add CMake to system PATH" 옵션을 체크하세요
   - 설치 후 새 터미널을 열고 `cmake --version` 명령어로 확인

2. **Visual Studio Build Tools 설치** (필수):
   - https://visualstudio.microsoft.com/visual-cpp-build-tools/ 에서 다운로드
   - "C++ build tools" 워크로드 설치

3. **dlib 설치**:
```bash
pip install -r requirements-dlib.txt
```

4. **얼굴 랜드마크 모델 다운로드**:
   - 다운로드 링크: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   - 압축 해제 후 프로젝트 루트 디렉토리에 `shape_predictor_68_face_landmarks.dat` 파일을 저장하세요.

## 사용 방법

### 카메라 선택

프로그램은 자동으로 외부 웹캠(로지텍 등)을 찾아 사용합니다. 여러 카메라가 연결된 경우 가장 높은 인덱스의 카메라를 선택합니다.

**사용 가능한 카메라 확인:**
```bash
python list_cameras.py
```

**특정 카메라 선택:**
```bash
# MediaPipe 버전
python main_mediapipe.py [카메라_인덱스]

# 예: 카메라 인덱스 1 사용
python main_mediapipe.py 1
```

### 방법 1: MediaPipe 버전 (권장, 설치가 쉬움)

1. 웹캠을 USB 포트에 연결합니다.

2. 프로그램 실행:
```bash
python main_mediapipe.py
```

3. 웹캠 앞에 얼굴을 위치시키고 조명이 충분한지 확인하세요.

4. 측정이 시작되면 이마 영역에 녹색 박스가 표시됩니다.

5. 'q' 키를 눌러 프로그램을 종료합니다.

### 방법 2: dlib 버전 (더 정확할 수 있음)

1. 웹캠을 USB 포트에 연결합니다.

2. dlib 모델 파일을 다운로드하여 프로젝트 루트에 저장합니다.

3. 프로그램 실행:
```bash
python main.py
```

4. 웹캠 앞에 얼굴을 위치시키고 조명이 충분한지 확인하세요.

5. 측정이 시작되면 이마 영역에 녹색 박스가 표시됩니다.

6. 'q' 키를 눌러 프로그램을 종료합니다.

### MQTT 데이터 전송

프로그램은 측정된 심박수 및 호흡률 데이터를 MQTT 브로커로 실시간 전송할 수 있습니다. **신뢰값(confidence)도 함께 전송됩니다.**

#### 설정 파일 사용 (권장) ⭐

1. **설정 파일 생성**: `mqtt_config.json` 파일을 생성하거나 `mqtt_config.example.json`을 복사합니다.

2. **설정 파일 편집**:
```json
{
  "broker": {
    "host": "203.250.148.52",
    "port": 20516,
    "username": null,
    "password": null
  },
  "topic": {
    "name": "rppg/vital_signs",
    "format": "json"
  },
  "qos": 0,
  "enabled": true
}
```

3. **프로그램 실행**:
```bash
python main_mediapipe.py
```

설정 파일이 자동으로 읽혀서 MQTT에 연결됩니다.

#### 명령줄 인수 사용

**기본 사용법 (로컬 MQTT 브로커):**
```bash
python main_mediapipe.py --mqtt-host localhost --mqtt-port 1883
```

**원격 MQTT 브로커 사용:**
```bash
python main_mediapipe.py --mqtt-host your-broker.com --mqtt-port 1883 --mqtt-topic rppg/vital_signs
```

**인증이 필요한 경우:**
```bash
python main_mediapipe.py --mqtt-host your-broker.com --mqtt-port 1883 --mqtt-username user --mqtt-password pass
```

**MQTT 비활성화:**
```bash
python main_mediapipe.py --no-mqtt
```

#### 환경 변수 사용

```bash
# Windows PowerShell
$env:MQTT_ENABLED="true"
$env:MQTT_BROKER_HOST="localhost"
$env:MQTT_BROKER_PORT="1883"
$env:MQTT_TOPIC="rppg/vital_signs"
python main_mediapipe.py
```

#### 설정 우선순위

1. **명령줄 인수** (최우선)
2. **설정 파일** (`mqtt_config.json`)
3. **환경 변수**

#### MQTT 데이터 수신 예제

다른 터미널에서 다음 명령어로 데이터를 수신할 수 있습니다:
```bash
python mqtt_example.py
```

#### 전송되는 데이터 형식

**신뢰값(confidence)이 포함된 데이터:**
```json
{
  "heart_rate": 72.5,
  "heart_rate_confidence": 0.8542,
  "heart_rate_unit": "BPM",
  "respiration_rate": 16.2,
  "respiration_rate_confidence": 0.7821,
  "respiration_rate_unit": "RPM",
  "timestamp": 1234567890.123,
  "datetime": "2024-01-01T12:00:00"
}
```

**필드 설명:**
- `heart_rate`: 심박수 (BPM)
- `heart_rate_confidence`: 심박수 신뢰도 (0.0-1.0, 높을수록 신뢰도 높음)
- `respiration_rate`: 호흡률 (RPM, 분당 호흡 수)
- `respiration_rate_confidence`: 호흡률 신뢰도 (0.0-1.0)
- `timestamp`: Unix 타임스탬프
- `datetime`: ISO 형식 날짜/시간

## 측정 가능한 생체 신호

### 심박수 (Heart Rate)
- 측정 범위: 40-200 BPM
- 측정 시간: 최소 2초
- 주파수 범위: 0.7-4.0 Hz

### 호흡률 (Respiration Rate)
- 측정 범위: 8-30 RPM (분당 호흡 수)
- 측정 시간: 최소 6초 (더 긴 시간 필요)
- 주파수 범위: 0.1-0.5 Hz
- 참고: 호흡률은 심박수보다 느린 신호이므로 더 긴 측정 시간이 필요합니다.

## 주의사항

- **조명**: 충분한 조명이 필요합니다. 어두운 환경에서는 측정 정확도가 떨어질 수 있습니다.
- **움직임**: 측정 중에는 가능한 한 움직임을 최소화하세요.
- **거리**: 웹캠과 얼굴 사이의 거리는 약 50-80cm가 적절합니다.
- **정확도**: 이 프로그램은 의료용 장비가 아니며, 참고용으로만 사용하세요.

## 작동 원리

rPPG(remote Photoplethysmography)는 웹캠을 통해 얼굴의 미세한 색상 변화를 감지하여 심박수를 측정하는 기술입니다.

1. **얼굴 감지**: MediaPipe 또는 dlib을 사용하여 얼굴을 감지합니다.
2. **ROI 추출**: 이마 영역을 관심 영역(ROI)으로 설정합니다.
3. **신호 추출**: ROI 영역의 녹색 채널 평균값을 추출합니다 (녹색 채널이 혈류 변화에 가장 민감함).
4. **신호 처리**: 밴드패스 필터(0.7-4 Hz)를 적용하여 노이즈를 제거합니다.
5. **주파수 분석**: FFT를 사용하여 주파수 도메인에서 분석합니다.
6. **심박수 계산**: 최대 파워를 가진 주파수를 찾아 BPM으로 변환합니다.

## 버전 차이

- **MediaPipe 버전** (`main_mediapipe.py`): 설치가 쉽고 Windows에서 더 안정적입니다. 별도의 모델 파일이 필요 없습니다.
- **dlib 버전** (`main.py`): 더 정확한 얼굴 랜드마크 감지가 가능하지만, Windows에서 설치가 복잡할 수 있습니다.

## 문제 해결

### dlib 설치 오류 (CMake 관련)

**오류 메시지**: "CMake is not installed on your system!"

**해결 방법**:
1. CMake를 설치하고 PATH에 추가했는지 확인하세요
2. 새 터미널을 열고 `cmake --version` 명령어로 확인
3. 그래도 안 되면 MediaPipe 버전을 사용하세요 (dlib 없이도 작동합니다)

**간단한 해결책**: MediaPipe 버전만 사용하세요!
```bash
pip install -r requirements.txt
python main_mediapipe.py
```

### 노트북 기본 카메라 대신 로지텍 웹캠을 사용하고 싶은 경우

프로그램은 자동으로 외부 웹캠을 찾아 사용합니다. 수동으로 선택하려면:

1. 사용 가능한 카메라 확인:
```bash
python list_cameras.py
```

2. 특정 카메라 인덱스 지정:
```bash
python main_mediapipe.py [카메라_인덱스]
```

예: 로지텍 웹캠이 인덱스 1이면:
```bash
python main_mediapipe.py 1
```

### 웹캠이 인식되지 않는 경우
- 다른 USB 포트에 연결해보세요.
- 다른 프로그램에서 웹캠을 사용 중인지 확인하세요.
- `python list_cameras.py`로 사용 가능한 카메라를 확인하세요.

### 얼굴이 감지되지 않는 경우
- 조명을 밝게 조정하세요.
- 웹캠과 얼굴 사이의 거리를 조정하세요.
- 얼굴이 프레임 중앙에 위치하도록 하세요.

### 심박수가 측정되지 않는 경우
- 충분한 시간(최소 2초) 동안 얼굴을 고정하세요.
- 조명을 더 밝게 하세요.
- 배경이 단순한 곳에서 측정하세요.

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

