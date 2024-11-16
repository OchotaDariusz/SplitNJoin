Stworzę dla Ciebie skrypt konsolowy, który będzie obsługiwał rozdzielanie i łączenie klatek wideo z obsługą różnych zależności.



Aby zainstalować wymagane biblioteki, użyj następujących komend:

```bash
pip install opencv-python    # Podstawowa instalacja OpenCV
pip install opencv-python-headless  # Wersja bez GUI (opcjonalnie, dla serwerów)
```

FFmpeg należy zainstalować osobno, w zależności od systemu operacyjnego:
- Windows: Pobierz z https://ffmpeg.org/download.html lub użyj `winget install ffmpeg`
- Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) lub `sudo dnf install ffmpeg` (Fedora)
- macOS: `brew install ffmpeg`

Użycie skryptu:

1. Rozdzielanie wideo na klatki:
```bash
python script.py --mode extract --input video.mp4 --output frames_folder
```

2. Łączenie klatek w wideo:
```bash
python script.py --mode join --input frames_folder --output output_video.mp4 --fps 30
```

Skrypt zapewnia:
- Automatyczne wykrywanie dostępności FFmpeg i OpenCV
- Wybór najlepszej dostępnej metody
- Postęp operacji
- Obsługę błędów
- Zachowanie oryginalnego FPS przy ekstrakcji
- Możliwość określenia FPS przy łączeniu
- Nazywanie klatek w formacie umożliwiającym prawidłowe sortowanie

Dodatkowo skrypt:
- Sprawdza poprawność ścieżek wejściowych/wyjściowych
- Tworzy katalogi wyjściowe jeśli nie istnieją
- Wyświetla informacje o postępie dla długich operacji
- Obsługuje różne formaty wideo
- Zapewnia spójną numerację klatek

Jeśli potrzebujesz dodatkowych funkcji lub modyfikacji, daj znać!