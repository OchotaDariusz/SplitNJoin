#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path

def check_dependencies():
    dependencies = {
        'ffmpeg': False,
        'opencv': False
    }
    
    # Sprawdzanie FFmpeg
    if shutil.which('ffmpeg') is not None:
        dependencies['ffmpeg'] = True
    
    # Sprawdzanie OpenCV
    try:
        import cv2
        dependencies['opencv'] = True
    except ImportError:
        pass
        
    return dependencies

class VideoProcessor:
    def __init__(self):
        self.deps = check_dependencies()
        if not any(self.deps.values()):
            print("BŁĄD: Nie znaleziono ani FFmpeg ani OpenCV!")
            print("Zainstaluj jedną z wymaganych zależności:")
            print("1. FFmpeg: https://ffmpeg.org/download.html")
            print("2. OpenCV: pip install opencv-python")
            sys.exit(1)
    
    def extract_frames(self, video_path, output_dir):
        """Ekstrahuje klatki z wideo do podanego katalogu."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if self.deps['opencv']:
            return self._extract_frames_opencv(video_path, output_dir)
        elif self.deps['ffmpeg']:
            return self._extract_frames_ffmpeg(video_path, output_dir)
    
    def _extract_frames_opencv(self, video_path, output_dir):
        """Ekstrahuje klatki używając OpenCV"""
        import cv2
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        # Pobierz FPS z oryginalnego wideo
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            output_path = os.path.join(output_dir, f'frame_{frame_count:06d}.jpg')
            cv2.imwrite(output_path, frame)
            frame_count += 1
            
            # Pokazuj postęp
            if frame_count % 100 == 0:
                print(f"Wyekstrahowano {frame_count} klatek...")
        
        cap.release()
        return fps, frame_count
    
    def _extract_frames_ffmpeg(self, video_path, output_dir):
        """Ekstrahuje klatki używając FFmpeg"""
        import subprocess
        import json
        
        # Pobierz informacje o wideo
        probe_cmd = ['ffmpeg', '-i', video_path, '-print_format', 'json', '-show_format', '-show_streams', '-v', 'quiet']
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        
        # Znajdź strumień wideo i pobierz FPS
        video_stream = next(s for s in info['streams'] if s['codec_type'] == 'video')
        fps = eval(video_stream['r_frame_rate'])  # Konwertuje string "24000/1001" na liczbę
        
        # Ekstrahuj klatki
        output_pattern = os.path.join(output_dir, 'frame_%06d.jpg')
        cmd = ['ffmpeg', '-i', video_path, '-vf', 'fps=' + str(fps), output_pattern]
        subprocess.run(cmd)
        
        # Policz ilość wyekstrahowanych klatek
        frame_count = len([f for f in os.listdir(output_dir) if f.startswith('frame_')])
        return fps, frame_count
    
    def join_frames(self, frames_dir, output_path, fps=30):
        """Łączy klatki w wideo."""
        if self.deps['opencv']:
            return self._join_frames_opencv(frames_dir, output_path, fps)
        elif self.deps['ffmpeg']:
            return self._join_frames_ffmpeg(frames_dir, output_path, fps)
    
    def _join_frames_opencv(self, frames_dir, output_path, fps):
        """Łączy klatki używając OpenCV"""
        import cv2
        
        # Pobierz listę plików klatek
        frames = sorted([f for f in os.listdir(frames_dir) if f.startswith('frame_')])
        if not frames:
            raise ValueError("Nie znaleziono klatek w podanym katalogu!")
        
        # Wczytaj pierwszą klatkę aby uzyskać wymiary
        first_frame = cv2.imread(os.path.join(frames_dir, frames[0]))
        height, width = first_frame.shape[:2]
        
        # Utwórz writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Zapisz wszystkie klatki
        for idx, frame in enumerate(frames):
            img = cv2.imread(os.path.join(frames_dir, frame))
            out.write(img)
            if idx % 100 == 0:
                print(f"Przetworzono {idx} klatek...")
        
        out.release()
        print(f"Zapisano wideo do: {output_path}")
    
    def _join_frames_ffmpeg(self, frames_dir, output_path, fps):
        """Łączy klatki używając FFmpeg"""
        import subprocess
        
        input_pattern = os.path.join(frames_dir, 'frame_%06d.jpg')
        cmd = [
            'ffmpeg', '-y',  # Nadpisz istniejący plik
            '-framerate', str(fps),
            '-i', input_pattern,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        subprocess.run(cmd)
        print(f"Zapisano wideo do: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Narzędzie do przetwarzania wideo na klatki i z powrotem')
    parser.add_argument('--mode', choices=['extract', 'join'], required=True,
                       help='Tryb działania: extract (rozdziel) lub join (połącz)')
    parser.add_argument('--input', required=True,
                       help='Ścieżka do pliku wideo (dla extract) lub katalogu z klatkami (dla join)')
    parser.add_argument('--output', required=True,
                       help='Ścieżka do katalogu wyjściowego (dla extract) lub pliku wideo (dla join)')
    parser.add_argument('--fps', type=float, default=30,
                       help='Klatki na sekundę (tylko dla trybu join)')
    
    args = parser.parse_args()
    
    processor = VideoProcessor()
    
    try:
        if args.mode == 'extract':
            fps, count = processor.extract_frames(args.input, args.output)
            print(f"Wyekstrahowano {count} klatek z FPS={fps}")
        else:  # join
            processor.join_frames(args.input, args.output, args.fps)
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
