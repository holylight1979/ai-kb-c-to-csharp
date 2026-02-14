# 編碼損壞模型與修復

> 來源: 移植實戰經驗，編碼損壞分析
> 信心度: VERIFIED
> 前置知識: atoms/encoding/big5-what-is.md, atoms/encoding/0x5C-backslash.md
> 相關原子: atoms/encoding/fffd-detection.md
> 觸發條件: 遇到無法直接修復的亂碼或損壞中文字串

## 知識
兩條主要損壞路徑。

### 路徑一：標準損壞（Big5 → UTF-8 誤讀）
```
原始 Big5 bytes: A4 A4 A4 E5  ("中文")
當成 UTF-8 讀取:
  A4 → 非法 UTF-8 開頭 → U+FFFD
  A4 → U+FFFD
  A4 → U+FFFD
  E5 → 不完整 3-byte UTF-8 → U+FFFD
結果: ""
```

修復：找到原始 Big5 bytes，用 cp950 正確解碼。

### 路徑二：0x5C 跳脫損壞
```
原始 Big5: A5 5C B3 5C  ("功許")
C 字串處理把 5C 當作 \：
  A5 → 保留
  5C → \ (跳脫開始)
  B3 → 被跳脫序列消耗
  5C → \ (跳脫開始)
結果：不可預測的 byte 序列
```

修復：反向模擬跳脫處理，推導原始 bytes。

### 修復演算法（路徑一）
```python
def fix_standard_corruption(corrupted_text, original_c_file):
    """從原始 C 檔案重新擷取正確字串"""
    raw = open(original_c_file, 'rb').read()
    # 在 raw bytes 中搜尋相鄰的上下文（非中文部分）
    # 找到後，擷取完整 Big5 byte 序列
    # 用 cp950 正確解碼
    return raw_segment.decode('cp950')
```

### 修復演算法（路徑二）
```python
def fix_backslash_corruption(corrupted_bytes):
    """反向模擬 0x5C 跳脫"""
    result = bytearray()
    i = 0
    while i < len(corrupted_bytes):
        b = corrupted_bytes[i]
        if 0x81 <= b <= 0xFE:
            # Big5 前導：下一個 byte 即使是 5C 也是合法後隨
            result.append(b)
            i += 1
            if i < len(corrupted_bytes):
                result.append(corrupted_bytes[i])
            i += 1
        else:
            result.append(b)
            i += 1
    return result.decode('cp950')
```

### 預防措施
- 永遠在 Big5-aware 模式下處理 byte 流
- 絕不逐 byte 比較含 Big5 的資料
- 轉碼管線：原始 Big5 → cp950 解碼 → UTF-8 .cs

## 行動
- 判斷損壞屬於哪條路徑
- 從原始 C 原始碼重新擷取正確字串
- 替換 .cs 中的損壞部分

## 驗證
- 修復後的字串與原始 Big5 解碼結果一致
- 無 U+FFFD 殘留

## 失敗時
→ 手動用十六進位編輯器比對原始 C 檔案 bytes
