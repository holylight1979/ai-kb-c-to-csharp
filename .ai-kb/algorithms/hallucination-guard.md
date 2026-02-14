# Hallucination Guard — 反幻覺守衛

> 呼叫時機: 每次產出 C# 程式碼之前和之後
> 輸入: 修改動作描述 + 函數特徵標籤 + 當前 error-recovery 狀態
> 輸出: 風險等級 + 對應的驗證深度指令

## 演算法

```
FUNCTION hallucination_guard(action: Action) → VerifyPlan

  # ══ 硬性前置條件（零成本，純邏輯檢查） ══

  BEFORE_WRITE:
    IF NOT has_read_c_source(action.target_function):
      HALT → "必須先 Read 對應的 C 原始碼"
      # 這不是驗證，是前置條件 — 零例外

  # ══ 風險分類器 ══

  risk = risk_classify(action)

  # ══ 比例驗證 ══

  RETURN verify_plan_for(risk)

END FUNCTION
```

## 風險分類器

```
FUNCTION risk_classify(action) → RISK_LEVEL

  # ── CRITICAL（全套 + 留痕）──
  IF action.is_new_pattern                    # 未被任何原子覆蓋的模式
    RETURN CRITICAL
  IF action.error_recovery_round >= 2         # 修復迴圈已跑 2 輪仍未解
    RETURN CRITICAL
  IF action.inferred_lines > 10               # 推論產生的程式碼超過 10 行
    RETURN CRITICAL

  # ── HIGH（build + encoding + strings + 邏輯）──
  IF action.c_line_count > 50                 # 大函數
    RETURN HIGH
  IF "HAS_PRINTF" IN action.tags AND "HAS_SWITCH" IN action.tags
    RETURN HIGH
  IF "HAS_FORMAT_WIDTH" IN action.tags        # 格式化寬度（高風險）
    RETURN HIGH
  IF "HAS_CHINESE" IN action.tags AND action.c_line_count > 30
    RETURN HIGH

  # ── MEDIUM（build + 行數比對）──
  IF action.c_line_count > 15                 # 標準函數
    RETURN MEDIUM
  IF len(action.tags) >= 2                    # 多個特徵標籤
    RETURN MEDIUM

  # ── LOW（僅 build）──
  RETURN LOW                                  # 單純改名/using/CStr/簡單委派

END FUNCTION
```

## 驗證深度對照表

```
LOW (~5 秒):
  → dotnet build 通過即可
  → 批次策略：5-10 個 LOW 動作合併 → 一次 build

MEDIUM (~10 秒):
  → dotnet build
  → 行數比檢查：C# 行數 >= C 行數 x 0.3
  → 批次策略：3-5 個 MEDIUM 動作合併 → 一次 build + 行數比

HIGH (~30 秒):
  → dotnet build
  → encoding-scan（檢查 FFFD）
  → compare-strings（中文字串覆蓋率）
  → 行數比檢查
  → 批次策略：逐個驗證，不合併

CRITICAL (全套):
  → 全部 verify 子命令
  → checkpoint 記錄存入 workspace/session/
  → 若仍失敗 → 寫入 workspace/staging/ → 停止
  → 批次策略：逐個驗證，不合併，每個都留完整記錄
```

## 三條反幻覺鐵律

```
1. 來源法則: 產出 C# 碼前必須已 Read 過 C 原始碼（零例外）
2. 比例法則: 驗證深度由風險分類器決定，不手動跳過也不過度驗證
3. 回退法則: error-recovery 3 輪未解 → 寫入 staging → 停止（不無限迴圈）
```

## INFERRED 升級規則

```
INFERRED 程式碼 = AI 推論產生、無法直接對照 C 原始碼的程式碼

累積規則:
  IF inferred_total_lines > 10:
    原本風險等級 → 強制升級為 CRITICAL
    觸發完整驗證 + 寫入 workspace/session/

計數方式:
  - 每次寫入 C# 時標記：哪些行有直接 C 來源，哪些是推論
  - 推論行跨函數累積，直到通過 CRITICAL 驗證後歸零
```

## 連結原子

- algorithms/function-classifier.md — 提供標籤作為分類器輸入
- algorithms/error-recovery.md — CRITICAL 等級或驗證失敗時進入
- algorithms/memory-lifecycle.md — 未解問題寫入 staging
- atoms/verification/encoding-scan.md — HIGH+ 驗證步驟
- atoms/verification/compare-strings.md — HIGH+ 驗證步驟
- atoms/verification/line-count-check.md — MEDIUM+ 驗證步驟
- atoms/verification/build-check.md — 所有等級的基礎驗證
