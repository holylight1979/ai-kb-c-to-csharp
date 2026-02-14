# Fake Completion (假完成 — 方法只有 TODO/stub)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-E
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: verification/stub-scan
> 觸發條件: 方法簽名完整但方法體為空或僅含 TODO 註解

## 知識

移植過程中，某些方法可能只建立了簽名和框架，但內部實作完全缺失。
這些方法看起來「已完成」，因為它們能通過編譯，但實際上什麼都不做。

**典型模式：**

```csharp
// 看起來已完成 — 有簽名、有參數、能編譯
public void UpdateHandler()
{
    // TODO: implement
}

// 更隱蔽的變體 — 有部分框架
public void SaveCharObj(CharData ch, string filename)
{
    // TODO: save character
    return;
}

// 最危險的變體 — 有不完整的實作
public void Interpret(CharData ch, string argument)
{
    if (string.IsNullOrEmpty(argument))
        return;
    // TODO: command lookup and execution
}
```

**已知的 CRITICAL stub（來自審計）：**
- `Interpret` — 命令解析核心
- `UpdateHandler` — 遊戲主循環更新
- `LoadCharObj` — 角色載入
- `SaveCharObj` — 角色儲存
- `Crypt` — 密碼加密
- `BootDb` 委派函式

**為什麼危險：**
- 編譯器不會報錯（語法正確）
- 單元測試可能不覆蓋（若測試也是 stub）
- 執行時靜默失敗（不丟例外，只是不做事）

## 行動

1. 執行 stub-scan 掃描所有方法體
2. 搜尋 `// TODO`、`throw new NotImplementedException()`
3. 比對 C 原始碼確認預期實作長度
4. 逐一實作所有 stub 方法

```bash
grep -rn "// TODO" {CSHARP_DIR}/MudGM/Src/
grep -rn "NotImplementedException" {CSHARP_DIR}/MudGM/Src/
```

## 驗證

- stub-scan 回報 0 個未實作方法
- 所有方法體行數 > 3（排除單純的 getter/setter）
- 關鍵方法（Interpret, UpdateHandler 等）有完整邏輯

## 失敗時

→ verification/stub-scan
