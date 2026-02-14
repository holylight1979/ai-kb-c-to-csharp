# Error Recovery — 錯誤修復迴圈

> 呼叫時機: 任何驗證步驟回報錯誤時（build 失敗、encoding 異常、trap 攔截）
> 輸入: 錯誤訊息 + 觸發來源狀態
> 輸出: 修復後的程式碼 + 修復記錄檔 | 或未解決問題寫入 staging

## 演算法

```
FUNCTION error_recovery(error: ErrorInfo, source_state: string) → RecoveryResult

  MAX_ROUNDS = 3

  FOR round = 1 TO MAX_ROUNDS:

    # ── 步驟 1：分類錯誤 ──
    category = classify_error(error)

    # ── 步驟 2：根據類別載入原子 ──
    atoms = load_atoms_for(category)

    # ── 步驟 3：執行修復 ──
    fix = apply_fix(category, error, atoms)

    # ── 步驟 4：記錄修復過程 ──
    Write("workspace/session/fix-round{round}.md", {
      round:    round,
      category: category,
      error:    error.message,
      fix:      fix.description,
      atoms:    atoms,
      result:   "PENDING"
    })

    # ── 步驟 5：重新驗證 ──
    verify_result = re_verify(source_state)

    IF verify_result.passed:
      update_fix_log(round, "RESOLVED")
      RETURN RecoveryResult(success=true, rounds=round)

    # ── 步驟 6：仍有錯誤 → 更新 error 進入下一輪 ──
    error = verify_result.new_error
    update_fix_log(round, "STILL_FAILING")

  END FOR

  # ── 3 輪未解決 ──
  Write("workspace/staging/unresolved-{describe(error)}.md", {
    original_error: error,
    attempts: 3,
    fix_logs: ["fix-round1.md", "fix-round2.md", "fix-round3.md"],
    suggestion: "需要人工介入或不同策略"
  })

  RETURN RecoveryResult(success=false, rounds=3, staging_path=path)

END FUNCTION
```

## 錯誤分類器

```
FUNCTION classify_error(error) → Category

  msg = error.message

  IF contains(msg, ["FFFD", "亂碼", "cp950", "encoding", "Encoding"])
    RETURN ENCODING

  IF contains(msg, ["CS0", "error CS", "build failed", "dotnet build"])
    RETURN BUILD

  IF contains(msg, ["line count", "行數比", "ratio", "omitted"])
    RETURN LOGIC

  IF contains(msg, ["trap:", "陷阱", "BLOCK"])
    RETURN TRAP

  RETURN UNKNOWN

END FUNCTION
```

## 分類 → 原子映射

```
ENCODING:
  → atoms/encoding/corruption-model.md    # 損壞模型
  → atoms/encoding/fffd-detection.md      # 偵測方法
  → atoms/encoding/cp950-vs-big5.md       # 解碼器選擇

BUILD:
  → atoms/syntax/null-terminator.md       # 常見編譯錯誤來源
  → atoms/syntax/int-to-bool.md           # 型別轉換問題
  → atoms/verification/build-check.md     # 編譯診斷流程

LOGIC:
  → atoms/traps/H-logic-omitted.md        # 邏輯被省略
  → atoms/traps/C-formula-simplified.md   # 公式被簡化
  → atoms/verification/line-count-check.md # 行數比對

TRAP:
  → (由 trap-detector 提供的具體陷阱原子)

UNKNOWN:
  → atoms/verification/build-check.md     # 通用診斷
  → 寫入 workspace/staging/ 待分析
```

## 修復策略

```
ENCODING → 重新用 cp950 解碼來源、修正損壞字串
BUILD    → 讀取編譯錯誤行號、載入相關語法原子、修正程式碼
LOGIC    → 重新 Read C 原始碼、比對遺漏的邏輯、補回缺失段落
TRAP     → 依陷阱原子的「行動」區段執行修復
UNKNOWN  → 嘗試通用修復，失敗則提交 staging
```

## 連結原子

- atoms/encoding/* — ENCODING 類錯誤的修復知識
- atoms/syntax/* — BUILD 類錯誤的語法知識
- atoms/traps/* — TRAP 類錯誤的陷阱知識
- atoms/verification/build-check.md — 重新驗證
- algorithms/hallucination-guard.md — error-recovery 第 2 輪未解 → 升級為 CRITICAL 風險
- algorithms/memory-lifecycle.md — 未解問題寫入 staging
