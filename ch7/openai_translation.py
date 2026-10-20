# 引入套件
from openai import OpenAI
import os

# 讀取語音檔
speech_file_path = "audio/speech_CHINESE.mp3"
audio_file = open(speech_file_path, "rb")

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
translation = client.audio.translations.create(
    model="whisper-1",
    file=audio_file,
)


# 顯示翻譯結果
print(translation.text)
    