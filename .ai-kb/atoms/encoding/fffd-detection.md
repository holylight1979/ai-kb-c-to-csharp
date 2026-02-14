# U+FFFD 偵測與修復

> 來源: 移植品質檢查流程
> 信心度: VERIFIED
> 前置知識: atoms/encoding/cp950-vs-big5.md
> 相關原子: atoms/encoding/corruption-model.md
> 觸發條件: 品質檢查時發現 U+FFFD 或 PUA 字元

## 知識
U+FFFD（ ）= Unicode 替換字元，表示解碼失敗。
PUA（U+E000-F8FF）= 私用區，可能是 raw bytes 殘留。

### 出現原因
1. Big5 bytes 被當成 UTF-8 解碼 → 無法對應 → U+FFFD
2. 部分工具將無法解碼的 byte 映射到 PUA 範圍
3. 使用 `big5` codec 而非 `cp950` → \xF9xx 範圍解碼失敗

### 偵測方法
```python
# Python 掃描 .cs 檔案
import pathlib
for f in pathlib.Path('src-cs').rglob('*.cs'):
    text = f.read_text('utf-8')
    for i, ch in enumerate(text):
        if ch == '\ufffd':
            print(f"{f}:{i} U+FFFD found")
        if 0xE000 <= ord(ch) <= 0xF8FF:
            print(f"{f}:{i} PUA U+{ord(ch):04X} found")
```

```bash
# 命令列快速掃描
python -X utf8 -c "
import sys, pathlib
for f in pathlib.Path('src-cs').rglob('*.cs'):
    t = f.read_text('utf-8')
    if '\ufffd' in t or any(0xE000<=ord(c)<=0xF8FF for c in t):
        print(f'DIRTY: {f}')
"
```

### 修復流程
1. 找到損壞的 .cs 檔案與行號
2. 定位對應的原始 C 原始碼
3. 用 cp950 正確解碼原始字串
4. 替換 .cs 中的損壞字元

### 零容忍政策
- 最終交付的 .cs 檔案中不允許任何 U+FFFD
- 不允許任何 PUA 範圍字元
- CI/CD 應包含自動掃描

## 行動
- 定期執行 U+FFFD 掃描
- 發現後立即定位原始 C 檔案並修復
- 確認使用 cp950 而非 big5 解碼

## 驗證
- 掃描結果為零 U+FFFD
- 掃描結果為零 PUA 字元
- 所有中文字串在 MUD 客戶端正確顯示

## 失敗時
→ atoms/encoding/corruption-model.md（理解損壞路徑並反向修復）
