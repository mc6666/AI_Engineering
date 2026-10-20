# 引入套件
from openai import OpenAI
import os, base64

# 會議紀錄語音檔
speech_file_path = "audio/3_person_meeting_short.wav"

# 定義函數將語音檔轉換為Base64格式
def to_data_url(path: str) -> str:
    with open(path, "rb") as fh:
        return "data:audio/wav;base64," + \
            base64.b64encode(fh.read()).decode("utf-8")

# 建立用戶端物件
client = OpenAI()

# 呼叫 API
with open(speech_file_path, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe-diarize",
        file=audio_file,
        response_format="diarized_json",
        chunking_strategy="auto",
        extra_body={
            "known_speaker_names": ["Tom"], # "Sameer", "Will"],
            "known_speaker_references": [
                to_data_url("audio/Tom.wav"),
                # to_data_url("audio/Sameer.wav"),
                # to_data_url("audio/Will.wav"),
            ],
        },
    )
    
# 顯示轉錄結果
for segment in transcript.segments:
    print(segment.speaker, segment.text, segment.start, segment.end)
    
    