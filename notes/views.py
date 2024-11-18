from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Note, Paper
from assignments.models import Assignment
from .serializers import NoteSerializer


class NoteListView(generics.GenericAPIView):
  serializer_class = NoteSerializer

  @swagger_auto_schema(
    operation_id='한 Paper의 Note 목록 조회',
    operation_description='해당 Paper의 note 목록을 조회합니다.',
    responses={
      200: NoteSerializer(many=True),
      404: "Not Found",
    },
  )

  def get(self, request, paperId):
    try:
      paper = Paper.objects.get(paper_id=paperId)
    except Paper.DoesNotExist:
      return Response({"detail": "Paper not found."}, status=status.HTTP_404_NOT_FOUND)
    
    try:
      notes = Note.objects.filter(paper=paper)
      serializer = NoteSerializer(notes, many=True)
    except:
      return Response({"detail": "Paper not found."}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  @swagger_auto_schema(
    operation_id='Paper에 Note 추가',
    operation_description='해당 Paper에 note를 추가합니다.',
    responses={
      201: "Created", 
      404: "Not Found",
      400: "Bad Request",
    },
  )
  def post(self, request, paperId):
    paper = get_object_or_404(Paper, paper_id=paperId)
    if not paper.pdf:
      return Response({"error": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)
    
    content = request.data.get("content")
    highlightAreas = request.data.get("highlightAreas")
    quote = request.data.get("quote")

    if not content or not highlightAreas or not quote:
      return Response({"detail": "[content, highlightAreas, quote] fields missing."}, status=status.HTTP_400_BAD_REQUEST,)
    
    note = Note.objects.create(paper=paper, content=content, highlightAreas=highlightAreas, quote=quote)
    serializer = NoteSerializer(note)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

