@echo off
REM Docker 실행 스크립트 (Windows용)

echo ========================================
echo rPPG Docker 실행 스크립트
echo ========================================

REM Docker 이미지 빌드 확인
docker images | findstr rppg >nul
if errorlevel 1 (
    echo Docker 이미지 빌드 중...
    docker build -t rppg:latest .
)

REM 웹캠 디바이스 확인 (Windows에서는 WSL2 사용 시)
echo 웹캠 디바이스 확인 중...

REM Docker 실행
echo.
echo Docker 컨테이너 실행 중...
echo.

docker run -it --rm ^
    --device=/dev/video0:/dev/video0 ^
    -v %cd%/mqtt_config.json:/app/mqtt_config.json:ro ^
    --network host ^
    rppg:latest %*

pause

