# Message Scope Downgraded (訊息範圍降級)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-I
> 信心度: VERIFIED
> 前置知識: act() 函式與 TO_ROOM/TO_CHAR 語義
> 相關原子: patterns/act-function, patterns/message-scope
> 觸發條件: C 中的房間廣播在 C# 變成私人訊息

## 知識

MUD 中訊息傳遞有不同範圍（scope）。移植時容易將廣播訊息
降級為私人訊息，導致其他玩家看不到應該看到的互動。

**C 的訊息範圍系統：**
```c
// TO_CHAR  — 只有行為者本人看到
// TO_ROOM  — 房間內除行為者外所有人看到
// TO_VICT  — 只有目標看到
// TO_NOTVICT — 房間內除行為者和目標外所有人看到

// 房間廣播範例
act("$n說：'$T'", ch, NULL, argument, TO_ROOM);
send_to_char("你說：", ch);
```

**錯誤移植（範圍降級）：**
```csharp
// 錯誤：do_say 變成只有自己看到
ch.SendToChar($"你說：'{argument}'\n");
// 遺漏了 TO_ROOM 的廣播！
```

**正確移植：**
```csharp
// 正確：保持房間廣播
Act($"$n說：'{argument}'", ch, null, null, ToType.Room);
ch.SendToChar($"你說：'{argument}'\n");
```

**常見降級模式：**
| C 原始                    | 錯誤 C#           | 正確 C#                |
|---------------------------|--------------------|-----------------------|
| `act(TO_ROOM)`            | `SendToChar`       | `Act(ToType.Room)`   |
| `do_say` (房間廣播)       | `SendToChar`       | `Act` + `SendToChar` |
| `send_to_room`            | `SendToChar`       | `SendToRoom`         |
| `act(TO_NOTVICT)`         | 完全遺漏           | `Act(ToType.NotVict)`|

**為什麼危險：**
- 遊戲互動性大幅降低（別人看不到你的動作）
- 社交指令（say, emote, yell）完全失效
- 戰鬥訊息只有自己看到

## 行動

1. 在 C 原始碼中搜尋 `act(` 和 `TO_ROOM`
2. 確認 C# 中每個 act 呼叫保持相同的範圍參數
3. 搜尋 C# 中所有 `SendToChar`，確認是否應為廣播
4. 補齊所有遺漏的廣播呼叫

## 驗證

- grep C 中所有 `TO_ROOM` 出現次數
- grep C# 中對應的 `ToType.Room` 出現次數
- 兩者數量應大致相等

## 失敗時

→ patterns/act-function, patterns/message-scope
