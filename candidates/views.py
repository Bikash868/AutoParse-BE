import os

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Candidate
from .serializers import CandidateSerializer
from .services import ResumeParser, AIDocumentRequestGenerator

@method_decorator(csrf_exempt, name='dispatch')
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def upload(self, request, *args, **kwargs):
        resume_file = request.FILES.get('resume')

        if not resume_file:
            return Response({'error': 'Resume file is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create temp directory if it doesn't exist
            from django.conf import settings
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save file temporarily with a unique name to avoid conflicts
            import time
            temp_filename = f"{int(time.time())}_{resume_file.name}"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Write the uploaded file to temp location
            with open(temp_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)
            
            # Parse the resume
            resume_parser = ResumeParser()
            resume_text = resume_parser.parse_resume(temp_path)

            if not resume_text:
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
                return Response({'error': 'Failed to parse resume'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new candidate
            candidate = Candidate.objects.create(
                name=resume_text.get('name'),
                email=resume_text.get('email'),
                phone=resume_text.get('phone'),
                employer=resume_text.get('employer'),
                designation=resume_text.get('designation'),
                skills=resume_text.get('skills'),
            )

            # Save the resume file to the candidate
            candidate.resume.save(resume_file.name, resume_file, save=True)

            # Remove the temporary file
            try:
                os.remove(temp_path)
            except OSError:
                pass

            serializer = self.get_serializer(candidate)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Log the error and return a proper error response
            import traceback
            print(f"Error in upload: {str(e)}")
            traceback.print_exc()
            return Response({
                'error': f'Failed to process resume: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='request-documents')
    def request_documents(self, request, pk=None):
        """Generating and logging a personalized request for PAN/Aadhaar documents."""
        try:
            candidate = self.get_object()
            
            ai_generator = AIDocumentRequestGenerator()
            message = ai_generator.generate_request(candidate)
            
            candidate.document_request_message = message
            candidate.save()
            
            return Response({
                'message': message,
                'candidate_id': candidate.id,
                'candidate_name': candidate.name
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to generate document request: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='submit-documents')
    def submit_documents(self, request, pk=None):
            """Accept uploaded PAN/Aadhaar images."""
            try:
                candidate = self.get_object()
                
                pan_card = request.FILES.get('pan_card')
                aadhar_card = request.FILES.get('aadhar_card')
                
                if not pan_card and not aadhar_card:
                    return Response({
                        'error': 'At least one document (PAN or Aadhaar) is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if pan_card:
                    candidate.pan_card = pan_card
                
                if aadhar_card:
                    candidate.aadhar_card = aadhar_card
                
                candidate.save()
                
                serializer = self.get_serializer(candidate)
                
                return Response({
                    'message': 'Documents uploaded successfully',
                    'candidate': serializer.data
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to upload documents: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
