# 引入套件
from openai import OpenAI
import os

# 讀取語音檔
speech_file_path = "audio/3_person_meeting_short.mp3"
audio_file = open(speech_file_path, "rb")

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
transcription = client.audio.transcriptions.create(
    model="gpt-transcribe", file=audio_file
)

# 顯示轉錄結果
print(transcription.text)
    