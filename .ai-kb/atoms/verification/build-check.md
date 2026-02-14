# Build Check Verification

> 來源: 編譯驗證流程
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: using-static-import, visibility-upgrade, partial-class
> 觸發條件: 每次修改任何 .cs 檔案後

## 知識
編譯是最基本的驗證步驟。每次修改後必須執行。

常見編譯錯誤與對應的 atom：

| 錯誤碼 | 訊息 | 對應 atom |
|--------|------|-----------|
| CS0103 | name does not exist in current context | using-static-import |
| CS0122 | inaccessible due to protection level | visibility-upgrade |
| CS0101 | already contains a definition | partial-class |
| CS0029 | cannot implicitly convert type | (型別轉換) |
| CS0246 | type or namespace not found | (缺少 using) |
| CS0019 | operator cannot be applied | (運算子不支援) |
| CS1503 | argument type mismatch | (參數型別錯誤) |

編譯命令必須從 `{CSHARP_DIR}` 目錄執行：
```bash
cd {CSHARP_DIR}
dotnet build {CSPROJ_PATH}
```

Build 成功的輸出：
```
Build succeeded.
    0 Warning(s)
    0 Error(s)
```

Warning 也應關注，特別是：
- CS0168: variable declared but never used → 可能遺漏邏輯
- CS0219: variable assigned but never used → 同上
- CS8600/CS8602: null reference warnings → 潛在 runtime 錯誤

## 行動
```bash
cd {CSHARP_DIR}
dotnet build {CSPROJ_PATH}
```

若錯誤過多，可分批修正，每次修正後重新編譯。

## 驗證
Build succeeded，0 Error(s)。
理想狀態：0 Warning(s)。

## 失敗時
→ using-static-import (CS0103)
→ visibility-upgrade (CS0122)
→ partial-class (CS0101)
→ grep-existing (搜尋現有定義避免重複)
