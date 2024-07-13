import fitz  # PyMuPDF
import openai
import json
import re
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Paper, PaperInfo
import time
from openai.error import OpenAIError, RateLimitError, InvalidRequestError  # 여기서 예외 클래스 가져오기
from rest_framework.permissions import IsAuthenticated
# OpenAI API 키 설정
openai.api_key = settings.OPENAI_API_KEY

# PDF 파일의 특정 페이지 텍스트 추출 함수
def extract_text_from_pdf(pdf_path, start_page, end_page):
    document = fitz.open(pdf_path) #pdf 첫 페이지만 추출 + img 를 text 로 바꾸는 도구
    text = ""
    for page_num in range(start_page - 1, end_page):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# GPT API에 텍스트 전달하여 정보 추출 함수
def extract_info_from_text(pdf_text):
    prompt = f"""다음은 네가 인용문을 써줄 학술 논문이야.: {pdf_text}
    
MLA, APA, Chicago, Vancouver 형식으로 인용을 한 줄씩 순서대로 써줘. 한국어 논문 저자명과 제목은 한국어로, 영어 논문은 영어로 써야 해.

다음은 한국어 논문 인용의 예시야. 정확히 이런 형식이어야 해. 제발 좀 한국어 논문은 한국어로 쓰라고!!!!!

MLA:
김경애. "회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-." 한국산학기술학회 논문지, vol. 25, no. 1, 2024, 734-743.
APA:
김경애. (2024). 회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-. 한국산학기술학회 논문지, 25(1), 734-743, 10.5762/KAIS.2024.25.1.734
Chicago:
김경애. "회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-." 한국산학기술학회 논문지 25, no. 1 (2024): 734-743, 10.5762/KAIS.2024.25.1.734
Vancouver:
김경애. 회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-. 한국산학기술학회 논문지. 2024;25(1): 734-743. 10.5762/KAIS.2024.25.1.734

These are the examples for English paper citation. Make sure to follow the format exactly!

MLA:
Hassabis, Demis, et al. "Neuroscience-Inspired Artificial Intelligence." Neuron, vol. 95, 2017, pp. 245-268.
APA:
Hassabis, Demis, et al. (2017). Neuroscience-Inspired Artificial Intelligence. Neuron, 95, 245-268.
Chicago:
Hassabis, D., Kumaran, D., Summerﬁeld, C., & Botvinick, M. "Neuroscience-Inspired Artificial Intelligence." Neuron. 2017;95:245-268.
Vancouver:
Hassabis D, Kumaran D, Summerﬁeld C, Botvinick M. Neuroscience-Inspired Artificial Intelligence. Neuron. 2017;95:245-268.

이제 다음 논문에 대한 인용문을 생성해줘:
{pdf_text}

제발 형식을 꼭 지켜서, 각 인용문을 한 줄씩 MLA, APA, Chicago, Vancouver 순서대로 정확히 만들어줘.
제발 좀 한국어 논문은 저자명, 제목, 저널명 모두 한국어로 쓰라고!!!!!
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600
    )

    return response.choices[0].message["content"].strip()

class ProcessPaperInfo(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Extract paper info",
        responses={200: 'PaperInfo created successfully or updated successfully.'},
        manual_parameters=[
            openapi.Parameter(
                "Authorization", 
                openapi.IN_HEADER, 
                description="access token", 
                type=openapi.TYPE_STRING
            )
        ]
    )
    def post(self, request, paper_id):
        paper = get_object_or_404(Paper, paper_id=paper_id)
        if not paper.pdf:
            return Response({"error": "PDF file not found."}, status=status.HTTP_400_BAD_REQUEST)

        pdf_path = paper.pdf.path
        pdf_text = extract_text_from_pdf(pdf_path, 1, 1)

        try:
            paper_info = extract_info_from_text(pdf_text)
            paper_info_list = re.split(r'\n+', paper_info)
            print(paper_info_list)
            
            # 기존의 PaperInfo 객체가 있으면 가져오고, 없으면 생성
            paper_info_instance, created = PaperInfo.objects.update_or_create(
                paper=paper,
                defaults={
                    'mla_reference': paper_info_list[1],
                    'apa_reference': paper_info_list[3],
                    'chicago_reference': paper_info_list[5],
                    'vancouver_reference': paper_info_list[7]
                }
            )
            
            if created:
                message = "PaperInfo created successfully."
            else:
                message = "PaperInfo updated successfully."
            
            return Response({"message": message, "paper_info_id": paper_info_instance.paperInfo_id}, status=status.HTTP_200_OK)
        
        except RateLimitError:
            return Response({"error": "Rate limit exceeded. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except InvalidRequestError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except json.JSONDecodeError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)