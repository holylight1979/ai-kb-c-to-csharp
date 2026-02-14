# Skill Orchestrator — Skill 自我成長閉環

> 呼叫時機: 任務 COMPLETE 時執行 DETECT；Skill 使用 5+ 次後觸發 EVOLVE
> 輸入: 操作簽名記錄（workspace/session/）
> 輸出: 新建/更新的 Skill 檔案（.claude/skills/）+ registry 更新

## 演算法

```
LIFECYCLE:  DETECT → CREATE → TEST → CORRECT → DEPLOY → MONITOR → EVOLVE
            全程零人工介入
```

### DETECT — 偵測重複操作模式

```
FUNCTION detect()
  # 觸發時機: 每次任務 COMPLETE

  signatures = load_all_signatures("workspace/session/op-signatures.md")

  FOR EACH sig IN unique(signatures):
    count = count_occurrences(sig, across_all_sessions=true)

    IF count >= 3:
      # 同一操作簽名出現 3+ 次 → 觸發 CREATE
      CREATE(sig, count)

  # 簽名 = (工具序列, 參數模式, 觸發情境)
  # 模糊匹配: 只有具體參數不同的操作視為同一簽名
  # 例: "Read SRC/X.C → port → build" ≈ "Read SRC/Y.C → port → build"

END FUNCTION
```

### CREATE — 建立 Skill

```
FUNCTION create(sig, count)

  name = auto_name(sig)   # 從操作簽名推導名稱
  path = ".claude/skills/{name}/SKILL.md"

  Write(path, template={
    name:        name,
    description: describe(sig),
    source:      "自動偵測，基於 {count} 次重複操作",
    date:        today(),
    version:     "1.0",
    test_status: "UNTESTED",
    trigger:     derive_trigger(sig),
    steps:       extract_steps(sig),
    corrections: []
  })

  → 進入 TEST

END FUNCTION
```

### TEST — 自我測試

```
FUNCTION test(skill) → PASS | FAIL

  # 用已完成的已知正確任務作為測試案例
  test_case = find_recent_completed_task(skill.signature)

  IF test_case IS NULL:
    RETURN FAIL   # 無可用測試案例

  # 執行 Skill
  actual_output = execute_skill(skill, test_case.input)

  # 比對結果
  checks = [
    dotnet_build_passes(actual_output),
    output_matches_expected(actual_output, test_case.expected),
    verify_tools_agree(actual_output)
  ]

  IF all(checks):
    RETURN PASS
  ELSE:
    RETURN FAIL

END FUNCTION
```

### CORRECT — 自我修正（最多 3 輪）

```
FUNCTION correct(skill, failure_info)

  FOR round = 1 TO 3:

    # 分析失敗原因
    cause = analyze_failure(failure_info)

    # 載入相關原子
    atoms = load_atoms_for_error(cause)

    # 修改 Skill 步驟
    update_skill_steps(skill, cause, atoms)

    # 追加修正記錄
    append_correction(skill, {
      version:  "1.{round}",
      problem:  failure_info.description,
      cause:    cause,
      fix:      describe_fix()
    })

    # 重新測試
    IF test(skill) == PASS:
      RETURN SUCCESS

    failure_info = get_new_failure()

  # 3 輪仍失敗
  skill.test_status = "FAILED"
  move_to("workspace/staging/failed-skill-{skill.name}.md")
  RETURN FAILED

END FUNCTION
```

### DEPLOY — 註冊啟用

```
FUNCTION deploy(skill)
  skill.test_status = "TESTED"
  update_file(skill.path)
  append_to_registry(".ai-kb/skills/registry.md", skill)
  # Skill 立即生效 — Claude Code 自動發現 .claude/skills/
END FUNCTION
```

### MONITOR — 使用追蹤

```
ON skill_invoked(skill):
  log_to("workspace/session/skill-usage-{skill.name}.md", {
    date:    today(),
    task:    current_task,
    result:  success | failure,
    details: brief_summary
  })
```

### EVOLVE — 自我進化

```
FUNCTION evolve(skill)
  # 觸發: 使用 5+ 次後自動評估

  usage = load_usage_log(skill.name)
  success_rate = usage.successes / usage.total

  IF success_rate < 0.8:
    → 重新進入 CORRECT（用最近失敗案例）

  IF has_new_param_patterns(usage):
    → 擴展 Skill 的參數化範圍

  IF exists_similar_skill(skill):
    → 合併為更通用的 Skill

  skill.version = increment(skill.version)
  → 重新 TEST

END FUNCTION
```

## 連結原子

- .claude/skills/ — Skill 實際存放位置
- .ai-kb/skills/registry.md — Skill 清冊
- .ai-kb/skills/creation-guide.md — Skill 格式規範
- algorithms/memory-lifecycle.md — 失敗 Skill 進入 staging
- algorithms/error-recovery.md — CORRECT 階段的錯誤分析共用邏輯
