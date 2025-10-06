# 개발 환경 설정 문서
## 시스템 구성 및 설정 정보

*생성일: 2025년 9월 20일*

---

## 📋 목차

1. [시스템 정보](#시스템-정보)
2. [Git 설정](#git-설정)
3. [Shell 환경](#shell-환경)
4. [Conda 환경](#conda-환경)
5. [Claude Code 설정](#claude-code-설정)
6. [VSCode 통합](#vscode-통합)
7. [복원 가이드](#복원-가이드)

---

## 1. 시스템 정보

### 기본 환경
```bash
OS: Linux DESKTOP-SG45LHF 6.6.87.2-microsoft-standard-WSL2
Platform: x86_64 GNU/Linux
WSL: Ubuntu-22.04
User: naru
Shell: /bin/bash
Home: /home/naru
Working Directory: /home/naru/work/2025_Vibe
```

### 주요 환경 변수
```bash
WSL_DISTRO_NAME=Ubuntu-22.04
COLORTERM=truecolor
TERM_PROGRAM_VERSION=1.104.0
CLAUDECODE=1
ENABLE_IDE_INTEGRATION=true
LANG=C.UTF-8
```

---

## 2. Git 설정

### Global Git Config
```ini
[user]
    name = Naru Suh
    email = naru.seo.official@gmail.com
```

### Local Repository Config (2025_Vibe)
```ini
[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true

[remote "origin"]
    url = https://github.com/NaruSuh/2025_Vibe
    fetch = +refs/heads/*:refs/remotes/origin/*

[branch "Prime"]
    remote = origin
    merge = refs/heads/Prime
    vscode-merge-base = origin/Prime

[branch "html-sample"]
    remote = origin
    merge = refs/heads/html-sample
    vscode-merge-base = origin/Prime
```

---

## 3. Shell 환경

### .bashrc 주요 설정
```bash
# History settings
HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000

# Shell options
shopt -s histappend
shopt -s checkwinsize

# Color support
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# VS Code integration
export PATH="/mnt/c/Users/Naru/AppData/Local/Programs/Microsoft VS Code/bin:$PATH"

# NPM global packages
export PATH="$HOME/.npm-global/bin:$PATH"

# Custom library path
export LD_LIBRARY_PATH=/home/naru/miniconda3/envs/CUDA/lib:$LD_LIBRARY_PATH
```

### Conda 초기화
```bash
# >>> conda initialize >>>
__conda_setup="$('/home/naru/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/naru/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/naru/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/naru/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```

---

## 4. Conda 환경

### 설치 경로
- **Miniconda**: `/home/naru/miniconda3`
- **활성 환경**: CUDA
- **환경 경로**: `/home/naru/miniconda3/envs/CUDA`

### .condarc 설정
```yaml
auto_activate_base: false
```

### 알려진 이슈
- `libtinfo.so.6` 버전 정보 경고 (기능에는 영향 없음)
- `.condarc` 파일에 중복 키 오류 (auto_activate_base/auto_activate)

---

## 5. Claude Code 설정

### 기본 정보
```json
{
  "numStartups": 21,
  "installMethod": "global",
  "autoUpdates": true,
  "theme": "light",
  "hasSeenTasksHint": true,
  "promptQueueUseCount": 2,
  "hasCompletedOnboarding": true,
  "lastOnboardingVersion": "1.0.92",
  "shiftEnterKeyBindingInstalled": true
}
```

### 계정 정보
```json
{
  "accountUuid": "c24c04f8-c277-4728-8560-cda9c31340b6",
  "emailAddress": "79808@naver.com",
  "organizationUuid": "16446397-ca0c-4bb3-b2d2-42848f9891d2",
  "organizationRole": "admin",
  "organizationName": "79808@naver.com's Organization"
}
```

### 프로젝트 설정
- **현재 프로젝트**: `/home/naru/work/2025_Vibe`
- **이전 프로젝트**: `/home/naru/work/kosa-gai-2025-1st`
- **신뢰 상태**: 승인됨 (hasTrustDialogAccepted: true)
- **온보딩 완료**: 4회

### Claude 디렉토리 구조
```
~/.claude/
├── .credentials.json        # 인증 정보
├── .update.lock            # 업데이트 잠금
├── ide/                    # IDE 통합 설정
├── plugins/                # 플러그인
├── projects/               # 프로젝트별 설정
├── shell-snapshots/        # 쉘 스냅샷
├── statsig/               # 통계 데이터
└── todos/                 # Todo 리스트
```

---

## 6. VSCode 통합

### 환경 변수
```bash
VSCODE_DEBUGPY_ADAPTER_ENDPOINTS=/home/naru/.vscode-server/extensions/ms-python.debugpy-2025.10.0-linux-x64/.noConfigDebugAdapterEndpoints/endpoint-29d7a53c4c1cc009.txt
VSCODE_GIT_ASKPASS_NODE=/home/naru/.vscode-server/bin/f220831ea2d946c0dcb0f3eaa480eb435a2c1260/node
```

### 주요 기능
- Python 디버깅 지원
- Git 통합
- WSL2 GUI 앱 지원 (`WSL2_GUI_APPS_ENABLED=1`)

---

## 7. 복원 가이드

### 환경 재구성 순서

1. **시스템 설정**
   ```bash
   # WSL2 Ubuntu-22.04 설치
   # 사용자 계정: naru
   ```

2. **Miniconda 설치**
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

3. **Git 설정**
   ```bash
   git config --global user.name "Naru Suh"
   git config --global user.email "naru.seo.official@gmail.com"
   ```

4. **작업 디렉토리 설정**
   ```bash
   mkdir -p ~/work
   cd ~/work
   git clone https://github.com/NaruSuh/2025_Vibe
   ```

5. **Shell 환경 설정**
   ```bash
   # .bashrc 내용을 위의 설정으로 복원
   # PATH 및 환경 변수 설정
   ```

6. **Claude Code 설정**
   ```bash
   npm install -g @anthropic-ai/claude-code
   # 로그인 및 프로젝트 신뢰 설정
   ```

7. **VSCode 확장 설치**
   - Python extension
   - Git integration
   - WSL extension

### 백업 파일 위치
- **Git config**: `~/.gitconfig`
- **Shell config**: `~/.bashrc`
- **Claude settings**: `~/.claude.json`
- **Conda config**: `~/.condarc`

### 중요 명령어
```bash
# 환경 정보 확인
uname -a
whoami
conda info
git config --list

# Claude Code 상태 확인
claude --version
claude /status

# 프로젝트 상태 확인
git status
git remote -v
```

---

## 🔧 트러블슈팅

### 알려진 이슈 및 해결책

1. **libtinfo.so.6 경고**
   - 증상: bash 명령어 실행 시 버전 정보 없음 경고
   - 해결: 기능에 영향 없음, 무시 가능

2. **Conda 설정 충돌**
   - 증상: `.condarc`에서 중복 키 오류
   - 해결: `auto_activate_base` 키만 유지

3. **VSCode 연결 문제**
   - 증상: WSL 환경에서 VSCode 연결 실패
   - 해결: `ENABLE_IDE_INTEGRATION=true` 확인

---

*이 문서는 자동으로 생성되었으며, 환경 변경 시 업데이트가 필요합니다.*