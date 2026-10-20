# 引入套件
from openai import OpenAI
from pathlib import Path
import os
from playsound import playsound

# 語音檔
speech_file_path = "d:/tmp/speech.mp3"

# 建立用戶端物件
client = OpenAI()

# 建立 d:/tmp 資料夾
os.makedirs("d:/tmp", exist_ok=True)

# 呼叫 API
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="Today is a wonderful day to build something people love!",
    instructions="Speak in a cheerful and positive tone.",
) as response:
    # 存檔
    response.stream_to_file(speech_file_path)

# 播放語音檔
playsound(speech_file_path)
    