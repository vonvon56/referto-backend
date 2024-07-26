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
from openai.error import OpenAIError, RateLimitError, InvalidRequestError  # 여기서 예외 클래스 가져오기
from rest_framework.permissions import IsAuthenticated
from .serializers import PaperInfoSerializer
from .request_serializers import PaperInfoChangeSerializer
# OpenAI API 키 설정
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 한국어 논문 여부 판별
def contains_korean(text):
    korean_pattern = re.compile(r'[가-힣]')
    return bool(korean_pattern.search(text))

# PDF 파일의 특정 페이지 텍스트 추출 함수
def extract_text_from_pdf(pdf_path, start_page, end_page):
    document = fitz.open(pdf_path) #pdf 첫 페이지만 추출 + img 를 text 로 바꾸는 도구
    text = ""
    for page_num in range(start_page - 1, end_page):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# GPT API에 텍스트 전달하여 정보 추출 함수
def extract_info_from_korean_text(pdf_text):
    prompt = f"""제공된 PDF OCR 결과를 바탕으로 MLA, APA, Chicago, Vancouver 형식으로 인용을 작성하십시오:

1. 제공된 PDF OCR 결과가 학술 논문에서 추출되었고 인용에 필요한 모든 정보를 포함하는지 확인하십시오:
3. 추출된 정보를 사용하여 인용을 **MLA, APA, Chicago, Vancouver** 형식으로 작성하십시오.
4. 최종 인용 형식의 정확성과 일관성을 확인하십시오.
5. 인용 형식이 정확하게 한글로 출력되었는지 확인하십시오.

인용 내용을 추가 설명 없이 직접 출력하십시오.

### 예시 인용:
MLA:
김경애. "회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-." 한국산학기술학회 논문지, vol. 25, no. 1, 2024, 734-743.
APA:
김경애. (2024). 회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-. 한국산학기술학회 논문지, 25(1), 734-743, 10.5762/KAIS.2024.25.1.734
Chicago:
김경애. "회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-." 한국산학기술학회 논문지 25, no. 1 (2024): 734-743, 10.5762/KAIS.2024.25.1.734
Vancouver:
김경애. 회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-. 한국산학기술학회 논문지. 2024;25(1): 734-743. 10.5762/KAIS.2024.25.1.734

### 처리할 PDF OCR 결과:
{pdf_text}

인용을 반드시 다음과 같은 형식으로 출력하십시오:


MLA:
김경애. "회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-." 한국산학기술학회 논문지, vol. 25, no. 1, 2024, 734-743.
APA:
김경애. (2024). 회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-. 한국산학기술학회 논문지, 25(1), 734-743, 10.5762/KAIS.2024.25.1.734
Chicago:
김경애. "회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-." 한국산학기술학회 논문지 25, no. 1 (2024): 734-743, 10.5762/KAIS.2024.25.1.734
Vancouver:
김경애. 회빙환과 시간 되감기 서사의 문화적 의미 -웹소설 『내 남편과 결혼해 줘』를 중심으로-. 한국산학기술학회 논문지. 2024;25(1): 734-743. 10.5762/KAIS.2024.25.1.734

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


def extract_info_from_english_text(pdf_text):
    prompt = f"""Given the PDF OCR results provided, follow the steps to create citations in MLA, APA, Chicago, and Vancouver formats:

1. Confirm if the provided PDF OCR results are from an academic paper and contain all necessary information for citation:
    - Title of the paper
    - Authors
    - Journal name
    - Year of publication
    - Volume and issue number (if available)
    - Page numbers
    If the results are not from an academic paper or do not contain all necessary information, respond that the information cannot be found.
2. Extract the necessary information for citation:
    - Title of the paper
    - Authors
    - Journal name
    - Year of publication
    - Volume and issue number (if available)
    - Page numbers
3. Using the extracted information, format the citation **only** in the following styles: MLA, APA, Chicago, and Vancouver.
4. Ensure the final citation formats are correct and consistent.

Output the formatted citations directly without any additional explanation.

### Example citations:
MLA:
Hassabis, Demis, et al. "Neuroscience-Inspired Artificial Intelligence." Neuron, vol. 95, 2017, pp. 245-268.
APA:
Hassabis, Demis, et al. (2017). Neuroscience-Inspired Artificial Intelligence. Neuron, 95, 245-268.
Chicago:
Hassabis, D., Kumaran, D., Summerﬁeld, C., & Botvinick, M. "Neuroscience-Inspired Artificial Intelligence." Neuron. 2017;95:245-268.
Vancouver:
Hassabis D, Kumaran D, Summerﬁeld C, Botvinick M. Neuroscience-Inspired Artificial Intelligence. Neuron. 2017;95:245-268.

### PDF OCR results to process:
{pdf_text}

Output the citations in the following format:


MLA:
Hassabis, Demis, et al. "Neuroscience-Inspired Artificial Intelligence." Neuron, vol. 95, 2017, pp. 245-268.
APA:
Hassabis, Demis, et al. (2017). Neuroscience-Inspired Artificial Intelligence. Neuron, 95, 245-268.
Chicago:
Hassabis, D., Kumaran, D., Summerﬁeld, C., & Botvinick, M. "Neuroscience-Inspired Artificial Intelligence." Neuron. 2017;95:245-268.
Vancouver:
Hassabis D, Kumaran D, Summerﬁeld C, Botvinick M. Neuroscience-Inspired Artificial Intelligence. Neuron. 2017;95:245-268.

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
        pdf_text = extract_text_from_pdf(pdf_path, 1, 1)

        print("*****entered 3")

        try:
            # 한국어 논문인 경우
            if contains_korean(pdf_text):
                paper_info = extract_info_from_korean_text(pdf_text)
            else:
                paper_info = extract_info_from_english_text(pdf_text)
            paper_info_list = re.split(r'\n+', paper_info)
            print(paper_info_list)
            
            # 기존의 PaperInfo 객체가 있으면 가져오고, 없으면 생성
            paper_info_instance, created = PaperInfo.objects.update_or_create(
                paper=paper,
                defaults={
                    'MLA': paper_info_list[1],
                    'APA': paper_info_list[3],
                    'Chicago': paper_info_list[5],
                    'Vancouver': paper_info_list[7]
                }
            )
            serializer = PaperInfoSerializer(paper_info_instance)
            print("*****entered 4")
            
            if created:
                message = "PaperInfo created successfully."
            else:
                message = "PaperInfo updated successfully."
            
            return Response({"message": message, "paper_info": serializer.data}, status=status.HTTP_200_OK)
        
        except RateLimitError:
            return Response({"error": "Rate limit exceeded. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except InvalidRequestError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except json.JSONDecodeError:
            return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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