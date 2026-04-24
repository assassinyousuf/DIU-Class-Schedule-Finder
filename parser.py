import json
import re
import os

def parse_routine_text(text):
    batches = []
    # Split text into pages/batches
    pages = re.split(r'Dhaka International University', text)
    
    for page in pages:
        if not page.strip():
            continue
            
        batch_data = {}
        
        # 1. Extract Batch Name
        batch_match = re.search(r'Batch-([\w\d\+\-]+)', page)
        if batch_match:
            batch_data['name'] = batch_match.group(1).strip()
        else:
            continue 
            
        # 2. Extract Semester
        sem_match = re.search(r'Semester-([\w\d\s\(\)\-]+)', page)
        if sem_match:
            batch_data['semester'] = re.sub(r'\s+', ' ', sem_match.group(1).strip())
            
        # 3. Extract Counsellor
        counsellor_match = re.search(r'Batch Counsellor:\s*([^\n\r]+)', page)
        if counsellor_match:
            batch_data['counsellor'] = counsellor_match.group(1).strip()
            
        # 4. Extract Batch-wide Room
        batch_room = "Unknown"
        room_match = re.search(r'Room No-\s*([\d\w\/\-]+)', page)
        if room_match:
            batch_room = room_match.group(1).strip()
        batch_data['room'] = batch_room

        # 5. Extract Academic Calendar
        calendar = []
        calendar_section = re.search(r'Academic Calendar:(.*?)(?:Web Site|Department\u2019s|$)', page, re.DOTALL | re.IGNORECASE)
        if calendar_section:
            cal_lines = calendar_section.group(1).strip().split('\n')
            for line in cal_lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    event = parts[0].strip()
                    date = parts[1].strip()
                    if event and date:
                        calendar.append({"event": event, "date": date})
        batch_data['calendar'] = calendar

        # 6. Extract Courses
        courses = []
        course_section = re.search(r'Course\s*Number\s*Course\s*Name\s*Name\s*of\s*the\s*Teacher\s*Credit(.*?)(?:Academic\s*Calendar|Mark\s*Distribution|$)', page, re.DOTALL | re.IGNORECASE)
        if course_section:
            raw_lines = course_section.group(1).strip().split('\n')
            refined_lines = []
            for line in raw_lines:
                line = line.strip()
                if not line: continue
                # If line starts with a code, it's a new course
                if re.match(r'^([A-Z\d\-]{5,})', line):
                    refined_lines.append(line)
                elif refined_lines:
                    # Otherwise, it's a continuation of the previous course
                    refined_lines[-1] += " " + line
            
            for line in refined_lines:
                match = re.match(r'^(?P<code>[A-Z\d\-]+)\s+(?P<rest>.+)$', line.strip())
                if match:
                    code = match.group('code')
                    rest = match.group('rest')
                    credit_match = re.search(r'(?P<teacher_info>.+)\s+(?P<credit>\d+\.\d+)$', rest)
                    if credit_match:
                        teacher_info = credit_match.group('teacher_info').strip()
                        credit = credit_match.group('credit')
                        
                        # Try to separate course name and teacher
                        # Usually teacher starts with Md. Dr. Mr. Ms. Prof.
                        parts = re.split(r'\s+(?=Md\.|Dr\.|Mr\.|Ms\.|Prof\.|Mrs\.)', teacher_info)
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            teacher = " ".join(parts[1:]).strip()
                        else:
                            name = teacher_info
                            teacher = "N/A"
                        courses.append({"code": code, "name": name, "teacher": teacher, "credit": credit.strip()})
        batch_data['courses'] = courses

        # 7. Extract Schedule with Times and Specific Rooms
        schedule = []
        time_slot_matches = re.findall(r'(\d{1,2}:\d{2}-\d{1,2}:\d{2})', page)
        
        days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day in days:
            # Match the day row and the lines following it until the next day or section
            day_regex = day + r'\s+([^\n\r]+(?:(?!\n(?:' + '|'.join(days) + r'|Course Number)).)*)'
            day_match = re.search(day_regex, page, re.DOTALL)
            if day_match:
                section_text = day_match.group(1)
                
                # Check for line-specific room (e.g., Room-805)
                row_room_match = re.search(r'Room-([\d\w\-]+)', section_text)
                row_room = row_room_match.group(1) if row_room_match else batch_room
                
                # Split section into chunks by course code
                chunks = re.split(r'(\d{4,}-\d{3,}|[A-Z]+-\d{3,})', section_text)
                current_time_idx = 0
                
                for i in range(1, len(chunks), 2):
                    code = chunks[i]
                    following_text = chunks[i+1] if i+1 < len(chunks) else ""
                    
                    # Detect specific room for this code (e.g., Lab-1)
                    lab_match = re.search(r'(Lab-[\d\w]+)', following_text)
                    slot_room = lab_match.group(1) if lab_match else row_room
                    
                    # Detect specific time if overriden
                    time_match = re.search(r'Time:\s*(\d{1,2}:\d{2}-\d{1,2}:\d{2})', following_text)
                    slot_time = time_match.group(1) if time_match else (time_slot_matches[current_time_idx] if current_time_idx < len(time_slot_matches) else "TBA")
                    
                    schedule.append({
                        "day": day,
                        "time": slot_time,
                        "course_code": code,
                        "room": slot_room
                    })
                    current_time_idx += 1

        batch_data['schedule'] = schedule
        batches.append(batch_data)
    
    return batches

def main():
    if not os.path.exists("extracted_routines.json"):
        print("Error: extracted_routines.json not found.")
        return
        
    with open("extracted_routines.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    all_batches = []
    for file_name, text in raw_data.items():
        all_batches.extend(parse_routine_text(text))
        
    with open("routines.json", "w", encoding="utf-8") as f:
        json.dump({"batches": all_batches}, f, indent=4)
    print(f"Successfully parsed {len(all_batches)} batches into routines.json")

if __name__ == "__main__":
    main()
