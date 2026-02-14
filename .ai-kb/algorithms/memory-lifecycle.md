# Memory Lifecycle — 記憶生命週期管理

> 呼叫時機: 任務開始時初始化、任務進行中寫入、任務完成時執行 REFINE
> 輸入: 記憶項目（知識片段、修復記錄、驗證結果）
> 輸出: 記憶分類存放 + REFINE 後的升級/清理結果

## 四種記憶類型

```
類型           | 位置                        | 生命週期         | 用途
───────────────|─────────────────────────────|──────────────────|─────────────
PERMANENT      | .ai-kb/atoms/**/*.md        | 永久             | 核心知識原子
SESSION        | .ai-kb/workspace/session/   | 當前會話         | 暫存/中間結果
STAGING        | .ai-kb/workspace/staging/   | 待評估           | 新發現待精煉
REPORT         | .ai-kb/workspace/reports/   | 保留最近 5 份    | 驗證報告
```

## 演算法

### 寫入規則

```
FUNCTION memory_write(item: MemoryItem)

  SWITCH item.type:

    CASE "checkpoint":
      → workspace/session/checkpoint-{STATE}-{timestamp}.md

    CASE "decoded_text":
      → workspace/session/decoded-{FILENAME}-{line_range}.txt

    CASE "diff_compare":
      → workspace/session/diff-{FUNCTION_NAME}.md

    CASE "new_trap":
      → workspace/staging/new-trap-{description}.md

    CASE "new_pattern":
      → workspace/staging/new-pattern-{description}.md

    CASE "correction":
      → workspace/staging/correction-{atom_name}.md

    CASE "verify_report":
      → workspace/reports/{FILENAME}-{date}-verify.md

    CASE "build_report":
      → workspace/reports/{FILENAME}-{date}-build.md

END FUNCTION
```

### REFINE 流程（staging → atoms 的升級路徑）

```
FUNCTION refine()
  # 觸發時機: 每次任務的 COMPLETE 狀態

  staging_files = list("workspace/staging/*")

  FOR EACH file IN staging_files:

    content = Read(file)

    # ── 評估四種結局 ──

    IF is_duplicate(content, existing_atoms):
      # 已有原子覆蓋此知識
      DELETE file
      log("REFINE: 刪除重複 — {file.name}")

    ELSE IF is_too_narrow(content):
      # 只適用於單一函數/檔案，不具通用性
      DELETE file
      log("REFINE: 刪除過窄 — {file.name}")

    ELSE IF is_uncertain(content):
      # 有價值但需更多觀察
      mark_as_observed(file)
      increment_observation_count(file)
      IF observation_count(file) >= 3:
        promote_to_atom(file)   # 累積 3 次同類觀察 → 升級
      log("REFINE: 保留觀察中 — {file.name} ({count}/3)")

    ELSE:
      # 確定有價值 → 升級為永久原子
      promote_to_atom(file)
      DELETE file
      log("REFINE: 升級為原子 — {file.name}")

  # ── 清理 ──
  clear_directory("workspace/session/")
  trim_reports("workspace/reports/", keep=5)

  # ── 產出報告 ──
  Write("workspace/session/staging-report.md", refine_log)

END FUNCTION
```

### 報告保留策略

```
FUNCTION trim_reports(dir, keep)
  reports = list(dir, sort_by="date", order="desc")
  IF len(reports) > keep:
    FOR EACH old IN reports[keep:]:
      DELETE old
END FUNCTION
```

## 升級條件判斷

```
is_duplicate(content):
  → 用關鍵概念搜尋 atoms/ 目錄
  → 若找到 >80% 概念重疊的原子 → 重複

is_too_narrow(content):
  → 只提到單一檔案名/函數名 且 無法泛化
  → 例："MAGIC.C 第 42 行的特殊處理" → 過窄

is_uncertain(content):
  → 來自單次觀察，尚無重複佐證
  → 標記 OBSERVED，等待更多資料
```

## 連結原子

- atoms/ 全部目錄 — PERMANENT 記憶的存放位置
- algorithms/error-recovery.md — 未解問題寫入 STAGING
- algorithms/skill-orchestrator.md — COMPLETE 時同步執行 DETECT
- algorithms/hallucination-guard.md — CRITICAL 驗證結果寫入 SESSION
