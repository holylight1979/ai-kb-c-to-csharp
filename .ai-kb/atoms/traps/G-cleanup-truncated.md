# Cleanup Truncated (清理路徑只完成一半)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-G
> 信心度: VERIFIED
> 前置知識: C 資源清理模式
> 相關原子: patterns/extract-char, patterns/resource-cleanup
> 觸發條件: C 清理函式有 N 步驟，C# 只實作了部分

## 知識

C MUD 中的資源清理函式（如 extract_char、extract_obj）通常包含
多個步驟，每個步驟清理不同的關聯資源。移植時很容易只做前幾步
就認為「完成了」，遺漏後面的步驟。

**典型案例：extract_char（8 步 → 4 步）**

C 原始碼的完整清理步驟：
```c
void extract_char(CHAR_DATA *ch, bool fPull)
{
    // 步驟 1: 停止戰鬥
    if (ch->fighting != NULL)
        stop_fighting(ch, TRUE);

    // 步驟 2: 移除所有影響
    while (ch->affected)
        affect_remove(ch, ch->affected);

    // 步驟 3: 移除所有攜帶物品
    while (ch->carrying)
        extract_obj(ch->carrying);

    // 步驟 4: 從房間移除
    char_from_room(ch);

    // 步驟 5: 清除追蹤目標（常被遺漏！）
    die_follower(ch);

    // 步驟 6: 清除其他角色對此角色的引用
    // 走訪 char_list 清除 reply, retell 等指標

    // 步驟 7: 從全域 char_list 移除
    // 步驟 8: 釋放記憶體 / 加入回收池
}
```

C# 不完整移植（只做了 4 步）：
```csharp
public void ExtractChar(CharData ch, bool fPull)
{
    StopFighting(ch, true);
    // 移除影響和物品...
    CharFromRoom(ch);
    // 步驟 5-8 完全缺失！
}
```

**為什麼危險：**
- 記憶體洩漏（C# 有 GC 但引用未清會阻止回收）
- 懸空引用（其他角色的 reply 指向已移除角色）
- 追隨者系統錯亂

## 行動

1. 在 C 原始碼中逐行計數清理步驟
2. 在 C# 中逐行比對，標記每個步驟
3. 補齊所有遺漏的步驟
4. 特別注意「走訪全域串列清除引用」類步驟

## 驗證

- 逐行比對 C 與 C# 的清理步驟數量
- 確認每個步驟都有對應實作
- 測試角色離線後不會有懸空引用

## 失敗時

→ patterns/extract-char, patterns/resource-cleanup
