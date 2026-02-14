# Using Static Import Pattern

> 來源: 編譯錯誤分析, CS0103 修復經驗
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: visibility-upgrade, partial-class
> 觸發條件: CS0103 "The name 'XXX' does not exist in the current context"

## 知識
C# 的 `using static` 允許直接使用靜態類別的成員，不需前綴。
移植 C 程式碼時，常數和工具方法分散在多個靜態類別中。

常見需要匯入的類別：
```csharp
using static MudGM.Src.MercConstants;  // MAX_LEVEL, PULSE_TICK 等常數
using static MudGM.Src.MercTypes;      // 型別定義、列舉
using static MudGM.Src.CStr;           // 中文字串常數
using static MudGM.Src.Merc;           // 全域函式
using static MudGM.Src.DbModule;       // 資料庫函式
```

CS0103 錯誤判斷流程：
1. 找不到的名稱是常數？→ 加 `using static MercConstants;`
2. 找不到的名稱是 CStr 開頭？→ 加 `using static CStr;`
3. 找不到的名稱是型別？→ 加 `using static MercTypes;`
4. 找不到的名稱是全域函式？→ 用 Grep 搜尋定義位置

注意事項：
- 多個類別定義同名成員時會產生歧義（CS0104）
- 此時需使用完整前綴 `MercConstants.MAX_LEVEL`
- partial class 的每個檔案都需要各自的 using static

## 行動
1. 確認 CS0103 報錯的名稱
2. 使用 Grep 搜尋該名稱的定義位置
3. 在檔案頂部加入對應的 `using static` 宣告
4. 重新編譯確認

## 驗證
```bash
dotnet build {CSPROJ_PATH}
```
CS0103 錯誤應消失。若出現 CS0104 歧義，改用完整前綴。

## 失敗時
→ build-check (重新編譯)
→ visibility-upgrade (若改為 CS0122)
→ grep-existing (搜尋定義位置)
