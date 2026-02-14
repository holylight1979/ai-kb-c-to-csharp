# Task Router — 任務分類器

> 呼叫時機: AI 收到使用者指令的第一步（INDEX.md 入口）
> 輸入: 使用者指令字串（自然語言）
> 輸出: 任務類型 TASK + 對應 workflow 路徑

## 演算法

```
FUNCTION task_route(instruction: string) → (TASK, workflow_path)

  # ── 第一階段：關鍵字分類 ──

  keywords = lowercase(instruction)

  IF match(keywords, ["移植", "port", "轉換", "transpile", "新增檔案"])
    TASK = PORT_NEW
    RETURN (TASK, "workflows/port-new-file.md")

  IF match(keywords, ["驗證", "verify", "審查", "audit", "檢查"])
    TASK = VERIFY
    RETURN (TASK, "workflows/verify-existing.md")

  IF match(keywords, ["亂碼", "FFFD", "corruption", "編碼錯誤", "garbled"])
    TASK = FIX_CORRUPTION
    RETURN (TASK, "workflows/fix-corruption.md")

  IF match(keywords, ["CStr", "字串", "集中化", "centralize", "常數化"])
    TASK = CSTR_ONLY
    RETURN (TASK, "workflows/port-new-file.md#step-CSTR")

  IF match(keywords, ["stub", "委派", "delegation", "skeleton", "空殼"])
    TASK = STUB_FIX
    RETURN (TASK, "atoms/patterns/stub-*.md")

  # ── 第二階段：模糊推論 ──

  IF contains_filename(keywords, pattern="*.C")
    # 提到 C 檔名但未明說動作 → 預設移植
    TASK = PORT_NEW
    RETURN (TASK, "workflows/port-new-file.md")

  IF contains_filename(keywords, pattern="*.C.cs")
    # 提到 C# 檔名 → 預設驗證
    TASK = VERIFY
    RETURN (TASK, "workflows/verify-existing.md")

  # ── 第三階段：無法判斷 ──

  TASK = ASK_USER
  RETURN (TASK, null)
  # → 回覆使用者：「請問您想要 移植/驗證/修復 哪個檔案？」

END FUNCTION
```

## 分派後的初始化動作

```
ON DISPATCH(TASK, workflow_path):
  1. Read workflow_path → 載入狀態機
  2. 從指令中提取目標檔案名稱 (e.g., "MAGIC.C")
  3. 確認檔案存在於 SRC/ 或 {CSHARP_DIR}/MudGM/Src/
  4. 建立 workspace/session/ 暫存目錄（若尚未存在）
  5. 啟動 workflow 的 STATE: INIT
```

## 多任務處理

```
IF instruction 包含多個檔案:
  FOR EACH file IN extract_files(instruction):
    task_route(instruction_for(file))
  # 依序處理，每個檔案獨立走完整 workflow
```

## 連結原子

- workflows/port-new-file.md — PORT_NEW 的完整狀態機
- workflows/verify-existing.md — VERIFY 的完整狀態機
- workflows/fix-corruption.md — FIX_CORRUPTION 的完整狀態機
- atoms/patterns/stub-empty.md — STUB_FIX 的空殼處理
- atoms/patterns/stub-simplified.md — STUB_FIX 的簡化處理
- atoms/cstr/new-file-setup.md — CSTR_ONLY 的前置設定
