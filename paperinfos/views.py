import re, os, json, openai, fitz
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Paper, PaperInfo
from assignments.models import Assignment
#from openai.error import OpenAIError, RateLimitError, InvalidRequestError  # 여기서 예외 클래스 가져오기
from rest_framework.permissions import IsAuthenticated
from .serializers import PaperInfoSerializer
from .request_serializers import PaperInfoChangeSerializer

# OpenAI API 키 설정
openai.api_key = os.environ.get("OPENAI_API_KEY")

# # 한국어 논문 여부 판별
# def contains_korean(text):
#     korean_pattern = re.compile(r'[가-힣]')
#     return bool(korean_pattern.search(text))

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
    prompt = f"""This is the text of a paper that you will generate citations for: {pdf_text}
You are provided with a paper's details, citation guidelines, and styles (APA, MLA, Chicago, Vancouver). Based on this information, generate citations for each style, keeping the author names and journal title exactly as they appear in the original language. Use the following output format in JSON:

Paper Details:

Title: 일본어에서 간접차용된 영어 차용어의 음운론적 특질
Authors: 이경철, 김대영
Journal: 환경연구
Volume: 10
Issue: 2
Pages: 195-202
Year: 2023
Citation Guidelines Recap:

APA Style: Focuses on the date and uses initials for authors but does not include "&" for non-English names.
MLA Style: Focuses on the author names, using full names.
Chicago Style: Uses full author names and supports "Notes-Bibliography" format.
Vancouver Style: Uses numbered references listed in the order they appear and uses initials for authors.
Do not use \, *, or similar special characters in the citations.
Generate the citations in the following JSON format:

example:
{{
  "apa": "이경철, 김대영. (2023). 일본어에서 간접차용된 영어 차용어의 음운론적 특질. 환경연구, 10(2), 195-202.",
  "mla": "이경철, 김대영. 일본어에서 간접차용된 영어 차용어의 음운론적 특질. 환경연구, vol. 10, no. 2, 2023, pp. 195-202.",
  "chicago": "이경철, 김대영. 일본어에서 간접차용된 영어 차용어의 음운론적 특질. 환경연구 10, no. 2 (2023): 195-202.",
  "vancouver": "이경철, 김대영. 일본어에서 간접차용된 영어 차용어의 음운론적 특질. 환경연구. 2023;10(2):195-202."
}}
Ensure that the author names, journal title, and paper title remain exactly as they appear in the provided details, in the original language, and do not use "&" between the author names.
"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000
        )
        print("response: ", response)
        print("refined: ", response.choices[0].message["content"].strip())
        json_match = re.search(r"\{[\s\S]*\}", response.choices[0].message["content"].strip())
        if json_match:
            print('json_match: ', json_match.group())
            return json_match.group()
        else:
            return response.choices[0].message["content"].strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API 오류: {e}")  
        return None  # 또는 적절한 오류 응답
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return None  # 또는 적절한 오류 응답


class ProcessPaperInfo(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="PaperInfo 생성",
        operation_description="Paper 파일로부터 PaperInfo(인용)을 추출합니다.",
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
        print("*****entered paperinfo post")
        paper = get_object_or_404(Paper, paper_id=paper_id)
        if not paper.pdf:
            return Response({"error": "PDF file not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        print("*****entered 2")

        pdf_path = paper.pdf.path
        pdf_text = extract_text_from_pdf(pdf_path, 1, 2)

        print("*****entered 3")

        try:
            paper_info_text = extract_info_from_text(pdf_text)      
            paper_info = json.loads(paper_info_text)
            
            # 기존의 PaperInfo 객체가 있으면 가져오고, 없으면 생성
            paper_info_instance, created = PaperInfo.objects.update_or_create(
                paper=paper,
                defaults={
                    'MLA': re.sub(r'[\\*]', '', paper_info.get('mla', '')),
                    'APA': re.sub(r'[\\*]', '', paper_info.get('apa', '')),
                    'Chicago': re.sub(r'[\\*]', '', paper_info.get('chicago', '')),
                    'Vancouver': re.sub(r'[\\*]', '', paper_info.get('vancouver', ''))
                }
            )
            serializer = PaperInfoSerializer(paper_info_instance)
            print("*****entered 4")
            
            if created:
                message = "PaperInfo created successfully."
            else:
                message = "PaperInfo updated successfully."
            
            return Response({"message": message, "paper_info": serializer.data}, status=status.HTTP_200_OK)
        
        except json.JSONDecodeError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            return Response({"error": f"Missing key in paper_info: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        operation_id="PaperInfo 삭제",
        operation_description="PaperInfo를 삭제합니다.",
        responses={
            204: "No Content",
            400: "Bad Request",
            404: "Not Found",
        },
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )

    def delete(self, request, paper_id):
        try:
            paperInfo_id = paper_id
            paperinfo = PaperInfo.objects.get(paperInfo_id=paperInfo_id)
        except:
            return Response(
                {"detail": "PaperInfo Not found."}, status=status.HTTP_404_NOT_FOUND
            )
        paperinfo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    serializer_class = PaperInfoChangeSerializer
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="PaperInfo 수정",
        operation_description="PaperInfo를 이용자가 수정합니다.",
        responses={
            200: PaperInfoSerializer,
            400: "Bad Request",
            404: "Not Found",
        },
        request_body=PaperInfoChangeSerializer,
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def put(self, request, paper_id):
        serializer = PaperInfoChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reference_type = serializer.validated_data['reference_type']
        new_reference = serializer.validated_data['new_reference']

        try:
            paperinfo = PaperInfo.objects.get(paperInfo_id=paper_id)
        except PaperInfo.DoesNotExist:
            return Response({"detail": "PaperInfo Not found."}, status=status.HTTP_404_NOT_FOUND)

        if reference_type not in ['MLA', 'APA', 'Chicago', 'Vancouver']:
            return Response({"detail": "Invalid reference type."}, status=status.HTTP_400_BAD_REQUEST)

        setattr(paperinfo, reference_type, new_reference)
        paperinfo.save()

        response_serializer = PaperInfoSerializer(paperinfo)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class PaperInfoListView(APIView):
        permission_classes = [IsAuthenticated]
        @swagger_auto_schema(
            operation_id="PaperInfo 목록 조회",
            operation_description="해당 Assignment의 참고문헌 목록을 조회합니다.",
            responses={
                200: PaperInfoSerializer(many=True),
                404: "Not Found",
            }
        )
        def get(self, request, assignment_id):
            if(assignment_id == 0):
                paperinfos = PaperInfo.objects.all()
                serializer = PaperInfoSerializer(paperinfos, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
            
            if not Paper.objects.filter(assignment=assignment).exists():
                return Response([], status=status.HTTP_200_OK) #return empty list if no paperinfos are found
        
            try:
                papers = Paper.objects.filter(assignment=assignment)
                paperinfos = PaperInfo.objects.filter(paper__in=papers)

                serializer = PaperInfoSerializer(paperinfos, many=True)
            
            except:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

class PaperInfoDetailView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_id="PaperInfo 조회",
        operation_description="PaperInfo 하나를 조회합니다.",
        responses={
            200: PaperInfoSerializer,
            404: "Not Found",
        },
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, assignment_id, paper_id):
        try:
            assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
            papers = Paper.objects.filter(assignment=assignment)
            paper = Paper.objects.get(paper_id=paper_id)
            paperinfo = PaperInfo.objects.get(paper=paper)
            serializer = PaperInfoSerializer(paperinfo)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
