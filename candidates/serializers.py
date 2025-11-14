from rest_framework import serializers
from .models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'employer',
            'designation',
            'skills',
            'resume',
            'aadhar_card',
            'pan_card',
            'document_request_message',
            'created_at',
            'updated_at'
        ]