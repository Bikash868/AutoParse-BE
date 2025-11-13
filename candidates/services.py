import os
import json
import re

import PyPDF2
import docx
from anthropic import Anthropic


class ResumeParser:
    def __init__(self):
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None

    def parse_pdf(self, resume_path):
        with open(resume_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            resume_text = ''
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
            return resume_text

    def parse_docx(self, resume_path):
        with open(resume_path, 'rb') as file:
            docx_reader = docx.Document(file)
            resume_text = ''
            for paragraph in docx_reader.paragraphs:
                resume_text += paragraph.text
            return resume_text

    def parse_doc(self, resume_path):
        with open(resume_path, 'rb') as file:
            doc_reader = docx.Document(file)
            resume_text = ''
            for paragraph in doc_reader.paragraphs:
                resume_text += paragraph.text
            return resume_text

    def extract_fields_with_ai(self, resume_text):
        """Using Anthropic API to extract structured fields from resume text."""
        if not self.anthropic:
            # Fallback: return empty dict if no API key
            print('Anthropic API key is not set')
            return {
                'name': None,
                'email': None,
                'phone': None,
                'employer': None
            }

        prompt = f"""Extract the following information from this resume and return ONLY a valid JSON object with these exact keys: name, email, phone, employer (current or most recent employer).

If a field is not found, use null for that field.

Resume text:
{resume_text}

Return only the JSON object, no other text."""

        try:
            # print("Calling Anthropic API...")
            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            print(f"API Response: {response_text}")
            
            # Try to extract JSON from the response
            # Sometimes Claude wraps it in markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            parsed_data = json.loads(response_text)
            # print(f"Parsed data: {parsed_data}")
            return parsed_data
        except Exception as e:
            # Log the error so we can see what went wrong
            print(f"Error in extract_fields_with_ai: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'name': None,
                'email': None,
                'phone': None,
                'employer': None
            }

    def parse_resume(self, resume_path):
        if resume_path is None:
            raise ValueError('Resume path is not set')

        if resume_path.endswith('.pdf'):
            resume_text = self.parse_pdf(resume_path)
        elif resume_path.endswith('.docx'):
            resume_text = self.parse_docx(resume_path)
        elif resume_path.endswith('.doc'):
            resume_text = self.parse_doc(resume_path)
        else:
            raise ValueError('Unsupported file type')

        if not resume_text:
            raise ValueError('Failed to parse resume')

        print("resume_text:", resume_text)

        # Extract structured fields using AI
        candidate_data = self.extract_fields_with_ai(resume_text)
        return candidate_data


class AIDocumentRequest:
    def __init__(self, document_path):
        self.document_path = document_path

    def request(self):
        with open(self.document_path, 'r') as file:
            document_text = file.read()
        return document_text
