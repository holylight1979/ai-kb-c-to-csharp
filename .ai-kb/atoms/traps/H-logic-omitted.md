# Logic Omitted (大量邏輯區塊被省略)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-H
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: verification/line-count-check
> 觸發條件: C 函式行數遠大於 C# 對應函式（比率 > 3:1）

## 知識

大型 C 函式在移植時，整段邏輯區塊可能被完全省略。
這與 E-fake-completion（空 stub）不同 — 函式有部分實作，
看起來有在做事，但大量邏輯被靜默跳過。

**典型案例：char_to_room**

C 原始碼：~150 行
```c
void char_to_room(CHAR_DATA *ch, ROOM_INDEX_DATA *pRoomIndex)
{
    // 基本鏈結設定 (10行)
    ch->in_room = pRoomIndex;
    ch->next_in_room = pRoomIndex->people;
    pRoomIndex->people = ch;

    // 光源處理 (15行)
    if (IS_AFFECTED(ch, AFF_GLOW))
        pRoomIndex->light++;

    // 隱藏/偵測處理 (20行)
    // 飛行/游泳地形檢查 (25行)
    // 陷阱觸發 (30行)
    // 房間程式觸發 (20行)
    // 特殊區域效果 (30行)
}
```

C# 移植：~15 行（只有基本鏈結）
```csharp
public void CharToRoom(CharData ch, RoomIndexData room)
{
    ch.InRoom = room;
    room.People.Add(ch);
    // 其餘 135 行的邏輯完全缺失
}
```

**偵測準則：**
- C 行數 > C# 行數 × 3 → 高度警戒
- C 行數 > C# 行數 × 5 → 幾乎確定有遺漏
- 特別注意超過 100 行的 C 函式

**高風險大型函式：**
- `char_to_room` / `char_from_room`
- `do_look` / `do_scan`
- `one_hit` / `multi_hit`
- `spell_*` 系列法術函式
- `update_handler` 主循環

## 行動

1. 用 line-count-check 比對所有函式的行數比
2. 標記比率 > 3:1 的函式
3. 逐一檢查遺漏的邏輯區塊
4. 補齊所有遺漏的邏輯

## 驗證

```bash
# 行數比對工具
python -X utf8 tools/line-count-check.py
# 所有函式比率應 < 3:1（考慮 C# 較精簡的語法）
```

## 失敗時

→ verification/line-count-check
