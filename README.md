# Anatomy Lab · 인체 위치 탐험

한국어·영어 이름으로 구조를 검색하고 인체 안의 위치와 주변 관계를 확인하는 3D 웹앱입니다.

## 사용

- 남성 / 여성 모형 전환
- 검색 결과 선택 시 청록색 하이라이트와 위치 점·이름표 표시
- 주변 구조를 흐리게 유지하고, 필요하면 선택 부위만 따로 보기
- 휠: 상하 이동 / Ctrl+휠: 확대·축소 / Shift+드래그: 이동
- 드래그: 회전 / 두 손가락: 이동·확대 / 방향키: 이동

첫 실행에는 모델 다운로드 시간이 필요합니다. Chrome 또는 Edge의 최신 버전을 사용하세요.

## GitHub에 올리고 웹 링크 만들기

1. GitHub에서 `anatomy-lab`이라는 **공개(Public)** 저장소를 만듭니다. 이 이름은 제안이며 바꿔도 됩니다.
2. 이 폴더의 **내용 전체**를 저장소 최상위에 올립니다. `index.html`, `atlas.js`, `style.css`, 두 JSON 파일, `vendor/`, `data/`가 모두 필요합니다. ZIP 자체를 올리지 않습니다.
3. 저장소의 **Settings → Pages → Build and deployment**에서 **Deploy from a branch**를 선택합니다.
4. **main / (root)**를 선택하고 저장합니다.
5. 배포 후 Pages 설정에 표시되는 사이트 주소를 공유합니다. 실제 주소는 GitHub가 제공한 값을 사용하세요.

모델을 8MiB 이하의 파일로 나눠 일반 Git 저장소와 웹 업로드에서 사용할 수 있게 했습니다. Git LFS나 별도 서버는 필요하지 않습니다.

## 내 컴퓨터에서 실행

다운로드한 저장소 폴더에서 `python -m http.server 8000`을 실행한 뒤 `http://localhost:8000`을 엽니다. 저장소의 `index.html`은 모델을 별도 파일로 불러오므로 더블클릭으로 실행하지 않습니다.

## 데이터 범위

- 남성: BodyParts3D 4.0의 2,234개 모형, 3,432개 개별·묶음 구조명.
- 여성: Human Reference Atlas v1.10의 전체 956개 모형에 v1.5 골반 모형 8개를 더한 964개 모형, 1,172개 선택 구조.
- 여성 원본에는 두개골·갈비뼈·팔뼈 등 일부 구조가 없습니다. 남성 데이터를 여성 모형으로 가장해 보충하지 않았습니다.
- 한국어는 용어 사전과 구성 규칙으로 만든 탐색용 번역입니다. 영어 원명을 유지합니다.
- 위치 탐색과 복습을 위한 참고 아틀라스이며, Step 2 문제은행이나 임상 의사결정 자료는 포함하지 않습니다.

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

