# 📝 REFERTO: 참고문헌 생성 및 관리 서비스
![image](https://github.com/user-attachments/assets/b3a7e6b4-bc75-4194-81d1-7685fdefb8f2)


<div align="center">
🍉 2024 서울대학교 멋쟁이 사자처럼 여름 해커톤 🍉

🔗 https://www.referto.site/

📲 [프론트엔드 레포지토리](https://github.com/vonvon56/referto-frontend)
</div>

---

## 👥 팀원 소개
|이름|박혜리|이은재|편예빈|황경서|
|:---:|:---:|:---:|:---:|:---:|
|역할|대장, 프론트엔드|프론트엔드|프론트엔드, 간식팀장|백엔드|
|깃허브|[@Hypell](https://github.com/Hypell)|[@eunjaelee1004](https://github.com/eunjaelee1004)|[@yebin1926](https://github.com/yebin1926)|[@vonvon56](https://github.com/vonvon56)|



## ℹ️ 프로젝트 소개

- 원하는 참고문헌을 등록할 수 있습니다.

- 등록한 참고문헌의 4가지 인용 양식(APA, Vancouver, MLA, Chicago)이 자동으로 생성됩니다.

- 문헌별 세부 페이지에 접속하여 하이라이팅, 메모를 할 수 있습니다.


## 🛠️ 기술 스택
<img src="https://img.shields.io/badge/React-61DAFB?style=flat&logo=React&logoColor=white"/> <img src="https://img.shields.io/badge/Django-092E20?style=flat&logo=Django&logoColor=white"/> <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=HTML5&logoColor=white" />

<img src="https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=CSS3&logoColor=white" /> <img src="https://img.shields.io/badge/amazonwebservices-232F3E?style=flat&logo=amazonwebservices&logoColor=white"/>

## 🖥️ API 


![REFERTO](https://github.com/user-attachments/assets/bc377203-a96f-4917-9999-53ce5486c61c)


## ⚙️ 백엔드 주요 기능
- fitz 라이브러리 활용

  유저로부터 파일을 수신받고, 첫 장만 잘라서 OCR 처리한 뒤 텍스트만 openai api(GPT 3.5 turbo)에 송신합니다.
  인용을 생성하기 위한 정보는 거의 모든 경우 논문의 첫 장에 모두 포함되어 있으므로, 첫 장의 정보만 추출하면 api 비용을 절약할 수 있습니다.

- 한/영 논문 구분

  정규표현식으로 한글이 포함되어 있는지 판별한 후, 한글이 하나라도 포함되어 있다면 한국어 논문으로 간주합니다.
  이렇게 논문의 언어를 구분한 뒤, 각 언어에 서로 다른 프롬프트를 적용합니다.
  이를 통해 한국어 논문이 강제로 영어로 변환되는 오류를 줄일 수 있습니다.
  

