# MacBook에서 프로젝트 실행 가이드

Windows 노트북에서 MacBook으로 프로젝트를 옮겨서 실행하는 방법입니다.

## 필수 파일 (반드시 전송)

### 1. 핵심 프로그램 파일
- ✅ `main_mediapipe.py` - 메인 실행 파일 (MediaPipe 버전)
- ✅ `rppg_mediapipe.py` - rPPG 측정 모듈
- ✅ `mqtt_client.py` - MQTT 클라이언트
- ✅ `camera_utils.py` - 카메라 유틸리티

### 2. 설정 파일
- ✅ `mqtt_config.json` - MQTT 설정 파일
- ✅ `requirements.txt` - Python 패키지 목록

### 3. Docker 파일 (Docker 사용 시)
- ✅ `Dockerfile` - Docker 이미지 빌드 파일
- ✅ `docker-compose.yml` - Docker Compose 설정
- ✅ `.dockerignore` - Docker 빌드 제외 파일

## 선택적 파일 (선택사항)

### 유틸리티 파일 (있으면 좋음)
- `test_webcam.py` - 웹캠 테스트
- `list_cameras.py` - 카메라 목록 확인
- `mqtt_example.py` - MQTT 수신 예제

### 문서 파일
- `README.md` - 사용 설명서
- `DOCKER_GUIDE.md` - Docker 가이드
- `파일_정리_가이드.md` - 파일 정리 가이드

### dlib 버전 (사용 안 할 시 제외 가능)
- ❌ `main.py` - dlib 버전 (MediaPipe만 사용 시 불필요)
- ❌ `rppg.py` - dlib 버전 (MediaPipe만 사용 시 불필요)
- ❌ `requirements-dlib.txt` - dlib 패키지 목록
- ❌ `install_dlib_windows.md` - dlib 설치 가이드
- ❌ `shape_predictor_68_face_landmarks.dat` - dlib 모델 파일 (약 100MB)

## 최소 구성 (가장 간단)

MacBook에서 실행하기 위한 최소 파일:

```
필수 파일:
├── main_mediapipe.py
├── rppg_mediapipe.py
├── mqtt_client.py
├── camera_utils.py
├── mqtt_config.json
├── requirements.txt
└── Dockerfile (또는 docker-compose.yml)

선택 파일:
├── README.md
├── test_webcam.py
└── list_cameras.py
```

## 전송 방법

### 방법 1: Git 사용 (권장)

```bash
# Windows에서
git init
git add .
git commit -m "Initial commit"

# GitHub/GitLab 등에 푸시하거나
# MacBook에서 클론
```

### 방법 2: 압축 파일

```bash
# Windows에서 압축 (필수 파일만)
# PowerShell
Compress-Archive -Path main_mediapipe.py,rppg_mediapipe.py,mqtt_client.py,camera_utils.py,mqtt_config.json,requirements.txt,Dockerfile,docker-compose.yml -DestinationPath rppg_project.zip

# 또는 전체 프로젝트 (dlib 파일 제외)
Compress-Archive -Path * -Exclude main.py,rppg.py,requirements-dlib.txt,install_dlib_windows.md,shape_predictor_68_face_landmarks.dat -DestinationPath rppg_project.zip
```

### 방법 3: USB/클라우드

필수 파일들을 USB나 클라우드 드라이브(Google Drive, Dropbox 등)로 전송

## MacBook에서 설정

### 1. 파일 받기
압축 파일을 받아서 압축 해제

### 2. Docker 설치 확인
```bash
docker --version
docker-compose --version
```

### 3. 실행
```bash
# Docker Compose 사용 (권장)
docker-compose up

# 또는 직접 실행
docker build -t rppg:latest .
docker run -it --rm \
  --device=/dev/video0:/dev/video0 \
  -v $(pwd)/mqtt_config.json:/app/mqtt_config.json:ro \
  --network host \
  rppg:latest
```

## 빠른 체크리스트

전송 전 확인:
- [ ] `main_mediapipe.py` 포함
- [ ] `rppg_mediapipe.py` 포함
- [ ] `mqtt_client.py` 포함
- [ ] `camera_utils.py` 포함
- [ ] `mqtt_config.json` 포함
- [ ] `requirements.txt` 포함
- [ ] `Dockerfile` 또는 `docker-compose.yml` 포함

## 주의사항

1. **dlib 파일은 크기가 큼** (약 100MB)
   - MediaPipe만 사용한다면 전송 불필요

2. **mqtt_config.json 설정 확인**
   - MacBook에서도 동일한 MQTT 브로커 사용 가능한지 확인

3. **웹캠 디바이스 경로**
   - Mac에서는 `/dev/video0`이 아닐 수 있음
   - `list_cameras.py`로 확인 가능

