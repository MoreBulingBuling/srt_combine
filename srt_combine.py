import os
from datetime import datetime, timedelta

def parse_srt_time(srt_time):
    """解析SRT格式的时间字符串到datetime对象"""
    return datetime.strptime(srt_time, '%H:%M:%S,%f')

def format_srt_time(dt):
    """格式化datetime对象到SRT格式的时间字符串"""
    return dt.strftime('%H:%M:%S,%f')[:-3]

def apply_offset_to_subtitle(subtitle, offset):
    """给定时间偏移量，应用到字幕的时间戳上"""
    start_time = parse_srt_time(subtitle[0])
    end_time = parse_srt_time(subtitle[1])
    
    new_start_time = (start_time + offset).time()
    new_end_time = (end_time + offset).time()
    
    return [format_srt_time(new_start_time), format_srt_time(new_end_time)]

def merge_subtitles(base_file, additional_file, offset_str, output_file):
    """合并两个字幕文件，第二个文件的时间戳加上偏移量"""
    offset = datetime.strptime(offset_str, '%H:%M:%S,%f') - datetime.min
    
    with open(base_file, 'r', encoding='utf-8') as f:
        base_lines = f.readlines()
    
    with open(additional_file, 'r', encoding='utf-8') as f:
        additional_lines = f.readlines()

    # Process and offset the second subtitle file
    processed_additional_lines = []
    index = 0
    while index < len(additional_lines):
        line = additional_lines[index].strip()
        if '-->' in line:  # If it's a time stamp line
            start, end = line.split(' --> ')
            new_times = apply_offset_to_subtitle([start, end], offset)
            processed_additional_lines.append(f"{new_times[0]} --> {new_times[1]}\n")
            index += 1
            # Add the subtitle text lines until an empty line is found
            while index < len(additional_lines) and additional_lines[index].strip():
                processed_additional_lines.append(additional_lines[index])
                index += 1
            processed_additional_lines.append('\n')  # Add blank line between subtitles
        index += 1

    # Write merged subtitles to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(base_lines + processed_additional_lines)

def find_and_merge_subtitles(directory, offset_str):
    """查找并合并目录中所有匹配模式的字幕文件"""
    for root, dirs, files in os.walk(directory):
        # Create a dictionary to hold pairs of subtitle files
        subtitle_pairs = {}
        for file in files:
            if file.endswith('.srt'):
                name, ext = os.path.splitext(file)
                parts = name.split('-')
                if len(parts) > 2 and parts[-1].isdigit():
                    base_name = '-'.join(parts[:-1])
                    subtitle_pairs.setdefault(base_name, []).append(file)

        # Merge subtitle files that have both -1.srt and -2.srt versions
        for base_name, files in subtitle_pairs.items():
            if len(files) == 2 and all(x in files for x in [f"{base_name}-1.srt", f"{base_name}-2.srt"]):
                output_filename = f"{base_name}.srt"
                print(f"Merging {files} into {output_filename}")
                merge_subtitles(
                    os.path.join(root, f"{base_name}-1.srt"),
                    os.path.join(root, f"{base_name}-2.srt"),
                    offset_str,
                    os.path.join(root, output_filename)
                )

if __name__ == '__main__':
    # Define the offset you want to add to the -2.srt file times
    offset = "01:59:47,02"  # Format HH:MM:SS,ms
    # Call the function to find and merge subtitles in the current directory
    find_and_merge_subtitles('.', offset)