# Fallthrough Break (switch fall-through 被加上 break)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-L
> 信心度: VERIFIED
> 前置知識: C switch fall-through 語義
> 相關原子: syntax/switch-fallthrough, patterns/case-groups
> 觸發條件: C 中刻意省略 break 的 case 在 C# 被加上 break

## 知識

C 語言的 switch 語句中，若 case 末尾沒有 break，執行會「落入」
(fall through) 下一個 case。這在 MUD 程式碼中是常見的刻意用法。
C# 不允許隱式 fall-through，必須用 `goto case` 明確表示。

**典型案例：**

C 原始碼（刻意 fall-through）：
```c
switch (ch->position)
{
    case POS_DEAD:
        send_to_char("你已經死了！\n", ch);
        /* break; */          // 注意：break 被註解掉了！
    case POS_MORTAL:
    case POS_INCAP:
        send_to_char("你受了致命傷。\n", ch);
        break;
    case POS_STUNNED:
        send_to_char("你失去了意識。\n", ch);
        break;
}
```

錯誤移植（加上 break）：
```csharp
switch (ch.Position)
{
    case POS_DEAD:
        ch.SendToChar("你已經死了！\n");
        break;  // 錯誤：不會再落入 POS_MORTAL
    case POS_MORTAL:
    case POS_INCAP:
        ch.SendToChar("你受了致命傷。\n");
        break;
}
```

正確移植（用 goto case）：
```csharp
switch (ch.Position)
{
    case POS_DEAD:
        ch.SendToChar("你已經死了！\n");
        goto case POS_MORTAL;  // 明確的 fall-through
    case POS_MORTAL:
    case POS_INCAP:
        ch.SendToChar("你受了致命傷。\n");
        break;
}
```

**偵測關鍵：**
- 在 C 中搜尋 `/* break; */` 或 `// break;`（被註解掉的 break）
- 搜尋 case 末尾沒有 break、return、continue 的情況
- 空 case（無程式碼直接落入下一個）在 C# 中是合法的，不需處理

## 行動

1. 列出 C 中所有 switch 語句
2. 檢查每個 case 的 break 狀態
3. 特別注意被 `/* */` 註解掉的 break
4. 在 C# 中用 `goto case` 保持 fall-through 語義

## 驗證

- 逐一比對每個 case 的 break 狀態（C vs C#）
- 確認所有刻意的 fall-through 都用 `goto case` 實作
- 測試 fall-through 路徑的行為正確

## 失敗時

→ syntax/switch-fallthrough, patterns/case-groups
