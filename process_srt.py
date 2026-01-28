from datetime import datetime
import os
import json

def nonsense(text):
    if not text.strip():
        return True
    keywords = ['感谢', '打赏', '点歌', '放一下']
    return any(keyword in text for keyword in keywords)

def chunk2str(chunk):
    text = '，'.join(filter(lambda x: not nonsense(x), chunk))
    question_suffix = ['吗', '对吧', '是吧', '呢']
    end = '？' if any(text.endswith(s) for s in question_suffix) else '。'
    return text + end

def abstime(timestamp):     # %H:%M:%S,%f
    h, m, s_ms = timestamp.strip().replace(',', '.').split(':')
    return int(h)*3600 + int(m)*60 + float(s_ms)

def read_chunks(filename):
    chunks = []
    with open(filename, 'r', encoding='utf-8') as f:
        index = 1
        threshold = 5  # seconds
        chunk = []
        chunk_start = None 
        chunk_idx = 0
        while True:
            if not f.readline().startswith(str(index)):
                break
            start, end = f.readline().split('-->')
            start, end = abstime(start), abstime(end)
            text = f.readline()
            f.readline()
            if index > 1:
                if start - chunk_end > threshold:
                    chunks.append({'time': (chunk_start, chunk_end), 'index': (chunk_idx, index-1), 'text': chunk2str(chunk)})
                    chunk = []
            if not chunk:
                chunk_start = start
                chunk_idx = index
            chunk.append(text.strip())
            chunk_end = end
            index += 1
    return chunks

def main():
    video_dir = 'srt'
    all = []
    for root, _, files in os.walk(video_dir):
        for file in files:
            # if file.endswith('.srt') and '_' not in file:
            file_path = os.path.join(root, file)
            chunks = read_chunks(file_path)
            bv = os.path.splitext(file)[0].split('-')[-1]
            all.append({
                'bv': bv,
                'filename': file,
                'chunks': chunks,
            })
    
    with open('docs/all_subtitles.json', 'w', encoding='utf-8') as f:
        json.dump(all, f, ensure_ascii=False, indent=2)
    with open('docs/all_subtitles.min.json', 'w', encoding='utf-8') as f:
        json.dump(all, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    main()