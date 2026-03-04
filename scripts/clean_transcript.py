import re

def clean_vtt(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove WEBVTT header and metadata
    lines = content.split('\n')
    clean_lines = []
    
    # Regex to match timestamps like 00:00:00.000 --> 00:00:00.000
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{2}:\d{2}:\d{2}\.\d{3}')
    
    # Regex to match tags like <c> or <00:00:00.000>
    tag_pattern = re.compile(r'<[^>]+>')

    for line in lines:
        # Skip header lines
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        
        # Skip timestamp lines
        if timestamp_pattern.match(line):
            continue
            
        # Remove tags from text lines
        clean_line = tag_pattern.sub('', line).strip()
        
        # Skip empty lines
        if clean_line:
            clean_lines.append(clean_line)

    # Join and deduplicate consecutive duplicate lines (common in VTT)
    final_text = []
    if clean_lines:
        final_text.append(clean_lines[0])
        for i in range(1, len(clean_lines)):
            if clean_lines[i] != clean_lines[i-1]:
                final_text.append(clean_lines[i])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(' '.join(final_text))

if __name__ == "__main__":
    input_file = "/root/.openclaw/workspace/downloads/ai_projects_video.vtt.en.vtt"
    output_file = "/root/.openclaw/workspace/downloads/clean_transcript.txt"
    try:
        clean_vtt(input_file, output_file)
        print(f"Successfully cleaned transcript to: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
