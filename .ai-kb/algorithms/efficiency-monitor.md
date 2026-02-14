# Efficiency Monitor — 效率度量與自我調校

> 呼叫時機: 每次任務完成時記錄度量；達到階段門檻時觸發基線比對
> 輸入: 任務執行過程中的各項度量指標
> 輸出: 效率報告 + 不達標時的自我調校動作

## 度量指標

```
指標          | 說明                                        | 計算方式
──────────────|──────────────────────────────────────────────|─────────────
T_total       | 整體完成時間（指令→通過所有驗證）              | 結束時間 - 開始時間
T_learn       | AI 重新學習專案知識的時間                     | 首次 Read 原子到開始產出程式碼
N_build       | dotnet build 執行次數                        | 計數
N_error       | error-recovery 觸發次數                      | 計數
N_trap        | 事後才發現的陷阱數（VERIFY 階段才抓到的）      | 計數
N_token       | 消耗的 token 數（估算）                       | 輸入+輸出 token
```

## 演算法

### 度量收集

```
FUNCTION start_measurement(task)
  metrics = {
    task_name:  task.file,
    start_time: now(),
    N_build:    0,
    N_error:    0,
    N_trap:     0,
    N_token:    0
  }
  RETURN metrics

FUNCTION end_measurement(metrics)
  metrics.T_total = now() - metrics.start_time
  Write("workspace/reports/metrics-{task}-{date}.md", metrics)
END FUNCTION

# 各計數器在對應事件發生時遞增:
ON dotnet_build:  metrics.N_build += 1
ON error_recovery: metrics.N_error += 1
ON trap_in_verify: metrics.N_trap += 1
```

### 基線與基準比對

```
FUNCTION benchmark(current_metrics, baseline_path)

  baseline = Read(baseline_path)  # workspace/benchmarks/baseline-*.md

  comparison = {
    T_learn:  current.T_learn  vs baseline.T_learn,   # 目標: → 0
    N_build:  current.N_build  vs baseline.N_build,    # 目標: -50%
    N_error:  current.N_error  vs baseline.N_error,    # 目標: -60%
    N_trap:   current.N_trap   vs baseline.N_trap,     # 目標: → 0
    T_total:  current.T_total  vs baseline.T_total,    # 目標: ≤ 70%
    N_token:  current.N_token  vs baseline.N_token     # 容許: +20%
  }

  Write("workspace/reports/benchmark-{task}-{date}.md", comparison)

  IF NOT meets_targets(comparison):
    self_optimize(comparison)

END FUNCTION
```

### 目標值

```
T_learn  → 應降至 ~0（原子直接提供知識，不需重新學習）
N_build  → 應降低 50%+（批次策略 + 風險分類）
N_error  → 應降低 60%+（陷阱預先攔截）
N_trap   → 應降至 ~0（trap-detector 在移植階段就攔截）
T_total  → 目標: ≤ 基線的 70%（至少快 30%）
N_token  → 容許增加 20%（原子讀取 overhead），應被更少的迴圈抵消
```

### 自我調校（不達標時）

```
FUNCTION self_optimize(comparison)

  IF comparison.T_total > baseline.T_total * 0.9:
    # 系統反而變慢 → 診斷

    # 診斷 1: 原子讀取 overhead
    IF atom_read_ratio > 0.3:
      → 合併相關原子，減少檔案數
      → 更新 function-classifier 的原子映射

    # 診斷 2: 風險分類器準確度
    IF low_classified_as_high > 0.2:
      → 調寬 LOW 的門檻（提高 line_count 上限）
    IF high_classified_as_low_caused_error:
      → 調嚴 LOW 的門檻（降低 line_count 上限）

    # 診斷 3: Skill 觸發過度
    IF skill_creation_per_task > 1:
      → 提高 DETECT 門檻（3 次 → 5 次）

    # 套用調整
    update_algorithms(adjustments)

    # 重新測量
    log("SELF-OPTIMIZE: 已調整，下次任務將重新度量")

END FUNCTION
```

## 漸進式啟用

```
Phase A（立即啟用）:
  → INDEX + workflow + 原子
  → 最小 overhead，已能減少 T_learn 和 N_trap
  → 度量: T_learn, N_trap

Phase B（完成 2 個檔案後）:
  → 啟用風險分類器 (hallucination-guard)
  → 有 2 個檔案的經驗數據校準閾值
  → 度量: N_build（預期 -50%）

Phase C（完成 5 個檔案後）:
  → 啟用 Skill 閉環 (skill-orchestrator)
  → 有足夠操作簽名數據觸發 DETECT
  → 度量: 重複操作時間

Phase D（完成 10 個檔案後）:
  → 啟用 EVOLVE（Skill 自我進化）
  → 有足夠使用數據驅動進化
  → 度量: 全指標 vs 基線

每個 Phase 都測量效率，確認改善後才啟用下一 Phase。
```

## 連結原子

- algorithms/hallucination-guard.md — Phase B 啟用的風險分類器
- algorithms/skill-orchestrator.md — Phase C 啟用的 Skill 閉環
- algorithms/task-router.md — 度量從任務入口開始
- workspace/benchmarks/ — 基線與度量數據存放
- workspace/reports/ — 效率報告存放
