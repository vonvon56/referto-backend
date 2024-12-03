from django.http import FileResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import *
from .serializers import *
from .request_serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from paperinfos.views import extract_text_from_pdf, extract_info_from_text
from paperinfos.serializers import *
import json, re
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import os
from django.conf import settings
from tempfile import NamedTemporaryFile

# pdf 파일 업로드 뷰
class PaperUploadView(generics.GenericAPIView):
    serializer_class = PaperCreateSerializer
    # # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_id='Paper 생성',
        operation_description="새로운 Paper를 생성합니다.",
        responses={
            201: openapi.Response('Successfully created', PaperCreateSerializer),
            400: 'Bad request'
        },
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def post(self, request):
        serializer = PaperCreateSerializer(data=request.data)
        if serializer.is_valid():
            pdf = request.FILES['pdf']
            assignment_id = request.data['assignment']
            paper = Paper.objects.create(pdf=pdf, assignment_id=assignment_id)
            model_serializer = PaperSerializer(paper)
            return Response({"message": "Paper created successfully", "data": model_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LandingPagePaperUploadView(generics.GenericAPIView):
    serializer_class = LandingPagePaperCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_id='Landing Page 논문정보 return',
        operation_description="paper 정보를 저장하지 않고, 인용 정보를 체험용으로 보여줍니다.",
        responses={
            201: openapi.Response('Successfully created', LandingPagePaperCreateSerializer),
            400: 'Bad request'
        },
    )
    def post(self, request):
        serializer = LandingPagePaperCreateSerializer(data=request.data)
        if serializer.is_valid():
           
            # 파일을 NamedTemporaryFile로 저장
            pdf_file = request.FILES['pdf']
            temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
            try:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)
                temp_file.close()  # 명시적으로 파일을 닫음

                # PDF 라이브러리에 파일 경로 전달
                pdf_text = extract_text_from_pdf(temp_file.name, 1, 1)
                paper_info_text = extract_info_from_text(pdf_text)
                paper_info = json.loads(paper_info_text)

                # 인용 정보 정리
                landing_page_paper_info = {
                    'MLA': re.sub(r'[\\*]', '', paper_info.get('mla', '')),
                    'APA': re.sub(r'[\\*]', '', paper_info.get('apa', '')),
                    'Chicago': re.sub(r'[\\*]', '', paper_info.get('chicago', '')),
                    'Vancouver': re.sub(r'[\\*]', '', paper_info.get('vancouver', ''))
                }

                return Response({"message": "Landing page paperinfo created successfully.", "paper_info": landing_page_paper_info}, status=status.HTTP_200_OK)
            finally:
                # 파일 삭제
                if os.path.exists(temp_file.name):
                    os.remove(temp_file.name)

            # except json.JSONDecodeError:
            #     return Response({"error": "Error parsing the response from OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # except Exception as e:
            #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaperDetailView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='Paper 삭제',
        operation_description="특정 Paper를 삭제합니다.",
        responses={
            204: 'No Content',
            404: 'Not Found'
        },
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def delete(self, request, *args, **kwargs):
        paper_id = kwargs.get('pk')
        try:
            paper = Paper.objects.get(paper_id=paper_id)
        except:
            return Response({"detail":"Paper not found."}, status=status.HTTP_404_NOT_FOUND)

        paper.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @swagger_auto_schema(
        operation_id='Paper 조회',
        operation_description="특정 Paper를 조회합니다.",
        responses={
            200: 'application/pdf',
            404: 'Not Found'
        },
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, pk, *args, **kwargs):
        paper = self.get_paper(pk)
        if not paper:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        file_handle = paper.pdf.open()
        response = FileResponse(file_handle, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{paper.pdf.name}"'
        return response
    
    def get_paper(self, pk):
        try:
            paper = Paper.objects.get(pk=pk)
            return paper
        except Paper.DoesNotExist:
            return None
        
class PaperNumberView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='Paper 번호 로드',
        operation_description="Paper의 번호를 가져옵니다. paper_id와는 별개입니다.",
        responses={
            204: 'No Content',
            404: 'Not Found'
        },
        manual_parameters=[
            openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, pk):
        try:
            paper = Paper.objects.get(paper_id=pk)
        except:
            return Response({"detail":"Paper not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"number": paper.number}, status=status.HTTP_200_OK)
