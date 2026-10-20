# 引入套件
from openai import OpenAI
import os

# 讀取語音檔
speech_file_path = "output/speech.mp3"
audio_file = open(speech_file_path, "rb")

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
with open("meeting.wav", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio_file,
        prompt="A customer support call about a premium plan and account AC-42.",
        extra_body={
            "keywords": ["premium plan", "AC-42", "billing"],
            "languages": ["en", "fr"],
        },
    )

# 顯示轉錄結果
print(transcription.text)
    