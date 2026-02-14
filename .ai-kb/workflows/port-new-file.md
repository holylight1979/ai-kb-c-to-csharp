# 移植新檔案工作流程 (port-new-file)

> 將 C 原始碼（Big5）移植為 C#（UTF-8）的完整狀態機流程

## 狀態機總覽

```
INIT → SKELETON → PORT_FUNCTIONS → CSTR → VERIFY → COMPLETE
                                              ↓
                                       ERROR_RECOVERY (最多 3 次)
                                              ↓
                                         re-VERIFY
```

---

## STATE: INIT — 初始化與解碼驗證

**進入條件**: 收到移植新 C 檔案的指令

1. 使用 `big5_extract.py` 讀取原始 C 檔案，確認 cp950 解碼正常
2. 檢查輸出中是否有 U+FFFD（替換字元），若有則進入 fix-corruption 流程
3. 統計中文字串總數，作為後續 CSTR 階段的基準
4. 確認 C 檔案的函數清單（`grep` 搜尋函數定義）

**產出**: 原始字串清單、函數清單、解碼品質報告
**退出條件**: 零 FFFD → 進入 SKELETON

---

## STATE: SKELETON — 建立 C# 骨架

1. 在 `{CSHARP_DIR}/MudGM/Src/` 建立 `FILENAME.C.cs`
2. 定義 partial class 與命名空間結構
3. 列出所有待移植函數，進行風險分級
4. 確認 `FILE_TO_PREFIX` 映射已新增到 `cstr_add_missing.py` 和 `cstr_replacer.py`
5. 在 CStr.cs 建立對應的 `#region` / `#endregion` 區段

### 風險分級標準

| 等級 | 條件 | 策略 |
|------|------|------|
| **LOW** | 簡單委派/轉發、<20 行、無特殊模式 | 批次 5-10 個函數，1 次 build |
| **MEDIUM** | <50 行、無 printf/switch/中文 | 逐一移植，2-3 個一組 build |
| **HIGH** | >50 行、含 printf/switch/中文字串 | 單獨移植，每個都 build |
| **CRITICAL** | fread_string、新模式、INFERRED >10 行 | 單獨移植 + 逐行比對 + build |

**退出條件**: 骨架已建立 + 函數已分級 → 進入 PORT_FUNCTIONS

---

## STATE: PORT_FUNCTIONS — 逐批移植函數

### 移植順序: LOW → MEDIUM → HIGH → CRITICAL

**LOW 批次流程**:
1. 一次移植 5-10 個 LOW 函數
2. 執行 `dotnet build {CSPROJ_PATH}`
3. 修復編譯錯誤（若有）

**MEDIUM 批次流程**:
1. 一次移植 2-3 個 MEDIUM 函數
2. Build + 修復

**HIGH/CRITICAL 逐一流程**:
1. 逐行比對 C 原始碼與 C# 翻譯
2. 特別注意: 指標算術、format string、Big5 字串、switch fallthrough
3. 每個函數完成後立即 build

### 陷阱偵測掃描 (trap-detector)

每批次完成後，檢查以下陷阱:
- `sprintf` / `printf` → 是否正確轉為 `string.Format` 或插值字串
- `switch` → 是否有 fallthrough（C# 不允許隱式 fallthrough）
- `goto` → 是否需要重構為迴圈或方法呼叫
- `str_cmp` / `str_prefix` → 是否使用正確的 C# 比較方法
- 指標運算 → 是否轉為陣列索引或 ref 參數

**退出條件**: 所有函數已移植 + build 成功 → 進入 CSTR

---

## STATE: CSTR — 字串集中化

依序執行四步驟:

```bash
# 1. 確認原始字串覆蓋
python -X utf8 .claude/tools/big5_extract.py SRC/XXX.C --verify

# 2. 新增缺少的 CStr 常數
python -X utf8 .claude/tools/cstr_add_missing.py

# 3. 替換硬編碼字串
python -X utf8 .claude/tools/cstr_replacer.py --apply XXX.C.cs

# 4. 編譯驗證
dotnet build {CSPROJ_PATH}
```

若步驟 3 的 `--analyze` 顯示 MISSING > 0，重複步驟 2-3。

**退出條件**: MISSING=0 + build 成功 → 進入 VERIFY

---

## STATE: VERIFY — 最終驗證

依序執行驗證命令:

```bash
# 1. 編碼掃描 — 必須零 FFFD/PUA
python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src/XXX.C.cs

# 2. 字串比對 — 確認 C 與 C# 字串一致
python -X utf8 verify.py compare-strings SRC/XXX.C {CSHARP_DIR}/MudGM/Src/XXX.C.cs

# 3. Stub 掃描 — 列出殘留 TODO/stub
python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src/XXX.C.cs
```

**退出條件**:
- 零 FFFD/PUA → 零嚴重 stub → 字串覆蓋率 >95% → 進入 COMPLETE
- 任何失敗 → 進入 ERROR_RECOVERY

---

## STATE: ERROR_RECOVERY — 錯誤修復（最多 3 次）

1. **分類錯誤**: FATAL（編碼損壞）、CRITICAL（邏輯錯誤）、MEDIUM（缺少字串）、LOW（格式問題）
2. **載入修復原子**: 根據錯誤類型選擇修復策略
   - FATAL → 進入 fix-corruption 子流程
   - CRITICAL → 回到 PORT_FUNCTIONS 重新移植該函數
   - MEDIUM → 回到 CSTR 重新處理字串
   - LOW → 就地修復
3. **執行修復**
4. **重新驗證** → 回到 VERIFY

**最大重試**: 3 次。超過則標記為需要人工介入。

---

## STATE: COMPLETE — 完成收尾

1. 更新 `src-cs/TODO.md`，標記該檔案為已完成
2. REFINE staging: 確認所有相關檔案已準備好 commit
3. DETECT skills: 如果移植過程中發現新模式，考慮建立新 skill
4. 清理工作階段暫存

**最終產出**: 可編譯的 .cs 檔案 + 零亂碼 + 完整 CStr 覆蓋 + 更新的 TODO.md
