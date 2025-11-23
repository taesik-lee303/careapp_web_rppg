# GitHub에 프로젝트 올리는 방법

## 1단계: GitHub에서 저장소 생성

1. GitHub.com에 로그인
2. 우측 상단 `+` 버튼 → `New repository` 클릭
3. 저장소 이름 입력 (예: `webcam_rppg`)
4. Public 또는 Private 선택
5. **README, .gitignore, license는 추가하지 않기** (이미 있음)
6. `Create repository` 클릭

## 2단계: 로컬에서 원격 저장소 연결

### 방법 A: 저장소가 비어있는 경우 (권장)

```bash
# 원격 저장소 URL 확인 (GitHub 저장소 페이지에서 복사)
# 예: https://github.com/your-username/webcam_rppg.git

# 기존 원격 저장소 제거 (있다면)
git remote remove origin

# 새 원격 저장소 추가
git remote add origin https://github.com/your-username/webcam_rppg.git

# 브랜치 이름 확인 및 설정
git branch -M main

# 푸시
git push -u origin main
```

### 방법 B: 저장소에 이미 파일이 있는 경우

```bash
# 원격 저장소의 내용 가져오기
git pull origin main --allow-unrelated-histories

# 충돌 해결 후
git push -u origin main
```

## 3단계: 인증

### Personal Access Token 사용 (권장)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. `Generate new token` 클릭
3. 권한 선택: `repo` (전체)
4. 토큰 생성 후 복사

```bash
# 푸시 시 토큰 사용
git push -u origin main
# Username: your-username
# Password: (토큰 붙여넣기)
```

### SSH 키 사용

```bash
# SSH 키 생성 (없는 경우)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 공개 키 복사
cat ~/.ssh/id_ed25519.pub

# GitHub → Settings → SSH and GPG keys → New SSH key에 추가

# 원격 저장소 URL을 SSH로 변경
git remote set-url origin git@github.com:your-username/webcam_rppg.git

# 푸시
git push -u origin main
```

## 4단계: 확인

GitHub 저장소 페이지에서 파일들이 올라갔는지 확인:
- https://github.com/your-username/webcam_rppg

## 문제 해결

### "Repository not found" 오류

1. 저장소 URL 확인
2. 저장소가 실제로 생성되었는지 확인
3. 권한 확인 (Private 저장소인 경우)

### "Authentication failed" 오류

1. Personal Access Token 사용
2. 또는 SSH 키 설정

### "Updates were rejected" 오류

```bash
# 원격 저장소의 변경사항 먼저 가져오기
git pull origin main --rebase

# 다시 푸시
git push -u origin main
```

## 빠른 명령어 요약

```bash
# 1. 원격 저장소 확인
git remote -v

# 2. 원격 저장소 설정 (새로 만들 경우)
git remote add origin https://github.com/your-username/webcam_rppg.git

# 3. 브랜치 확인
git branch

# 4. 푸시
git push -u origin main
```

