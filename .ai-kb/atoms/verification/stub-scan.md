# Stub Scan Verification

> 來源: 審計流程, stub 管理規範
> 信心度: VERIFIED
> 前置知識: stub-empty, stub-simplified
> 相關原子: stub-empty, stub-simplified, build-check
> 觸發條件: 宣稱某檔案移植完成時、審計既有程式碼時

## 知識
Stub scan 搜尋程式碼中殘留的未完成標記：

掃描目標：
- `// TODO` 和 `// TODO:` 註解
- `// FIXME` 註解
- `throw new NotImplementedException()`
- `// stub` 標記
- `/* TODO */` 區塊註解

掃描結果分類：
1. **Critical stub**: 核心功能未實作（如 Interpret、BootDb）
2. **Non-critical stub**: 次要功能或 edge case 未實作
3. **Intentional TODO**: 已知限制或未來改進（需標記原因）

一個檔案被標記為「移植完成」的條件：
- Critical stub 數量 = 0
- 所有 Non-critical stub 有說明為何可延後
- 編譯通過（build-check）

注意：stub-scan 只能找到「空殼 stub」（patterns/stub-empty）。
「簡化 stub」（patterns/stub-simplified）需要 line-count-check 配合偵測。

## 行動
```bash
cd {CSHARP_DIR}
python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src
```

針對單一檔案掃描：
```bash
python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src/TARGET.C.cs
```

## 驗證
完成的檔案應顯示 0 個 TODO/FIXME/NotImplementedException。
若有 intentional TODO，應附帶說明。

## 失敗時
→ stub-empty (實作空殼)
→ stub-simplified (檢查簡化 stub)
→ decode-big5 (讀取 C 原始碼以實作)
