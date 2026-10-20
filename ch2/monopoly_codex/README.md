# 大富翁 PyGame 原型

這個專案提供一個可執行的 `PyGame` 大富翁原型，包含：

- 2~5 人遊戲選擇
- 每人初始資金 `$500`
- 擲骰子移動與動畫
- 空地購買、蓋房、過路費
- 機會 / 命運卡
- 監獄、免獄通行證、保釋金
- 破產淘汰與勝利判定

## 執行

```bash
pip install -r requirements.txt
python main.py
```

## 資產路徑

你可以自行放入圖片、音效、音樂，程式會自動嘗試讀取下列位置：

- `assets/tiles/00.png` ~ `assets/tiles/19.png`
- `assets/tiles/start.png`
- `assets/tiles/land.png`
- `assets/tiles/chance.png`
- `assets/tiles/fate.png`
- `assets/tiles/jail.png`
- `assets/images/tile.png`
- `assets/sounds/dice.wav`
- `assets/sounds/chance.wav`
- `assets/sounds/jail.wav`
- `assets/sounds/release.wav`
- `assets/music/background.ogg`

找不到檔案時，程式會自動改用內建圖形與文字，不會中斷。

## 操作

- `Space` 擲骰
- `Esc` 離開
- `F11` 切換全螢幕

## 架構

`main.py` 使用物件導向設計，主要類別包括：

- `MonopolyGame`
- `Player`
- `Tile`
- `Card`
- `Button`
- `AssetManager`
