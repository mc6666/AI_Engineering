# 引入套件
import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

# 建立非同步用戶端物件
client = AsyncOpenAI()

# 定義函數呼叫非同步 API
async def main():
    async with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="marin",
        input="今天清晨俄羅斯強震引發海嘯，民眾緊急撤離",
        instructions="Speak in a serious and neutral tone.",
        response_format="pcm",
    ) as response:
        # 播放語音
        await LocalAudioPlayer().play(response)

# 主程式
if __name__ == "__main__":
    asyncio.run(main())
    