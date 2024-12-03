from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Note
    fields = ['note_id', 'paper', 'content', 'highlightAreas', 'quote']
    read_only_fields = ['paper']