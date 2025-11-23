# GitHub Actions CI/CD 설정 가이드

이 프로젝트를 GitHub Actions로 자동 빌드하고 배포하는 방법입니다.

## 🚀 빠른 시작

### 1단계: GitHub Actions 자동 활성화

프로젝트를 GitHub에 푸시하면 **자동으로 GitHub Actions가 활성화**됩니다!

1. GitHub 저장소로 이동: https://github.com/taesik-lee303/careapp_web_rppg
2. `Actions` 탭 클릭
3. 첫 번째 워크플로우 실행이 자동으로 시작됩니다

### 2단계: 워크플로우 확인

`.github/workflows/ci.yml` 파일이 있으면:
- ✅ 코드 푸시 시 자동 빌드
- ✅ Pull Request 시 자동 테스트
- ✅ Docker 이미지 빌드

## 📋 현재 설정된 워크플로우

### 자동 실행 조건

- `main`, `master`, `develop` 브랜치에 푸시 시
- `main`, `master` 브랜치로 Pull Request 시
- 수동 실행 (Actions 탭에서 `Run workflow` 버튼)

### 실행되는 작업

1. **빌드 작업 (build)**
   - Python 3.9 환경 설정
   - 의존성 설치 (`requirements.txt`)
   - 코드 린팅 (flake8)
   - Docker 이미지 빌드
   - 이미지 확인

2. **Docker Hub 배포 (docker-build)** - 선택사항
   - Docker Hub 로그인
   - 이미지 빌드 및 푸시
   - 태그: `latest`, `커밋SHA`

## 🔐 Docker Hub 연동 (선택사항)

Docker Hub에 자동으로 이미지를 푸시하려면:

### 1. Docker Hub 계정 준비

1. https://hub.docker.com 에서 계정 생성 (없는 경우)
2. 로그인 확인

### 2. GitHub Secrets 설정

1. GitHub 저장소 → **Settings** 탭
2. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭
4. 다음 Secrets 추가:

   **Secret 1:**
   - Name: `DOCKER_USERNAME`
   - Value: Docker Hub 사용자명

   **Secret 2:**
   - Name: `DOCKER_PASSWORD`
   - Value: Docker Hub 비밀번호 (또는 Access Token)

### 3. Docker Hub Access Token 생성 (권장)

비밀번호 대신 Access Token 사용 권장:

1. Docker Hub → Account Settings → Security
2. New Access Token 클릭
3. 토큰 이름 입력 (예: `github-actions`)
4. 권한: `Read, Write, Delete` 선택
5. 토큰 생성 후 복사
6. GitHub Secrets의 `DOCKER_PASSWORD`에 토큰 붙여넣기

### 4. 자동 배포 확인

이제 `main` 브랜치에 푸시하면:
- Docker 이미지가 자동으로 빌드됨
- Docker Hub에 자동으로 푸시됨
- 태그: `your-username/rppg:latest`, `your-username/rppg:커밋SHA`

## 📊 워크플로우 실행 확인

### GitHub에서 확인

1. 저장소 → **Actions** 탭
2. 왼쪽에서 워크플로우 선택: **CI/CD Pipeline**
3. 실행 목록에서 최신 실행 클릭
4. 각 단계별 로그 확인

### 성공 표시

- ✅ 초록색 체크: 성공
- ❌ 빨간색 X: 실패
- 🟡 노란색 원: 진행 중

## 🔧 커스터마이징

### 특정 브랜치만 배포

`.github/workflows/ci.yml` 파일 수정:

```yaml
docker-build:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  # 또는
  if: github.ref == 'refs/heads/production'
```

### 배포 비활성화

Docker Hub 배포를 원하지 않으면:
- Secrets를 설정하지 않으면 자동으로 건너뜀 (`continue-on-error: true`)
- 또는 `docker-build` job 전체를 주석 처리

### 수동 배포만 허용

```yaml
docker-build:
  if: github.event_name == 'workflow_dispatch'
```

## 🐛 문제 해결

### 워크플로우가 실행되지 않음

1. `.github/workflows/ci.yml` 파일이 올바른 위치에 있는지 확인
2. 파일 이름이 `.yml` 또는 `.yaml`인지 확인
3. YAML 문법 오류 확인

### Docker 빌드 실패

1. Actions 탭에서 실패한 워크플로우 클릭
2. 실패한 단계의 로그 확인
3. 로컬에서 테스트: `docker build -t rppg:test .`

### Docker Hub 인증 실패

1. Secrets 이름 확인: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
2. Secrets 값이 올바른지 확인
3. Docker Hub Access Token 권한 확인

### Secrets가 적용되지 않음

1. Secrets 이름이 정확한지 확인 (대소문자 구분)
2. Secrets를 추가한 후 워크플로우를 다시 실행
3. Secrets는 워크플로우 실행 시점에만 사용 가능

## 📦 Docker Hub에서 이미지 사용

배포된 이미지를 사용하려면:

```bash
# 이미지 가져오기
docker pull your-username/rppg:latest

# 실행
docker run -it --rm \
  --device=/dev/video0:/dev/video0 \
  -v $(pwd)/mqtt_config.json:/app/mqtt_config.json:ro \
  --network host \
  your-username/rppg:latest
```

## 🎯 다음 단계

1. ✅ GitHub Actions 자동 활성화 확인
2. ⚙️ Docker Hub Secrets 설정 (선택)
3. 📝 코드 수정 후 푸시하여 자동 빌드 테스트
4. 📊 Actions 탭에서 빌드 결과 확인

## 참고 링크

- GitHub Actions 문서: https://docs.github.com/en/actions
- Docker Hub: https://hub.docker.com
- 워크플로우 파일: `.github/workflows/ci.yml`

