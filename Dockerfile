# rPPG 측정 프로그램을 위한 Dockerfile
# Windows, Mac, Linux 모두 지원

FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (OpenCV 및 GUI 관련)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libv4l-dev \
    v4l-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY *.py ./
COPY *.json ./
COPY *.md ./

# shape_predictor 파일이 있으면 복사 (dlib 버전 사용 시, 선택사항)
COPY shape_predictor_68_face_landmarks.dat* ./ 2>/dev/null || true

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# 웹캠 접근을 위한 권한 설정
RUN usermod -a -G video root

# 실행 (기본값은 MediaPipe 버전)
CMD ["python", "main_mediapipe.py"]

