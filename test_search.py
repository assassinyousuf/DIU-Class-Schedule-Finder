import json

def test_search(term):
    with open("routines.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        batches = data['batches']
        
    term = term.lower().strip()
    filtered = []
    for batch in batches:
        match = False
        if term in (batch.get('name', '') or '').lower(): match = True
        if term in (batch.get('semester', '') or '').lower(): match = True
        if term in (batch.get('counsellor', '') or '').lower(): match = True
        
        if batch.get('schedule'):
            for s in batch['schedule']:
                if term in (s.get('day', '') or '').lower(): match = True
                if term in (s.get('time', '') or '').lower(): match = True
                if term in (s.get('course_code', '') or '').lower(): match = True
                
        if batch.get('calendar'):
            for c in batch['calendar']:
                if term in (c.get('event', '') or '').lower(): match = True
                if term in (c.get('date', '') or '').lower(): match = True
                
        if batch.get('courses'):
            for c in batch['courses']:
                if term in (c.get('name', '') or '').lower(): match = True
                if term in (c.get('code', '') or '').lower(): match = True
                if term in (c.get('teacher', '') or '').lower(): match = True
                
        if match:
            filtered.append(batch['name'])
            
    return filtered

print(f"Results for 'Sunday': {len(test_search('Sunday'))}")
print(f"Results for '8:30': {len(test_search('8:30'))}")
print(f"Results for 'Mid-term': {len(test_search('Mid-term'))}")
print(f"Results for '19.02.2026': {len(test_search('19.02.2026'))}")
