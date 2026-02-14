# Decode Big5 Verification Tool

> 來源: 編碼處理規範, Big5 原始碼閱讀流程
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: encoding-scan, compare-strings, compare-constants
> 觸發條件: 需要閱讀 C 原始碼以進行移植或比對時

## 知識
原始 C 原始碼使用 Big5 編碼，現代編輯器無法直接正確顯示。
此工具將 Big5 解碼為可讀的 UTF-8 輸出。

關鍵：必須使用 `cp950` 而非 `big5` 編解碼器。
- Python 的 `big5` codec 無法處理 `\xF9xx` 範圍
- `cp950` 是 Microsoft 的 Big5 超集，涵蓋更多字元
- 範例：「裏」(U+88CF) = Big5 `\xF9\xD8`，只有 cp950 能解碼

用途：
1. 移植前逐行閱讀 C 函式的完整邏輯
2. 確認中文字串的正確內容
3. 比對 C 與 C# 的邏輯差異
4. 計算 C 函式的行數（用於 line-count-check）

支援指定行數範圍，避免一次輸出整個檔案：
```bash
# 顯示第 100-200 行
python -X utf8 verify.py decode-big5 SRC/ACT_WIZ.C 100 200
```

大檔案策略：
1. 先用不帶行數範圍的方式找到目標函式位置
2. 再用行數範圍精確查看該函式

## 行動
```bash
cd {CSHARP_DIR}
# 解碼整個檔案
python -X utf8 verify.py decode-big5 SRC/FIGHT.C

# 解碼指定行數範圍
python -X utf8 verify.py decode-big5 SRC/FIGHT.C 150 250
```

## 驗證
輸出應為可讀的繁體中文。若出現亂碼或 U+FFFD，
表示原始檔案可能損壞或有非 Big5 字元。

## 失敗時
→ encoding-scan (掃描是否有已知的編碼問題)
→ compare-strings (交叉比對字串)
