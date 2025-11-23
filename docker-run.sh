#!/bin/bash
# Docker 실행 스크립트 (Mac/Linux용)

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}rPPG Docker 실행 스크립트${NC}"
echo -e "${GREEN}========================================${NC}"

# OS 확인
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Mac 환경 감지"
    # Mac에서 XQuartz 설정 확인
    if ! command -v xquartz &> /dev/null; then
        echo -e "${YELLOW}경고: XQuartz가 설치되지 않았습니다.${NC}"
        echo "설치: brew install --cask xquartz"
    fi
    DISPLAY_VAL="host.docker.internal:0"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux 환경 감지"
    DISPLAY_VAL="${DISPLAY:-:0}"
    # X11 권한 설정
    xhost +local:docker 2>/dev/null || true
else
    echo "Windows 환경 감지"
    DISPLAY_VAL=":0"
fi

# 웹캠 디바이스 확인
if [ -e /dev/video0 ]; then
    VIDEO_DEVICE="/dev/video0"
    echo "웹캠 발견: $VIDEO_DEVICE"
elif [ -e /dev/video1 ]; then
    VIDEO_DEVICE="/dev/video1"
    echo "웹캠 발견: $VIDEO_DEVICE"
else
    VIDEO_DEVICE="/dev/video0"
    echo -e "${YELLOW}경고: /dev/video0을 찾을 수 없습니다. 기본값 사용${NC}"
fi

# Docker 이미지 빌드 확인
if ! docker images | grep -q rppg; then
    echo "Docker 이미지 빌드 중..."
    docker build -t rppg:latest .
fi

# Docker 실행
echo ""
echo "Docker 컨테이너 실행 중..."
echo ""

docker run -it --rm \
    --device=$VIDEO_DEVICE:$VIDEO_DEVICE \
    -e DISPLAY=$DISPLAY_VAL \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $(pwd)/mqtt_config.json:/app/mqtt_config.json:ro \
    --network host \
    rppg:latest "$@"

# 정리 (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xhost -local:docker 2>/dev/null || true
fi

