# Trap Detector — 自動陷阱偵測器

> 呼叫時機: PORT_FUNCTIONS 完成後，對整個 C# 檔案執行一次掃描
> 輸入: C# 原始碼檔案路徑
> 輸出: 偵測到的陷阱清單 + 自動修復或警告

## 演算法

```
FUNCTION detect_traps(cs_file: path) → List[TrapResult]

  source = Read(cs_file)
  results = []

  FOR EACH check IN CHECKS:
    matches = grep(source, check.pattern)
    IF matches:
      result = TrapResult(
        trap   = check.trap_id,
        atom   = check.atom_path,
        action = check.action,   # AUTO_FIX | WARN | BLOCK
        lines  = matches
      )
      results.append(result)

  RETURN results

END FUNCTION
```

## 20 項自動檢查清單

```
#  | 模式 (GREP/Regex)                         | 陷阱原子                    | 動作
---|--------------------------------------------|-----------------------------|--------
 1 | \[0\]\s*==\s*'\\0'                         | traps/P-null-term-crash     | AUTO_FIX → string.IsNullOrEmpty
 2 | string\.Format\(.*\{\d+,\d+\}              | traps/R-format-width-arg    | WARN → 檢查寬度參數對應
 3 | Console\.(Write|WriteLine)                 | traps/O-debug-output        | AUTO_FIX → 移除或改 log
 4 | (行數比: C# 行數 < C 行數 × 0.3)           | traps/H-logic-omitted       | BLOCK → 程式碼可能被省略
 5 | \(bool\)\s*\w+                             | traps/S-int-bool-narrow     | WARN → int→bool 窄化風險
 6 | \uFFFD|\\xEF\\xBF\\xBD                    | traps/A-encoding-corruption | BLOCK → 編碼損壞
 7 | //\s*TODO|//\s*STUB|throw.*NotImplemented  | traps/E-fake-completion     | WARN → 未完成的偽裝
 8 | (\w+)\s*=\s*\1\s*;                         | traps/J-duplicate-impl      | WARN → 自我賦值
 9 | case\s+\d+:(?!.*break|.*return|.*goto)     | traps/L-fallthrough-break   | AUTO_FIX → 補 break
10 | /\*.*\*/|//.*\bif\b.*\belse\b              | traps/M-commented-code      | WARN → 被註解的邏輯
11 | \bif\s*\(.*&&.*&&.*&&                      | traps/K-nested-if-flattened | WARN → 巢狀條件被壓平
12 | \bif\s*\(.*\|\|.*\|\|.*\|\|                | traps/N-extra-condition     | WARN → 額外條件檢查
13 | gsn_\w+\s*=\s*\d+                          | traps/Q-gsn-table-mixup     | WARN → gsn 硬編碼
14 | \b(MAX_\w+|NUM_\w+)\s*=\s*\d+              | traps/B-constant-mixup      | WARN → 常數值需對照 C 原始碼
15 | \b\d+\s*[+\-*/]\s*\d+\s*[+\-*/]\s*\d+     | traps/C-formula-simplified  | WARN → 複合運算可能被簡化
16 | "[\w\s]+(hit|dam|level|exp)"               | traps/D-chinese-to-english  | WARN → 中文被翻成英文
17 | \.\w+\s*=\s*\w+\(.*\)\s*;                  | traps/F-call-to-assign      | WARN → 函數呼叫→賦值轉換確認
18 | ~\s*\n\s*\n                                | traps/T-tilde-oneline       | WARN → tilde 後多餘換行
19 | (obj|ch|victim)\s*=\s*null;(?!.*free)      | traps/G-cleanup-truncated   | WARN → 清理流程可能被截斷
20 | send_to_char\(.*\+\s*"                     | traps/I-message-scope       | WARN → 訊息拼接範圍確認
```

## 動作處理流程

```
FOR EACH result IN detect_traps(cs_file):

  SWITCH result.action:

    CASE AUTO_FIX:
      apply_fix(result)          # 套用已知的自動修復
      log("AUTO-FIX", result)    # 記錄修復內容

    CASE WARN:
      Read(result.atom)          # 載入對應的陷阱原子
      log("WARNING", result)     # 輸出警告供後續判斷
      # 不自動修改，但標記需人工確認的行號

    CASE BLOCK:
      Read(result.atom)          # 載入原子了解問題
      HALT                       # 中斷流程
      → error-recovery.md        # 進入錯誤修復迴圈
```

## 掃描策略

```
# 整檔掃描一次（非逐函數），避免重複 I/O
# 結果依嚴重度排序：BLOCK > WARN > AUTO_FIX
# AUTO_FIX 套用後需重新 dotnet build 驗證
```

## 連結原子

- atoms/traps/A-encoding-corruption.md 至 atoms/traps/T-tilde-oneline.md（全部 20 個陷阱原子）
- algorithms/error-recovery.md — BLOCK 動作時進入修復迴圈
- atoms/verification/build-check.md — AUTO_FIX 後需重新編譯
