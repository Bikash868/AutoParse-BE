import re
import json


class ResumeParser:
    def __init__(self, resume_path):
        self.resume_path = resume_path

    def parse(self):
        with open(self.resume_path, 'r') as file:
            resume_text = file.read()
        return resume_text

class AIDocumentRequest:
	def __init__(self, document_path):
		self.document_path = document_path

	def request(self):
		with open(self.document_path, 'r') as file:
			document_text = file.read()
		return document_text
