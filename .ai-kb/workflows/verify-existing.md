# 驗證已移植檔案工作流程 (verify-existing)

> 對已完成移植的 .cs 檔案進行全面品質驗證的狀態機流程

## 狀態機總覽

```
SCAN → COMPARE → TRAP_CHECK → REPORT → ISSUES → FIX → COMPLETE
                                          ↓
                                    (無問題則直接)
                                          ↓
                                       COMPLETE
```

---

## STATE: SCAN — 基礎掃描

**進入條件**: 指定要驗證的 .cs 檔案（或批次驗證所有已移植檔案）

### 1. 編碼掃描 (encoding-scan)

```bash
python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src/TARGET.C.cs
```

檢查項目:
- U+FFFD (替換字元) — 表示 Big5→UTF-8 轉換失敗
- PUA 字元 (U+E000-F8FF) — 表示使用了私用區字元
- 非預期的控制字元

### 2. Stub 掃描 (stub-scan)

```bash
python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src/TARGET.C.cs
```

檢查項目:
- `TODO` 標記
- `FIXME` 標記
- `NotImplementedException`
- `// stub` 註解
- 空方法體（只有 `{ }` 或 `{ return; }`）

**產出**: encoding-scan 結果 + stub-scan 結果
**退出條件**: 掃描完成 → 進入 COMPARE

---

## STATE: COMPARE — 字串與常數比對

### 1. 字串比對 (compare-strings)

```bash
python -X utf8 verify.py compare-strings SRC/TARGET.C {CSHARP_DIR}/MudGM/Src/TARGET.C.cs
```

- 提取 C 原始碼（Big5）中所有中文字串
- 提取 C# 檔案（UTF-8）中所有中文字串（含 CStr 引用）
- 並排比較，標記遺漏或不一致

### 2. 常數比對 (compare-constants)（視情況）

僅對包含常數定義的檔案（如 MercConstants.cs、CONST.C.cs）:

```bash
python -X utf8 verify.py -v compare-constants SRC/MERC.H {CSHARP_DIR}/MudGM/Src/MercConstants.cs
```

- 提取 C 的 `#define` 數值常數
- 提取 C# 的 `const` 定義
- 逐一比對名稱和數值

**產出**: 字串差異報告 + 常數差異報告
**退出條件**: 比對完成 → 進入 TRAP_CHECK

---

## STATE: TRAP_CHECK — 陷阱偵測

對目標檔案進行常見移植陷阱掃描:

### 檢查清單

| 陷阱 | 搜尋模式 | 嚴重度 |
|------|----------|--------|
| 未轉換的 sprintf | `sprintf` 字面出現 | CRITICAL |
| switch fallthrough | `case.*:` 後無 `break`/`return`/`goto` | HIGH |
| 空指標解引用 | `.Name` / `.ShortDescr` 無 null 檢查 | MEDIUM |
| Big5 tilde 問題 | fread_string 中 `0x7E` 保護 | CRITICAL |
| str_cmp 殘留 | `str_cmp` / `str_prefix` 字面出現 | HIGH |
| 硬編碼中文 | 非 CStr 引用的中文字串 | MEDIUM |
| 未處理的 goto | `goto` 語句 | MEDIUM |
| 型別不匹配 | `sh_int` vs `short`, `char*` vs `string` | LOW |

### 執行方式

使用 grep 搜尋各陷阱模式，記錄行號與上下文。

**產出**: 陷阱偵測報告
**退出條件**: 掃描完成 → 進入 REPORT

---

## STATE: REPORT — 生成報告

彙整 SCAN、COMPARE、TRAP_CHECK 的結果，生成結構化報告:

```
=== 驗證報告: TARGET.C.cs ===
日期: YYYY-MM-DD
狀態: PASS / FAIL

[編碼掃描]
  FFFD: 0, PUA: 0 → PASS

[Stub 掃描]
  TODO: 2, FIXME: 0, NotImplemented: 0

[字串比對]
  C 字串: 156, C# 字串: 154, 遺漏: 2

[陷阱偵測]
  CRITICAL: 0, HIGH: 1, MEDIUM: 3, LOW: 2

總結: 需修復 1 HIGH + 3 MEDIUM 問題
```

**退出條件**:
- 零問題 → 進入 COMPLETE
- 有問題 → 進入 ISSUES

---

## STATE: ISSUES — 問題分級

將所有發現的問題按嚴重度分級:

| 嚴重度 | 定義 | 處理方式 |
|--------|------|----------|
| **FATAL** | 編碼損壞、資料遺失 | 必須立即修復，進入 fix-corruption 流程 |
| **CRITICAL** | 邏輯錯誤、功能缺失 | 必須修復才能標記完成 |
| **MEDIUM** | 字串遺漏、格式問題 | 應修復，可延後 |
| **LOW** | 風格問題、非關鍵 TODO | 可接受，記錄即可 |

**退出條件**: 分級完成 → 進入 FIX（若有可自動修復的問題）或 COMPLETE（僅 LOW 問題）

---

## STATE: FIX — 自動修復

對可自動修復的問題執行修復:

- **硬編碼中文** → 執行 cstr_add_missing + cstr_replacer
- **缺少 null 檢查** → 手動或半自動新增
- **字串遺漏** → 補充到 CStr.cs
- **FATAL/CRITICAL** → 需人工介入或進入專用修復流程

修復後重新執行 SCAN → COMPARE → TRAP_CHECK 驗證。

**退出條件**: 所有 FATAL/CRITICAL 已修復 → 進入 COMPLETE

---

## STATE: COMPLETE — 驗證完成

1. 記錄最終驗證狀態（PASS / PASS_WITH_WARNINGS）
2. 列出殘留的 LOW/MEDIUM 問題（若有）
3. 更新 TODO.md 中的驗證狀態

**最終產出**: 驗證報告 + 修復記錄 + 更新的 TODO.md
