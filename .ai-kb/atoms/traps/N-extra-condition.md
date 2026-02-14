# Extra Condition (無條件程式碼被包在額外的 if 中)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-N
> 信心度: VERIFIED
> 前置知識: C 控制流程
> 相關原子: syntax/c-brace-matching, verification/code-flow-trace
> 觸發條件: C 中無條件執行的程式碼在 C# 中被包在新的 if 條件內

## 知識

移植時，AI 或開發者可能「過度防禦」，為原本無條件的程式碼
新增不存在的條件檢查，改變了執行語義。

**典型案例：**

C 原始碼（無條件執行）：
```c
void do_quit(CHAR_DATA *ch, char *argument)
{
    // ... 前置檢查 ...

    // 無條件：所有玩家離線都要儲存
    save_char_obj(ch);
    extract_char(ch, TRUE);
    send_to_char("再見！\n", ch);
}
```

錯誤移植（加了額外條件）：
```csharp
public void DoQuit(CharData ch, string argument)
{
    // ... 前置檢查 ...

    // 錯誤：為什麼要檢查 IsNpc？C 原始碼沒有這個條件
    if (!ch.IsNpc())
    {
        SaveCharObj(ch);
    }
    ExtractChar(ch, true);
    ch.SendToChar("再見！\n");
}
```

**為什麼會發生：**
- 移植者認為「應該」要有保護條件
- AI 模型根據其他函式的模式推斷出條件
- 複製貼上其他函式的框架時帶入了不需要的條件
- 想要「改進」原始碼的防禦性

**常見的多餘條件：**
```csharp
if (!ch.IsNpc())        // C 原始碼沒有此檢查
if (ch.InRoom != null)  // C 假設永遠有效
if (victim != null)     // C 保證此處不為 null
if (ch.Level > 0)       // C 沒有此限制
```

**為什麼危險：**
- NPC 該存檔的沒存檔
- 特定狀態下的邏輯被跳過
- 行為與原始 C 不一致，產生難以追蹤的 Bug

## 行動

1. 比對 C 與 C# 的條件結構
2. 標記 C# 中多出的 if 條件
3. 確認每個條件在 C 中是否存在
4. 移除所有不在 C 中的額外條件

## 驗證

- 逐行追蹤 C 與 C# 的控制流程
- 確認兩者的條件分支結構完全一致
- 測試被額外條件保護的路徑是否正確執行

## 失敗時

→ syntax/c-brace-matching, verification/code-flow-trace
