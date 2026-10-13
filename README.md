# Anatomy Lab · 인체 위치 탐험

한국어·영어 이름으로 구조를 검색하고 인체 안의 위치와 주변 관계를 확인하는 3D 웹앱입니다.

## 사용

- 남성 / 여성 모형 전환
- 검색 결과 선택 시 청록색 하이라이트와 위치 점·이름표 표시
- 주변 구조를 흐리게 유지하고, 필요하면 선택 부위만 따로 보기
- 휠: 상하 이동 / Ctrl+휠: 확대·축소 / Shift+드래그: 이동
- 드래그: 회전 / 두 손가락: 이동·확대 / 방향키: 이동

첫 실행에는 모델 다운로드 시간이 필요합니다. Chrome 또는 Edge의 최신 버전을 사용하세요.

## 자동 빌드와 웹 링크

이 저장소는 GitHub Actions에서 공식 원본 모델을 내려받아 웹용 데이터로 변환한 뒤 GitHub Pages에 게시합니다. 원본 모델 전체를 재현할 수 있는 변환 코드와 한국어 용어 사전을 함께 저장합니다.

1. **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
2. **Actions → Build and publish Anatomy Lab**에서 실행 결과를 확인합니다. main 브랜치 변경 시 자동 실행됩니다.
3. 첫 빌드는 원본 모델 다운로드와 변환 때문에 몇 분 걸릴 수 있습니다.
4. 성공 후 Pages 설정 또는 배포 작업에서 표시되는 사이트 링크를 공유합니다.

웹용 모델은 8MiB 이하의 파일로 나눕니다. Git LFS나 별도 서버가 필요하지 않습니다. 데이터는 원본 출처에서 다시 내려받아 생성되며 원본 서버 가용성의 영향을 받습니다.

## 내 컴퓨터에서 실행

Python 3.12에서 `python -m pip install numpy==2.2.6`, `python tools/build_site.py`를 실행합니다. 이후 `python -m http.server 8000 --directory _site`를 실행하고 `http://localhost:8000`을 엽니다. 저장소의 `index.html`은 모델을 별도 파일로 불러오므로 더블클릭으로 실행하지 않습니다.

## 데이터 범위

- 남성: BodyParts3D 4.0의 2,234개 모형, 3,432개 개별·묶음 구조명.
- 여성: Human Reference Atlas v1.10의 전체 956개 모형에 v1.5 골반 모형 8개를 더한 964개 모형, 1,172개 선택 구조.
- 여성 원본에는 두개골·갈비뼈·팔뼈 등 일부 구조가 없습니다. 남성 데이터를 여성 모형으로 가장해 보충하지 않았습니다.
- 주요 한국어 이름은 임상·기존 용어와 해부학 용어를 함께 표시하며, 두 이름 모두 검색 별칭으로 지원합니다. 예: 대퇴골(넙다리뼈), 경골(정강뼈), 신장(콩팥), 갑상연골(방패연골). 세부 조합 명칭은 영어 원명과 대조가 필요하고, 대한해부학회·대한의사협회 용어집 전체와의 표준 대조 검증을 완료한 것은 아닙니다.
- 위치 탐색과 복습을 위한 참고 아틀라스이며, Step 2 문제은행이나 임상 의사결정 자료는 포함하지 않습니다.

## 한국어 용어 참고

용어 병기 방식을 검토한 자료: 정민석·오창석·이영일(2019), 해부학 선생이 의학용어집 제6판을 만드는 데 참여한 경험. https://doi.org/10.11637/aba.2019.32.1.9
주요 장기 명칭 참고: 서울대학교병원 https://www.snuh.org/m/reservation/meddept/BEN/mainIntro.do , 분당서울대학교병원 https://www.snubh.org/dh/ur , 대한신장학회 https://www.ksn.or.kr/general/disease/index.php
용어집 전체를 복제한 목록이 아니라 앱에서 작성한 주요 명칭·검색 별칭 표입니다. 학교별 교재 표현이나 모든 세부 명칭과 일치한다고 보장하지 않습니다.

## 출처 및 라이선스

**BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.**

- 원본: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- 현재 라이선스: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html
- 좌표·색상 변환 및 16비트 좌표 저장. 모든 원본 개별 모형을 유지했습니다.

**Kristen Browne and Heidi Schlehlein, Human Reference Atlas / HuBMAP, 3D Reference Organ Set for Female, v1.10 and v1.5. CC BY 4.0. Based on the Visible Human Female dataset, National Library of Medicine.**

- 원본 라이브러리: https://humanatlas.io/3d-reference-library
- 라이선스: https://creativecommons.org/licenses/by/4.0/
- 원본 좌표 변환, 정확히 겹치는 정점 병합, 색상 변경, 16비트 좌표 저장. v1.5에서 골반 모형 8개를 보충했습니다.

Three.js: © three.js authors, MIT. 전체 라이선스는 `vendor/LICENSE.txt`에 있습니다.
앱 코드의 라이선스는 `LICENSE`이며, 모델 데이터의 CC BY 4.0 라이선스를 변경하지 않습니다.

