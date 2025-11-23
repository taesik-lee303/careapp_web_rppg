# Windows에서 dlib 설치 가이드

Windows에서 dlib 설치가 실패하는 경우, 다음 방법들을 시도해보세요.

## ⚠️ 중요: MediaPipe 버전 사용 권장

dlib 설치가 어렵다면 **MediaPipe 버전을 사용하세요**. 기능상 차이가 거의 없고 설치가 훨씬 쉽습니다:

```bash
pip install -r requirements.txt
python main_mediapipe.py
```

## dlib 설치 방법

### 방법 1: 미리 빌드된 wheel 파일 사용 (가장 쉬움) ⭐

1. Python 버전 확인:
```bash
python --version
```

2. Python 버전에 맞는 wheel 파일 설치:

**옵션 A: dlib-bin 사용**
```bash
pip install dlib-bin
```

**옵션 B: GitHub에서 직접 다운로드**
- https://github.com/sachadee/Dlib/releases 방문
- Python 버전에 맞는 wheel 파일 다운로드
- 예: Python 3.9 64비트 → `dlib-19.24.2-cp39-cp39-win_amd64.whl`
- 설치:
```bash
pip install dlib-19.24.2-cp39-cp39-win_amd64.whl
```

**옵션 C: 직접 URL로 설치**
```bash
# Python 3.8
pip install https://github.com/sachadee/Dlib/releases/download/v19.24.2/dlib-19.24.2-cp38-cp38-win_amd64.whl

# Python 3.9
pip install https://github.com/sachadee/Dlib/releases/download/v19.24.2/dlib-19.24.2-cp39-cp39-win_amd64.whl

# Python 3.10
pip install https://github.com/sachadee/Dlib/releases/download/v19.24.2/dlib-19.24.2-cp310-cp310-win_amd64.whl

# Python 3.11
pip install https://github.com/sachadee/Dlib/releases/download/v19.24.2/dlib-19.24.2-cp311-cp311-win_amd64.whl
```

### 방법 2: Conda 사용 (권장)

Conda를 사용하는 경우:

```bash
conda install -c conda-forge dlib
```

### 방법 3: 소스에서 빌드 (가장 어려움)

소스에서 빌드하려면 다음이 필요합니다:

1. **CMake 설치**
   - https://cmake.org/download/ 에서 다운로드
   - 설치 시 "Add CMake to system PATH" 체크
   - 새 터미널에서 `cmake --version` 확인

2. **Visual Studio Build Tools 설치**
   - https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - "C++ build tools" 워크로드 설치

3. **dlib 설치**
```bash
pip install dlib
```

## 얼굴 랜드마크 모델 다운로드

dlib 설치 후, 얼굴 랜드마크 모델을 다운로드해야 합니다:

1. 다운로드: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
2. 압축 해제 (7-Zip 등 사용)
3. 프로젝트 루트 디렉토리에 `shape_predictor_68_face_landmarks.dat` 파일 저장

## 문제 해결

### "Failed building wheel for dlib" 오류

이 오류는 CMake나 Visual Studio Build Tools가 없을 때 발생합니다. **방법 1 (미리 빌드된 wheel)** 또는 **방법 2 (Conda)**를 사용하세요.

### "CMake is not installed" 오류

CMake를 설치하거나, 미리 빌드된 wheel 파일을 사용하세요.

### Python 버전 확인

```bash
python --version
python -c "import sys; print(sys.version)"
```

32비트 Python은 지원되지 않습니다. 64비트 Python을 사용하세요.

