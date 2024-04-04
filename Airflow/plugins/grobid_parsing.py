from bs4 import BeautifulSoup
import os
import sys
import pandas as pd
import re
import requests
 
# utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'utils'))
# sys.path.append(utils_path)
 
from utils.Model_PDFClass import MetaDataPDF, ContentPDF
 
current_file_dir = os.path.dirname(os.path.abspath(__file__))
files_dir = os.path.join(current_file_dir, '..', 'files')
 
class Dataset:
 
    def __init__(self):
        self.metadata = []
        self.content = []

 
    def load_data(self):
        # Call Grobid to process PDF files and generate XML
        xml_responses = self.process_pdfs_with_grobid()
 
        # Parse XML responses from Grobid
        for i, xml_response in enumerate(xml_responses):
            metadata, content = self.parse_grobid_xml(xml_response, i + 1)
            self.metadata.append(metadata)
            self.content.extend(content)
 
    def process_pdfs_with_grobid(self):
        pdf_files = [os.path.join(files_dir, f) for f in os.listdir(files_dir) if f.endswith('.pdf')]
        xml_responses = []
 
        for pdf_file in pdf_files:
            # Call Grobid via curl to process PDF and generate XML
            grobid_url = 'http://grobid_image:8070/api/processFulltextDocument'
            with open(pdf_file, 'rb') as file:
                response = requests.post(grobid_url, files={'input': file})
 
            if response.status_code == 200:
                xml_responses.append(response.text)
            else:
                print(f"Failed to process PDF: {pdf_file}")
 
        return xml_responses
 
    def parse_grobid_xml(self, xml_response, doc_id):
        soup = BeautifulSoup(xml_response, 'xml')
 
        filename = soup.find('Filename').text
        title = soup.find('Title').text
        idno = soup.find('Idno').text
 
        year = self.calculate_year(filename)
        level = self.calculate_level(filename)

 
        # Extract metadata from Grobid XML
        metadata = MetaDataPDF(
            doc_id=doc_id,
            filename=filename,
            title=title,
            idno=idno,
            year=year,
            level=level,
        )
 
        # Extract content from Grobid XML
        current_topic = None
        current_section_title = None
        contents = []
        in_initial_section = True
 
        for div in soup.find_all('div'):
            head = div.find('head')
            if head and 'LEARNING OUTCOMES' in head.text:
                # We have found a topic
                current_topic = head.find_previous('head').text.strip() if head.find_previous('head') else None
                # Turn off the flag once we reach the first 'topic' <head>
                in_initial_section = False
            elif head and in_initial_section:
                # We are in the initial section, process <head> as section_title
                current_section_title = head.text.strip()
 
                # Check if the next <head> is not 'LEARNING OUTCOMES' before processing as a new section_title
                next_head = head.find_next('head')
                if next_head and 'LEARNING OUTCOMES' not in next_head.text:
                    paragraph_text = '\n'.join([s.text.strip() for s in div.find_all(['s', 'p'])])
                    if paragraph_text or not div.find(['s', 'p']):
                        paragraph_text = paragraph_text.replace('\n', ' ').strip()
 
                        # Process paragraph_text using the existing method
                        paragraph_text = self.process_paragraph_text(paragraph_text)
 
                        # Map the level while creating ContentPDF instance
                        level_mapping = {'l1': 'Level I', 'l2': 'Level II', 'l3': 'Level III'}
                        level = level_mapping.get(metadata.level, metadata.level)
 
                        # Set default blank topic based on level
                        if not current_topic and level == 'Level I':
                            current_topic = 'Quantitative Methods'
                        elif not current_topic and level == 'Level II':
                            current_topic = 'Quantitative Methods'
                        elif not current_topic and level == 'Level III':
                            current_topic = 'Economics'
 
                        content = ContentPDF(
                            content_id=len(contents) + 1,
                            doc_id=doc_id,
                            level=level,
                            year=metadata.year,
                            topic=current_topic,
                            section_title=current_section_title,
                            paragraph_text=paragraph_text,
                        )
                        contents.append(content)
 
            elif head and current_topic is not None:
                # We are inside the section with <p><s> tags
                next_head = head.find_next('head')
                if next_head and 'LEARNING OUTCOMES' in next_head.text:
                    # Skip the current head as section_title if the next head has 'LEARNING OUTCOMES'
                    current_section_title = None
                else:
                    current_section_title = head.text.strip()
 
                    paragraph_text = '\n'.join([s.text.strip() for s in div.find_all(['s', 'p'])])
                    if paragraph_text or not div.find(['s', 'p']):
                        paragraph_text = paragraph_text.replace('\n', ' ').strip()
 
                        # Process paragraph_text using the existing method
                        paragraph_text = self.process_paragraph_text(paragraph_text)
 
                        # Map the level while creating ContentPDF instance
                        level_mapping = {'l1': 'Level I', 'l2': 'Level II', 'l3': 'Level III'}
                        level = level_mapping.get(metadata.level, metadata.level)
 
                        content = ContentPDF(
                            content_id=len(contents) + 1,
                            doc_id=doc_id,
                            level=level,
                            year=metadata.year,
                            topic=current_topic,
                            section_title=current_section_title,
                            paragraph_text=paragraph_text,
                        )
                        contents.append(content)
 
        self.content.extend(contents)
        return metadata, contents
    def calculate_level(self, filename):
        # Implement logic to calculate level based on filename
        return filename.split('-')[1].lower()
    def calculate_year(self, filename):
        # Implement logic to calculate year based on filename
        return int(filename.split('-')[0])
 
    def process_paragraph_text(self, paragraph_text):
        # Remove duplicate instances of 'The candidate should be able to: '
        paragraph_text = paragraph_text.replace('The candidate should be able to: The candidate should be able to: ', 'The candidate should be able to: ')
 
        # Replace special characters with a numbered list
        special_chars = ['□']
        for char in special_chars:
            paragraph_text = paragraph_text.replace(char, '-')
 
        return paragraph_text
    def save_metadata_to_csv(self, csv_file):
        metadata_df = pd.DataFrame([m.dict() for m in self.metadata])
        metadata_df.to_csv(csv_file, index=False)
        print(f"Metadata saved to {csv_file}")
 
    def save_content_to_csv(self, csv_file):
        content_df = pd.DataFrame([c.dict() for c in self.content])
        content_df
