from django.core.management.base import BaseCommand
from recommender.models import YouTuber

YOUTUBERS = [
    {
        "name": "愛莉莎莎",
        "channel_name": "愛莉莎莎 Alisasa",
        "youtube_url": "https://www.youtube.com/@alisasa",
        "description": "以精緻打卡風格聞名，專注介紹外觀漂亮、氛圍佳的餐廳與甜點店，深受年輕女性喜愛。",
        "style_keywords": "網紅打卡、外觀精緻、甜點、下午茶、氛圍感",
    },
    {
        "name": "台客劇場",
        "channel_name": "台客劇場",
        "youtube_url": "https://www.youtube.com/@taiketeatre",
        "description": "深入台灣各地挖掘在地小吃與古早味，走訪市場、夜市，呈現最道地的庶民美食文化。",
        "style_keywords": "在地小吃、古早味、平價、夜市、市場、庶民美食",
    },
    {
        "name": "喜翔",
        "channel_name": "喜翔",
        "youtube_url": "https://www.youtube.com/@hsiangeat",
        "description": "台南在地美食達人，擅長介紹台南府城傳統料理與海鮮，常帶觀眾造訪在地人才知道的隱藏版餐廳。",
        "style_keywords": "台南、海鮮、在地人推薦、傳統料理、隱藏版",
    },
    {
        "name": "蔡阿嘎",
        "channel_name": "蔡阿嘎 Life",
        "youtube_url": "https://www.youtube.com/@tsaiago",
        "description": "以搞笑幽默風格介紹台灣各地美食，常探訪巷弄小店、排隊名店，接地氣又有趣。",
        "style_keywords": "搞笑、台式、巷弄小店、排隊名店、接地氣",
    },
    {
        "name": "滴妹",
        "channel_name": "滴妹",
        "youtube_url": "https://www.youtube.com/@dimei",
        "description": "熱愛日系風格咖啡廳與飲料店，喜歡推薦文青感十足的輕食餐廳與特色手搖飲品。",
        "style_keywords": "日系、飲料、文青、咖啡廳、輕食、手搖飲",
    },
    {
        "name": "Edwin 吃什麼",
        "channel_name": "Edwin 吃什麼",
        "youtube_url": "https://www.youtube.com/@edwineat",
        "description": "專注高品質餐飲體驗，常介紹燒肉、火鍋、日式料理等中高單價餐廳，追求食材與服務的極致。",
        "style_keywords": "燒肉、火鍋、日式料理、高單價、品質至上",
    },
]


class Command(BaseCommand):
    help = "預填 6 位台灣美食 YouTuber 資料"

    def handle(self, *args, **options):
        created = 0
        for data in YOUTUBERS:
            obj, is_new = YouTuber.objects.get_or_create(
                name=data["name"],
                defaults=data,
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  新增：{obj.name}"))
            else:
                self.stdout.write(f"  已存在：{obj.name}（略過）")

        self.stdout.write(self.style.SUCCESS(f"\n完成！共新增 {created} 位 YouTuber。"))
