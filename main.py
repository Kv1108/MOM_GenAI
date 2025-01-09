from docx import Document
from datetime import datetime, timedelta
import re

# Function to parse the text file
def parse_text_file(file_path):
    speakers = set()
    discussion_points = []
    start_time, end_time = None, None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'\[(\d{2}:\d{2}:\d{2})\] \[([^\]]+)\]: (.+)', line)
            if match:
                time_str, speaker, message = match.groups()
                time = datetime.strptime(time_str, "%H:%M:%S")
                speakers.add(speaker)

                # Extract general discussion points
                discussion_points.append(f"{speaker} discussed: {message.strip()}")

                # Capture start and end time
                if not start_time:
                    start_time = time
                end_time = time

    return start_time, end_time, speakers, discussion_points

# Function to create the MOM document
def create_mom(file_path, output_file, title, date):
    start_time, end_time, speakers, discussion_points = parse_text_file(file_path)
    duration = str(end_time - start_time)
    no_of_people = len(speakers)

    document = Document()
    document.add_heading(title, level=1)

    # Add meeting details
    document.add_paragraph(f"Meeting Date: {date}")
    document.add_paragraph(f"Meeting Time: {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
    document.add_paragraph(f"Meeting Duration: {duration}")
    document.add_paragraph(f"No. of People Attended: {no_of_people}")

    # Agenda Section
    document.add_heading('Agenda Topics', level=2)
    document.add_paragraph("1. Team Updates\n2. Discussion on Current Issues\n3. Suggestions and Improvements", style='List Number')

    # General Discussion Section
    document.add_heading('General Discussion Points', level=2)
    for point in discussion_points:
        document.add_paragraph(point, style='List Bullet')

    # Suggestions Section
    document.add_heading('Suggestions', level=2)
    document.add_paragraph("1. Ensure better communication between team members.\n2. Schedule weekly check-ins to track progress.\n3. Assign specific roles for upcoming tasks.", style='List Number')

    # Remarks Section
    document.add_heading('Remarks', level=2)
    document.add_paragraph("The meeting concluded successfully with actionable insights.")

    # Save the document
    document.save(output_file)
    print(f"MOM generated successfully: {output_file}")

# Main execution
file_path = '02-01-2025-15-34-05_transcription.txt'  # Input text file
output_file = 'MOM_Summary.docx'                    # Output Word document
title = 'Team Meeting: Project Summary'             # Meeting title
date = '2025-01-02'                                 # Meeting date

create_mom(file_path, output_file, title, date)
