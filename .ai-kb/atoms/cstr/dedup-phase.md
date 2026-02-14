# CStr 去重階段

> 來源: CStr.cs 維護流程
> 信心度: VERIFIED
> 前置知識: atoms/cstr/why-centralize.md, atoms/cstr/naming-rules.md
> 相關原子: atoms/cstr/region-structure.md
> 觸發條件: CStr.cs 中出現重複的字串值；定期維護

## 知識
Phase 2 的 CStr 維護：找出跨 region 的重複字串，統一為共用常數。

### 為何會有重複
- 不同檔案移植時獨立提取，可能產生相同字串
- 例：`"你不能這麼做。\n"` 可能在 COMM、ACT_WIZ、FIGHT 都出現

### 重複偵測
```python
# 簡易 Python 掃描
from collections import Counter
import re

with open('CStr.cs', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有常數值
values = re.findall(r'= "(.*?)";', content)
dupes = {v: c for v, c in Counter(values).items() if c > 1}
for val, count in sorted(dupes.items(), key=lambda x: -x[1]):
    print(f"[{count}x] {val}")
```

### 去重流程
1. **識別**：找出值相同的常數
2. **選擇主常數**：若已有 M_USE 版本則用它，否則建立新的
3. **建立共用常數**：在 `#region Common Strings` 新增 `M_USE_NNN`
4. **更新引用**：所有 .cs 檔案中的舊常數名 → 新 M_USE 名
5. **刪除舊常數**：從各 region 移除被合併的常數

### 範例
```csharp
// 去重前
// #region COMM
public const string COMM_015 = "你不能這麼做。\n";
// #region FIGHT
public const string FIGHT_042 = "你不能這麼做。\n";

// 去重後
// #region Common Strings
public const string M_USE_023 = "你不能這麼做。\n";
// COMM_015 和 FIGHT_042 已刪除
// 所有引用處改為 CStr.M_USE_023
```

### 注意事項
- 去重後流水號會有空洞（如 COMM_015 被刪除）→ 可接受
- 大規模去重後可考慮重新編號（但風險較高）
- 優先去重出現 3 次以上的字串

## 行動
- 定期執行重複偵測掃描
- 高頻重複優先處理
- 更新所有引用處後再刪除舊常數

## 驗證
- `dotnet build` 編譯通過
- 搜尋被刪除的常數名，確認無殘留引用
- 再次執行重複偵測，確認已清除

## 失敗時
→ atoms/cstr/naming-rules.md（確認 M_USE 命名規則）
