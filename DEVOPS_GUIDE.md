# DevOps 배포 가이드

이 프로젝트를 다양한 DevOps 플랫폼에 배포하는 방법을 설명합니다.

## 지원하는 플랫폼

1. **GitHub Actions** ⭐ (가장 일반적)
2. **GitLab CI/CD**
3. **Azure DevOps**
4. **Jenkins**

## GitHub Actions 사용 (권장)

### 1. GitHub 저장소 생성

```bash
# 로컬에서
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/webcam_rppg.git
git push -u origin main
```

### 2. GitHub Actions 활성화

1. GitHub 저장소로 이동
2. `Actions` 탭 클릭
3. `.github/workflows/ci.yml` 파일이 자동으로 감지됨
4. 워크플로우 실행 확인

### 3. Docker Hub 연동 (선택사항)

Docker Hub에 이미지를 푸시하려면:

1. GitHub 저장소 → Settings → Secrets → Actions
2. 다음 Secrets 추가:
   - `DOCKER_USERNAME`: Docker Hub 사용자명
   - `DOCKER_PASSWORD`: Docker Hub 비밀번호

### 4. 자동 빌드

이제 `main` 브랜치에 푸시하면 자동으로:
- Docker 이미지 빌드
- 테스트 실행
- Docker Hub에 푸시 (설정 시)

## GitLab CI/CD 사용

### 1. GitLab 저장소 생성

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://gitlab.com/your-username/webcam_rppg.git
git push -u origin main
```

### 2. GitLab Runner 설정

GitLab에서 자동으로 CI/CD 파이프라인이 실행됩니다.

### 3. Container Registry 사용

GitLab Container Registry에 자동으로 푸시됩니다:
- `registry.gitlab.com/your-username/webcam_rppg:latest`

## Azure DevOps 사용

### 1. Azure DevOps 프로젝트 생성

1. Azure DevOps 포털 접속
2. 새 프로젝트 생성
3. 저장소 연결

### 2. Pipeline 생성

1. Pipelines → New Pipeline
2. Azure Repos Git 선택
3. `azure-pipelines.yml` 파일 선택
4. Run 실행

### 3. Docker Registry 연결

Service Connections에서 Docker Hub 또는 Azure Container Registry 연결

## Jenkins 사용

### 1. Jenkins 설정

1. Jenkins 설치
2. Docker 플러그인 설치
3. Pipeline 프로젝트 생성
4. `Jenkinsfile` 사용

### 2. Credentials 설정

Docker Hub 인증 정보를 Jenkins Credentials에 추가:
- ID: `docker-hub`
- Username: Docker Hub 사용자명
- Password: Docker Hub 비밀번호

## 배포 전 체크리스트

### 필수 확인 사항

- [ ] `.gitignore` 파일 확인 (불필요한 파일 제외)
- [ ] `mqtt_config.json`에 민감한 정보가 없음 (Secrets 사용 권장)
- [ ] Dockerfile이 올바르게 설정됨
- [ ] CI/CD 파이프라인 파일이 올바른 브랜치에 있음

### 보안 권장사항

1. **민감한 정보는 Secrets 사용**
   - MQTT 브로커 비밀번호
   - Docker Hub 비밀번호
   - API 키 등

2. **환경 변수로 설정 관리**
   ```yaml
   # CI/CD에서 환경 변수로 주입
   environment:
     MQTT_BROKER_HOST: ${{ secrets.MQTT_BROKER_HOST }}
     MQTT_BROKER_PASSWORD: ${{ secrets.MQTT_BROKER_PASSWORD }}
   ```

3. **.gitignore 확인**
   - `mqtt_config.json`에 비밀번호가 있다면 제외하거나
   - `mqtt_config.example.json`만 커밋

## 배포 후 사용

### Docker Hub에서 이미지 가져오기

```bash
# Docker Hub에서 이미지 가져오기
docker pull your-username/rppg:latest

# 실행
docker run -it --rm \
  --device=/dev/video0:/dev/video0 \
  -v $(pwd)/mqtt_config.json:/app/mqtt_config.json:ro \
  --network host \
  your-username/rppg:latest
```

### GitLab Container Registry에서 가져오기

```bash
docker pull registry.gitlab.com/your-username/webcam_rppg:latest
```

## CI/CD 파이프라인 커스터마이징

### 빌드만 실행 (배포 제외)

`.github/workflows/ci.yml`에서 `docker-build` job을 제거하거나 `continue-on-error: true`로 설정

### 특정 브랜치만 배포

```yaml
only:
  - main
  - production
```

### 수동 배포 활성화

```yaml
deploy:
  when: manual  # GitLab
  # 또는
  workflow_dispatch:  # GitHub Actions
```

## 문제 해결

### Docker 빌드 실패

- Dockerfile 문법 확인
- 빌드 로그 확인
- 로컬에서 먼저 테스트: `docker build -t rppg:test .`

### Secrets 인증 실패

- Secrets 이름 확인
- 권한 확인
- 값이 올바른지 확인

### 웹훅 설정

GitHub/GitLab에서 웹훅을 통해 다른 서비스로 알림을 받을 수 있습니다.

## 참고 자료

- GitHub Actions: https://docs.github.com/en/actions
- GitLab CI/CD: https://docs.gitlab.com/ee/ci/
- Azure DevOps: https://docs.microsoft.com/azure/devops
- Jenkins: https://www.jenkins.io/doc/

