import fitz  # PyMuPDF
import openai
import json
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

# OpenAI API 키 설정
openai.api_key = settings.OPENAI_API_KEY

# PDF 파일의 특정 페이지 텍스트 추출 함수
def extract_text_from_pdf(pdf_path, start_page, end_page):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(start_page - 1, end_page):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# GPT API에 텍스트 전달하여 정보 추출 함수
def extract_info_from_text(pdf_text):
    prompt = f"This is the text of an academic paper: {pdf_text}\n\nPlease extract the title, authors, and publication year of this paper. Authors should be in the form of python list."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    return response.choices[0].message["content"].strip()

class ProcessPaperInfo(APIView):
    @swagger_auto_schema(
        operation_description="Extract paper info",
        responses={200: 'PaperInfo created successfully.'}
    )
    def post(self, request, paper_id):
        paper = get_object_or_404(Paper, paper_id=paper_id)
        if not paper.pdf:
            return Response({"error": "PDF file not found."}, status=status.HTTP_400_BAD_REQUEST)

        pdf_path = paper.pdf.path
        pdf_text = extract_text_from_pdf(pdf_path, 1, 3)

        # time.sleep(5)

        try:
            paper_info = extract_info_from_text(pdf_text)
            # PaperInfo 생성 및 저장
            paper_info_instance = PaperInfo.objects.create(
                paper=paper,
                reference=paper_info
            )
            return Response({"message": "PaperInfo created successfully.", "paper_info_id": paper_info_instance.paperInfo_id}, status=status.HTTP_200_OK)
        except RateLimitError:
            return Response({"error": "Rate limit exceeded. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except InvalidRequestError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except json.JSONDecodeError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
