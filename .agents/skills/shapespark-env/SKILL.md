# Shapespark 및 시스템 스크립트 실행 스킬 (Shapespark & System Script Skill)

이 스킬은 워크스페이스 내에서 3D 웹 환경(Shapespark)을 제어하거나 터미널을 통해 PowerShell, Python 스크립트를 실행할 때만 활성화하여 적용합니다.

---

## 🏗️ 1. Shapespark 최우선 동작 원칙
- 모든 기능 구현의 1순위 기준은 **"Shapespark 웹뷰/에디터 환경에서의 정상 동작"**입니다.
- 새로운 기능을 추가하기 전, 현재 Shapespark API 및 3D 신(Scene)에 오류가 없는지 먼저 터미널이나 로그로 확인하십시오.
- 오류가 발견되면 다른 기능 개발을 전면 중단하고, 해당 에러부터 외과적으로 정밀하게 수정한 뒤 다음 단계로 진행하십시오.

---

## 💻 2. 터미널 및 OS 실행 제약 (Terminal Executions)
- **로컬 의존성 관리:** 글로벌 설치 명령(`npm install -g` 등)은 금지합니다. 필요한 패키지는 무조건 로컬에만 수동 배치하거나 설치하십시오.
- **PowerShell 우회 및 권한 처리:** 
  - 윈도우 환경에서 `.ps1` 스크립트를 실행할 때는 무조건 `PowerShell -ExecutionPolicy Bypass -File [파일명]` 구조를 사용하십시오.
  - 권한 오류(Permission Error)가 발생하면, 즉시 `cmd /c [명령어]` 형태로 우회(Fallback)하여 실행하십시오.

---

## 🐍 3. 파이썬 실행 규칙 (Python I/O Controls)

+ - **디렉터리 명시:** Python 스크립트를 실행하기 전에는 에이전트의 `run_command` 도구에서 `Cwd` 옵션을 사용하여 작업 디렉터리를 해당 폴더로 명시하거나, 스크립트 및 대상 파일의 완전한 절대 경로를 입력하십시오. (독립적인 `cd` 명령어 사용은 도구 제약으로 인해 권장되지 않습니다.)

- **경로 미스매치 방지:** 파일 읽기/쓰기(I/O)가 포함된 파이썬 코드를 작성할 때는 작업 디렉터리 꼬임을 막기 위해 `os.path.abspath(__file__)` 또는 `pathlib.Path`를 사용하여 스크립트 파일 위치를 기준으로 상대 경로를 절대 경로로 변환해 처리하십시오.
