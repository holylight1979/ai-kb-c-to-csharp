# CStr 編碼損壞修復工作流程 (fix-corruption)

> 偵測並修復 Big5→UTF-8 轉換過程中產生的亂碼字元

## 狀態機總覽

```
DETECT → LOCATE → DECODE → MATCH → REPLACE → VERIFY → COMPLETE
```

## 背景知識

Big5/CP950 編碼在轉換為 UTF-8 時，以下情況會產生損壞:
- 使用 `big5` 而非 `cp950` 解碼 → `\xF9xx` 範圍變成 U+FFFD
- 雙位元組切割錯誤 → 半個中文字變成亂碼
- 未處理 0x7E 作為 Big5 第二位元組 → 被誤判為 ASCII tilde

損壞表現:
- `U+FFFD` (�) — 替換字元，表示解碼失敗
- `U+E000-F8FF` (PUA) — 私用區字元，表示錯誤映射

---

## STATE: DETECT — 偵測損壞

使用 encoding-scan 掃描目標檔案:

```bash
python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src
```

**判定標準**:
- FFFD 數量 > 0 → 確認損壞
- PUA 數量 > 0 → 疑似損壞（需進一步確認）
- 兩者皆為 0 → 無損壞，流程結束

**產出**: 損壞檔案清單 + 各檔案的 FFFD/PUA 數量
**退出條件**: 偵測到損壞 → 進入 LOCATE

---

## STATE: LOCATE — 定位損壞字串

對每個損壞檔案，找出損壞字元的精確位置:

1. 逐行掃描，找出包含 U+FFFD 或 PUA 字元的行
2. 記錄行號、損壞字元位置、周圍上下文
3. 判斷損壞字元屬於哪個字串常數（若在 CStr.cs 中）

**輸出格式**:
```
CStr.cs:L1247  ACTOBJ_042 = "你把�丟在地上"  [FFFD at pos 6]
CStr.cs:L1305  FIGHT_018 = "你的攻擊打中了"  [PUA U+E001 at pos 8]
```

**產出**: 損壞字串清單（含行號、常數名、損壞位置）
**退出條件**: 所有損壞位置已定位 → 進入 DECODE

---

## STATE: DECODE — 從 C 原始碼解碼正確文字

使用 `big5_extract.py` 或 `verify.py decode-big5` 從原始 C 檔案取得正確文字:

```bash
# 方法 1: 使用 big5_extract 提取所有字串
python -X utf8 .claude/tools/big5_extract.py SRC/XXX.C

# 方法 2: 使用 decode-big5 查看指定行範圍
python -X utf8 verify.py decode-big5 SRC/XXX.C 1510 1545
```

對每個損壞字串，在原始 C 檔案中找到對應的正確文字。

**匹配策略**:
- 使用損壞字串的非損壞部分作為搜尋關鍵字
- 比對行號（若 C 與 C# 行號相近）
- 比對上下文（函數名稱、周圍程式碼）

**產出**: 損壞字串 → 正確字串的對應表
**退出條件**: 所有損壞字串都找到正確版本 → 進入 MATCH

---

## STATE: MATCH — 反向模擬損壞以確認

驗證損壞機制，確保修復正確:

1. 取得正確中文字串
2. 編碼為 cp950 位元組
3. 嘗試以 `big5`（非 cp950）解碼，確認會產生相同的 FFFD
4. 確認以 `cp950` 解碼可得到正確結果

```python
# 反向驗證範例
correct_text = "裏"           # 正確文字
cp950_bytes = correct_text.encode('cp950')  # b'\xF9\xD8'
big5_result = cp950_bytes.decode('big5', errors='replace')  # '�' (U+FFFD)
cp950_result = cp950_bytes.decode('cp950')  # '裏' (正確)
```

若反向模擬結果與實際損壞不符，標記為需人工審查。

**產出**: 驗證過的修復對應表
**退出條件**: 所有修復已驗證 → 進入 REPLACE

---

## STATE: REPLACE — 執行修復

根據損壞位置執行字串替換:

### CStr.cs 中的修復

直接替換損壞的常數值:
```csharp
// 修復前
public const string ACTOBJ_042 = "你把�丟在地上";
// 修復後
public const string ACTOBJ_042 = "你把裏丟在地上";
```

### 原始 .cs 檔案中的修復

若損壞在尚未 CStr 化的硬編碼字串中，直接替換:
```csharp
// 修復前
SendToChar("你把�丟在地上\n\r", ch);
// 修復後
SendToChar("你把裏丟在地上\n\r", ch);
```

**重要**: 每次修復後立即執行 `dotnet build` 確認編譯通過。

**產出**: 已修復的檔案
**退出條件**: 所有修復已套用 → 進入 VERIFY

---

## STATE: VERIFY — 驗證修復結果

重新執行完整編碼掃描:

```bash
python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src
```

**成功標準**: FFFD = 0, PUA = 0（針對修復的檔案）

若仍有殘留損壞:
- 回到 LOCATE 重新定位
- 最多重試 3 次
- 超過則標記為需人工介入

**退出條件**: 零損壞 → 進入 COMPLETE

---

## STATE: COMPLETE — 修復完成

1. 記錄修復摘要（修復了哪些字串、行號、原因）
2. 建議: 未來使用 cp950 而非 big5 進行解碼
3. 回到呼叫者流程（port-new-file 或 verify-existing）

**最終產出**: 零損壞的檔案 + 修復記錄
