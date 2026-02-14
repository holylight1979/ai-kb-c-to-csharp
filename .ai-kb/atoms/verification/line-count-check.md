# Line Count Check Verification

> 來源: stub-simplified 偵測方法
> 信心度: VERIFIED
> 前置知識: stub-simplified, decode-big5
> 相關原子: stub-simplified, decode-big5, stub-scan
> 觸發條件: 審計已移植函式的完整性時

## 知識
行數比較是偵測「簡化 stub」（stub-simplified）的量化方法。

原則：C 和 C# 的行數應大致相當。
C# 通常會稍長（因為型別宣告較詳細），但不應短太多。

警告閾值：
```
C 行數 > C# 行數 × 3  →  高度可疑，需逐行審查
C 行數 > C# 行數 × 2  →  中度可疑，應檢查
C 行數 ≈ C# 行數      →  正常範圍
```

例外情況（行數差異合理）：
- C 使用大量 `sprintf` + `strcat`，C# 用字串插值一行搞定
- C 的鏈結串列操作在 C# 用 List<T> 簡化
- C 的手動記憶體管理在 C# 不需要

仍需警惕的情況：
- C 有 for/while 迴圈遍歷全域列表 → C# 也必須有
- C 有多個 if/else 分支 → C# 不能省略
- C 有錯誤處理/edge case → C# 也必須有

使用方式：
1. 用 `decode-big5` 找到 C 函式，計算起迄行數
2. 在 C# 中找到對應函式，計算行數
3. 比較比率

## 行動
```bash
cd {CSHARP_DIR}
# 步驟 1：解碼 C 函式，找到行數範圍
python -X utf8 verify.py decode-big5 SRC/FIGHT.C 100 200

# 步驟 2：用 Grep 找到 C# 對應函式
# Grep "public static.*FunctionName" in {CSHARP_DIR}/MudGM/Src/
```

手動比對行數差異，記錄可疑函式。

## 驗證
所有重要函式的行數比率應在合理範圍內（< 3x）。
超過閾值的函式應逐一比對邏輯步驟。

## 失敗時
→ stub-simplified (確認是否為簡化 stub)
→ decode-big5 (重新閱讀 C 原始碼)
→ function-call-vs-assign (檢查是否有不當簡化)
