# Call-to-Assign (函式呼叫簡化為賦值)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-F
> 信心度: VERIFIED
> 前置知識: C 函式副作用概念
> 相關原子: patterns/stop-fighting, patterns/char-list-traversal
> 觸發條件: C 函式呼叫在 C# 中變成簡單賦值語句

## 知識

C MUD 程式碼中許多函式不只是設定一個值，還包含走訪鏈結串列、
通知其他物件等副作用。移植時若將函式呼叫簡化為單一賦值，
會遺漏這些關鍵副作用。

**典型案例：stop_fighting**

C 原始碼：
```c
void stop_fighting(CHAR_DATA *ch, bool fBoth)
{
    CHAR_DATA *fch;
    // 走訪整個 char_list，停止所有與 ch 戰鬥的角色
    for (fch = char_list; fch != NULL; fch = fch->next)
    {
        if (fch->fighting == ch || (fBoth && fch == ch))
        {
            fch->fighting = NULL;
            fch->position = IS_NPC(fch) ? fch->default_pos : POS_STANDING;
            update_pos(fch);
        }
    }
}
```

錯誤移植（簡化為賦值）：
```csharp
// 嚴重錯誤：遺漏了走訪 char_list 的副作用
ch.Fighting = null;
```

正確移植：
```csharp
StopFighting(ch, true);
// StopFighting 內部必須走訪所有角色
```

**其他高風險函式：**
- `extract_char` — 不只是移除，還要清理所有引用
- `char_from_room` — 不只是設 null，還要更新房間鏈結
- `obj_from_char` — 更新攜帶重量、物品數量
- `affect_remove` — 可能觸發其他效果

## 行動

1. 找到 C 中被簡化的函式定義
2. 檢查函式是否有副作用（迴圈、通知、更新其他物件）
3. 若有副作用，必須實作完整函式而非簡單賦值
4. 比對 C 與 C# 的行數差異

## 驗證

- 比對 C 函式行數與 C# 實作行數
- 若 C 函式 > 5 行而 C# 只有 1 行賦值，極可能是此陷阱
- 確認所有副作用都已實作

## 失敗時

→ patterns/stop-fighting, patterns/char-list-traversal
