# AI 知識庫入口

> 本知識庫是 AI 自主執行 C→C# MUD 伺服器移植的核心引擎。
> AI 收到任務後從本檔案開始，由演算法決定讀取路徑。

## 三條反幻覺鐵律

1. **來源法則**: 產出 C# 碼前必須已 Read 過 C 原始碼（零例外）
2. **比例法則**: 驗證深度由風險分類器決定，不手動跳過也不過度驗證
3. **回退法則**: error-recovery 3 輪未解 → 寫入 workspace/staging/ → 停止

## 任務路由

收到使用者指令後，依據 `algorithms/task-router.md` 分類：

| 關鍵詞 | 任務類型 | 進入流程 |
|--------|---------|---------|
| 移植 / port / 轉換 | PORT_NEW | workflows/port-new-file.md |
| 驗證 / verify / 審查 | VERIFY | workflows/verify-existing.md |
| 亂碼 / FFFD / corruption | FIX_CORRUPTION | workflows/fix-corruption.md |
| CStr / 字串 / 集中化 | CSTR_ONLY | workflows/port-new-file.md#CSTR |
| stub / 委派 | STUB_FIX | atoms/patterns/stub-*.md |

## 核心演算法

| 演算法 | 用途 | 呼叫時機 |
|--------|------|---------|
| task-router.md | 任務分類 → 派發 | 接到指令時 |
| function-classifier.md | 分析 C 函數特徵 → 載入原子 | 移植每個函數前 |
| trap-detector.md | 掃描 C# → 匹配陷阱模式 | 移植完成後 |
| hallucination-guard.md | 風險分類 → 比例驗證 | 每個修改動作 |
| error-recovery.md | 錯誤分類 → 修復迴圈 | 驗證失敗時 |
| memory-lifecycle.md | 記憶分類 + 清理 | 任務完成時 |
| skill-orchestrator.md | Skill 偵測/建立/進化 | 任務完成時 |
| efficiency-monitor.md | 效率度量 + 自我調校 | 定期評估 |

## 原子知識索引

| 類別 | 路徑 | 檔案數 | 覆蓋範圍 |
|------|------|--------|---------|
| 編碼 | atoms/encoding/ | 7 | Big5/CP950/UTF-8 |
| CStr | atoms/cstr/ | 7 | 字串集中化系統 |
| 語法 | atoms/syntax/ | 11 | C→C# 轉換規則 |
| 模式 | atoms/patterns/ | 8 | 架構模式 |
| 陷阱 | atoms/traps/ | 20 | A-T 已知陷阱 |
| 驗證 | atoms/verification/ | 8 | 驗證工具用法 |

## 快速開始

```
AI 收到「移植 XXX.C」→
  1. 讀本檔案（你正在讀）
  2. → algorithms/task-router.md → PORT_NEW
  3. → workflows/port-new-file.md → 狀態機開始
  4. → 每個函數: function-classifier → 載入需要的原子
  5. → 完成後: trap-detector + VERIFY + memory-lifecycle
```
