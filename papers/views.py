from django.http import FileResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Paper
from memos.models import Memo
from .serializers import PaperSerializer
from .request_serializers import PaperCreateSerializer
from rest_framework.parsers import MultiPartParser, FormParser



# pdf 파일 업로드 기능 뷰
class PaperUploadView(generics.GenericAPIView):
    serializer_class = PaperCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        operation_description="새로운 Paper를 생성합니다.",
        # request_body=openapi.Schema(
        #     type=openapi.TYPE_OBJECT,
        #     properties={
        #         'pdf': openapi.Schema(type=openapi.TYPE_FILE, description='PDF 파일'),
        #         'assignment': openapi.Schema(type=openapi.TYPE_INTEGER, description='Assignment ID')
        #     },
        #     required=['pdf', 'assignment']
        # ),
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
        # print(request)
        if serializer.is_valid():
            pdf_file = request.FILES['pdf']
            assignment_id = request.data['assignment']
            paper = Paper(pdf=pdf_file, assignment_id=assignment_id)
            paper.save()
            Memo.objects.create(paper=paper)
            return Response({"message": "Paper created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class PaperDetailView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get_paper(self, pk, user):
#         try:
#             paper = Paper.objects.select_related('assignment').get(pk=pk)
#             if paper.assignment.user != user:
#                 raise PermissionDenied("You do not have permission to access this paper.")
#             return paper
#         except Paper.DoesNotExist:
#             return None

#     # pdf 파일을 수정이나 삭제하는 기능은 아직 없음
#     @swagger_auto_schema(
#         operation_description="특정 Paper를 삭제합니다.",
#         responses={
#             204: 'No Content',
#             404: 'Not Found'
#         },
#         manual_parameters=[
#             openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
#         ]
#     )
#     def delete(self, request, pk, *args, **kwargs):
#         user = request.user
#         paper = self.get_paper(pk, user)
#         if not paper:
#             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#         paper.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
#     @swagger_auto_schema(
#         operation_description="특정 Paper를 수정합니다.",
#         responses={
#             200: PaperCreateSerializer,
#             400: 'Bad Request',
#             404: 'Not Found'
#         },
#         request_body=PaperCreateSerializer,
#         manual_parameters=[
#             openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
#         ]
#     )
#     def put(self, request, pk, *args, **kwargs):
#         user = request.user
#         paper = self.get_paper(pk, user)
#         if not paper:
#             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = PaperCreateSerializer(paper, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#     # pdf 파일을 개별 조회 후 다운로드 하는 기능 아직 없음
#     @swagger_auto_schema(
#         operation_description="특정 Paper를 조회합니다.",
#         responses={
#             200: 'application/pdf',
#             404: 'Not Found'
#         },
#         manual_parameters=[
#             openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)
#         ]
#     )
#     def get(self, request, pk, *args, **kwargs):
#         user = request.user
#         paper = self.get_paper(pk, user)
#         if not paper:
#             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#         file_handle = paper.pdf.open()
#         response = FileResponse(file_handle, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{paper.pdf.name}"'
#         return response