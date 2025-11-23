# Docker를 사용한 rPPG 프로그램 실행 가이드

이 가이드는 Docker를 사용하여 Windows, Mac, Linux에서 rPPG 프로그램을 실행하는 방법을 설명합니다.

## 사전 요구사항

1. **Docker Desktop 설치**
   - Windows/Mac: https://www.docker.com/products/docker-desktop
   - Linux: `sudo apt-get install docker.io docker-compose`

2. **웹캠 연결 확인**

## 빠른 시작

### 1. Docker 이미지 빌드

```bash
docker build -t rppg:latest .
```

### 2. Docker Compose로 실행 (권장)

```bash
docker-compose up
```

### 3. 직접 Docker로 실행

#### Mac/Linux

```bash
# X11 forwarding 설정 (GUI 표시용)
xhost +local:docker

# Docker 실행
docker run -it --rm \
  --device=/dev/video0 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/mqtt_config.json:/app/mqtt_config.json:ro \
  --network host \
  rppg:latest
```

#### Windows

```bash
# Windows에서는 X11 forwarding이 필요 없습니다
docker run -it --rm \
  --device=/dev/video0 \
  -v %cd%/mqtt_config.json:/app/mqtt_config.json:ro \
  --network host \
  rppg:latest
```

## 환경 변수 설정

### Docker Compose 사용 시

`docker-compose.yml` 파일을 편집하거나 환경 변수로 설정:

```bash
export MQTT_BROKER_HOST=your-broker.com
export MQTT_BROKER_PORT=1883
docker-compose up
```

### 직접 실행 시

```bash
docker run -it --rm \
  -e MQTT_BROKER_HOST=your-broker.com \
  -e MQTT_BROKER_PORT=1883 \
  -e MQTT_TOPIC=rppg/vital_signs \
  --device=/dev/video0 \
  rppg:latest
```

## 웹캠 디바이스 확인

### Mac/Linux

```bash
# 사용 가능한 웹캠 확인
ls -la /dev/video*

# 일반적으로 /dev/video0이 기본 웹캠입니다
```

### Windows

Windows에서는 Docker Desktop의 WSL2 백엔드를 사용하는 경우:

```bash
# WSL2에서 확인
ls /dev/video*
```

## 문제 해결

### 웹캠이 인식되지 않는 경우

1. **Mac/Linux**: 디바이스 권한 확인
```bash
# 권한 확인
ls -l /dev/video0

# 필요시 권한 부여
sudo chmod 666 /dev/video0
```

2. **Docker 실행 시 디바이스 지정**
```bash
# 특정 웹캠 사용
docker run -it --rm \
  --device=/dev/video1 \  # video1 사용
  ...
```

### GUI가 표시되지 않는 경우 (Mac/Linux)

1. **X11 forwarding 설정**
```bash
# Mac (XQuartz 필요)
brew install --cask xquartz
xhost +localhost

# Linux
xhost +local:docker
```

2. **DISPLAY 환경 변수 확인**
```bash
echo $DISPLAY
# Mac: :0 또는 localhost:0
# Linux: :0
```

### MQTT 연결 실패

1. **네트워크 모드 확인**
   - `--network host` 옵션 사용
   - 또는 `docker-compose.yml`에서 `network_mode: host` 확인

2. **방화벽 설정 확인**
   - MQTT 브로커 포트가 열려있는지 확인

## Docker Compose 설정 커스터마이징

`docker-compose.yml` 파일을 편집하여 설정을 변경할 수 있습니다:

```yaml
services:
  rppg:
    environment:
      - MQTT_BROKER_HOST=your-broker.com
      - MQTT_BROKER_PORT=1883
    devices:
      - /dev/video0:/dev/video0  # 웹캠 디바이스 변경 가능
```

## 빌드 옵션

### 특정 Python 버전 사용

`Dockerfile`에서 베이스 이미지 변경:

```dockerfile
FROM python:3.10-slim  # 또는 3.11, 3.12 등
```

### 개발 모드 (볼륨 마운트)

코드 변경사항을 즉시 반영하려면:

```yaml
volumes:
  - .:/app  # 전체 프로젝트 마운트
```

## 주의사항

1. **웹캠 접근**: Docker 컨테이너에서 웹캠에 접근하려면 `--device` 옵션이 필요합니다.

2. **GUI 표시**: Mac/Linux에서 GUI를 표시하려면 X11 forwarding이 필요합니다.

3. **성능**: Docker 컨테이너 내에서 실행하면 네이티브 실행보다 약간 느릴 수 있습니다.

4. **권한**: 일부 시스템에서는 Docker 실행 시 sudo 권한이 필요할 수 있습니다.

## 참고

- Docker Desktop: https://www.docker.com/products/docker-desktop
- Docker Compose: https://docs.docker.com/compose/

