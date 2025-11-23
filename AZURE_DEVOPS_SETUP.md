# Azure DevOps 배포 가이드

이 프로젝트를 Azure DevOps에 배포하고 CI/CD 파이프라인을 설정하는 방법입니다.

## 🚀 빠른 시작

### 1단계: Azure DevOps 프로젝트 생성

1. **Azure DevOps 포털 접속**
   - https://dev.azure.com 접속
   - Microsoft 계정으로 로그인 (없으면 생성)

2. **조직(Organization) 생성**
   - 처음 사용하는 경우 조직 이름 입력
   - 예: `taesik-lee303` 또는 원하는 이름

3. **프로젝트 생성**
   - `New project` 클릭
   - 프로젝트 이름: `careapp_web_rppg` (또는 원하는 이름)
   - Visibility: Private 또는 Public 선택
   - Version control: Git 선택
   - Work item process: Basic 선택
   - `Create` 클릭

### 2단계: Azure Repos에 코드 푸시

#### 방법 A: 기존 GitHub 저장소를 Azure DevOps에 연결

1. **Azure DevOps 프로젝트 → Repos → Files**
2. **Import repository** 클릭
3. **Import from GitHub** 선택
4. GitHub 저장소 URL 입력: `https://github.com/taesik-lee303/careapp_web_rppg.git`
5. **Import** 클릭

#### 방법 B: 로컬에서 직접 푸시

```bash
# Azure DevOps 저장소 URL 확인
# 프로젝트 → Repos → Files → Clone → HTTPS URL 복사
# 예: https://dev.azure.com/your-org/careapp_web_rppg/_git/careapp_web_rppg

# 기존 원격 저장소 확인
git remote -v

# Azure DevOps 원격 저장소 추가
git remote add azure https://dev.azure.com/your-org/careapp_web_rppg/_git/careapp_web_rppg

# 또는 기존 origin을 Azure DevOps로 변경
git remote set-url origin https://dev.azure.com/your-org/careapp_web_rppg/_git/careapp_web_rppg

# 푸시
git push -u azure main
# 또는
git push -u origin main
```

**인증 방법:**
- Personal Access Token (PAT) 사용 권장
- 또는 Azure DevOps Credential Manager 사용

### 3단계: Personal Access Token 생성

1. **Azure DevOps → 사용자 설정 (우측 상단 프로필) → Personal access tokens**
2. **+ New Token** 클릭
3. 설정:
   - Name: `git-push-token` (또는 원하는 이름)
   - Organization: 선택
   - Expiration: 원하는 기간 선택
   - Scopes: **Code (read & write)** 선택
4. **Create** 클릭
5. **토큰 복사** (한 번만 표시됨!)
6. 푸시 시 비밀번호에 토큰 붙여넣기

### 4단계: CI/CD 파이프라인 생성

1. **Azure DevOps 프로젝트 → Pipelines → Pipelines**
2. **Create Pipeline** 클릭
3. **Azure Repos Git** 선택
4. 저장소 선택: `careapp_web_rppg`
5. **Existing Azure Pipelines YAML file** 선택
6. Branch: `main` 선택
7. Path: `/azure-pipelines.yml` 선택
8. **Continue** 클릭
9. **Run** 클릭하여 첫 번째 빌드 실행

### 5단계: Docker Registry 연결 (선택사항)

Docker Hub 또는 Azure Container Registry에 이미지를 푸시하려면:

#### Docker Hub 연결

1. **Project Settings → Service connections**
2. **Create service connection** 클릭
3. **Docker Registry** 선택
4. **Docker Hub** 선택
5. Docker Hub 사용자명과 비밀번호 입력
6. Service connection name: `Docker Hub` 입력
7. **Save** 클릭

#### Azure Container Registry (ACR) 연결

