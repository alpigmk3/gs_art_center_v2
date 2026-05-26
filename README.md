# GS아트센터_좌석시야 서비스 v2

## 1. 개요 (Objective)
- **한 줄 요약:** 이 프로젝트가 무엇을 하는 프로그램인지 작성합니다.
- **주요 기능:**
  - shapespark 를 사용한 3D 모델을 온라인 가상 투어 
  - 추가적으로 좌석배치도로 각 층별 구역별 좌석별 시야 확인 
  - index.html 을 국문 , 영문  나눌 예정 
  - index.html 국문
  - index_eng.html 영문

## 2. 기술 스택 (Tech Stack)
- **Language/Runtime:** HTML , js only use
- **Framework:** shapespark , https://github.com/shapespark/shapespark-viewer-api 참조


## 3. 프로젝트 구조 (Structure)

gs_art_center_v2/
├── 2026-05-22-19-41-08/            # shapespark data
├── index.html		
├── seatmap_eng.svg		# 좌석배치도 국문
├── seatmap_kor.svg		# 좌석배치도 국문
└── README.md       	# 본 설정 파일


*   **규칙(Rules):
HTML , js 만 수정 shapespark 관련 html 과 js는 수정하지 않음
shapespark 관련 html 버튼 일부와 CSS 는 수정 가능 


**참고

1. 참고 : http://alpig.woobi.co.kr/test01/
이 사이트의  ID container 부분 좌석배치도 같이 구현할 예정
seatmap_kor.svg, seatmap_eng.svg 파일이 작업할 좌석배치도 



2.참고 : https://alpigmk3.github.io/gs_art_center_dev/
이 사이트 로고 , 로딩 바 부분 
최초 조작안내 및 매뉴 
화면구성을 그대로 가져올 예정 

3. 화면 구성 
    3.1 초기화면 
      - 로고 표시 
      - shapespark 로딩 완료후 메인화면 이동 
      - 2.참고 사이트와 같은 디자인
      
    3.2 조작안내 및 매뉴화면
        - 화면 전체 shapespark viewer 
        - 투명 테두리에 
          1. 조작안내 표시
          2. 좌석선택 | 자동투어 | 자유이동 
        - 2.참고 사이트의 div class="service-select-card"  같은 디자인
        
    3.3 메인화면
        - 서브 매뉴 버튼은 다 반투명 50% 

        - 좌측 상단에  로고
        - 좌측 하단
           1. 좌석선택 버튼 (좌석배치도 표시)
           2. 무대변경 버튼 (shapespark 설정 api 호출 예정 , 버튼 디자인만 추가해줘 )
        
        - 좌측 상단 shapespark 버튼 그대로 CSS만 변경  (2.참고 사이트와 같은 디자인)
        - 우측 하단 shapespark 버튼 그대로 CSS, 버튼 이미지 변경 (2.참고 사이트와 같은 이미지)
        - 2.참고 사이트와 같은 디자인

    3.4 좌석배치도 화면 
        - 좌석선택 버튼 클릭시 좌석배치도 화면 표시 
          - 2.참고 사이트의 div class="seatmap-popup" 와 동일한 디자인
          - div id="seatmap-zoom-content" 이 부분은 1. 참고 사이트의 div id="container" 이 부분과 같은 구조로 만들어줘
          - 안에 좌석 이미지는 seatmap_kor.svg 를 사용해 줘
          - 내부에 좌석마다 클릭 할수 있도록 해서 클릭시 해당 좌석으로 갈수 있게 해줘
          