1. Azure Portal에서 Container Registry 생성 (없는 경우)
2. **Service connections → Create service connection**
3. **Azure Container Registry** 선택
4. 구독 및 레지스트리 선택
5. **Save** 클릭

### 6단계: 파이프라인 변수 설정 (선택사항)

1. **Pipelines → Pipelines → 파이프라인 선택 → Edit**
2. **Variables** 탭 클릭
3. **+ New variable** 클릭하여 변수 추가:
   - `DOCKER_REGISTRY`: `your-registry.azurecr.io` 또는 `docker.io`
   - `IMAGE_NAME`: `rppg`
   - 기타 필요한 변수

## 📋 파이프라인 구조

현재 `azure-pipelines.yml` 파일은 다음 단계를 포함합니다:

1. **Build Stage**: Docker 이미지 빌드
2. **Test Stage**: 이미지 테스트
3. **Deploy Stage**: 레지스트리에 푸시

## 🔧 파이프라인 커스터마이징

### 특정 브랜치만 빌드

`azure-pipelines.yml` 파일 수정:

```yaml
trigger:
  branches:
    include:
      - main
      - production
```

### Docker Hub에 푸시

`azure-pipelines.yml`의 Deploy 단계에서:

```yaml
- task: Docker@2
  displayName: 'Push to Docker Hub'
  inputs:
    command: push
    repository: your-username/rppg
    containerRegistry: 'Docker Hub'
    tags: |
      latest
      $(Build.BuildId)
```

### Azure Container Registry에 푸시

```yaml
- task: Docker@2
  displayName: 'Push to ACR'
  inputs:
    command: push
    repository: rppg
    containerRegistry: 'Azure Container Registry'
    tags: |
      latest
      $(Build.BuildId)
```

## 🐛 문제 해결

### 파이프라인이 실행되지 않음

1. `azure-pipelines.yml` 파일이 저장소 루트에 있는지 확인
2. YAML 문법 오류 확인
3. 파이프라인 편집기에서 "Validate" 클릭

### Docker 빌드 실패

1. 파이프라인 실행 로그 확인
2. 로컬에서 테스트: `docker build -t rppg:test .`
3. Dockerfile 경로 확인

### 인증 실패

1. Service connection이 올바르게 설정되었는지 확인
2. Personal Access Token 권한 확인
3. Docker Registry 자격 증명 확인

### 권한 오류

1. **Project Settings → Permissions** 확인
2. Build Service 계정에 권한 부여
3. Service connection 권한 확인

## 📊 파이프라인 실행 확인

### Azure DevOps에서 확인

1. **Pipelines → Pipelines** 탭
2. 파이프라인 선택
3. 최신 실행 클릭
4. 각 단계별 로그 확인

### 성공 표시

- ✅ 초록색 체크: 성공
- ❌ 빨간색 X: 실패
- 🟡 노란색 원: 진행 중

## 🔄 자동 실행

파이프라인은 다음 경우에 자동으로 실행됩니다:

- `main`, `master`, `develop` 브랜치에 푸시 시
- Pull Request 생성 시 (설정된 경우)
- 수동 실행 (Run pipeline 버튼)

## 📦 배포된 이미지 사용

### Docker Hub에서

```bash
docker pull your-username/rppg:latest
```

### Azure Container Registry에서

```bash
# 로그인
az acr login --name your-registry-name

# 이미지 가져오기
docker pull your-registry.azurecr.io/rppg:latest
```

## 🎯 다음 단계

1. ✅ Azure DevOps 프로젝트 생성
2. ✅ 코드 푸시
3. ✅ 파이프라인 생성 및 실행
4. ✅ Docker Registry 연결 (선택)
5. ✅ 자동 빌드 및 배포 확인

## 참고 링크

- Azure DevOps 문서: https://docs.microsoft.com/azure/devops
- Azure Pipelines: https://docs.microsoft.com/azure/devops/pipelines
- Azure Container Registry: https://docs.microsoft.com/azure/container-registry

