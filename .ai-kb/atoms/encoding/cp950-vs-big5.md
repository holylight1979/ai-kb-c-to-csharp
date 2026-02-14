# cp950 vs big5 編碼差異

> 來源: 移植實戰經驗，Python/C# 編碼處理
> 信心度: VERIFIED
> 前置知識: atoms/encoding/big5-what-is.md
> 相關原子: atoms/encoding/fffd-detection.md
> 觸發條件: 選擇 Big5 解碼器時；遇到解碼錯誤

## 知識
**必須使用 cp950，絕對不要使用 big5。**

### 差異說明
cp950 = Microsoft 對 Big5 的擴充（Code Page 950）：
- 包含 Big5 的所有字元
- **額外**支援 `\xF9xx` 範圍的字元
- 額外支援部分歐元符號等

### 關鍵案例：裏（U+88CF）
```
裏 的 Big5 編碼 = \xF9\xD8
- Python big5 codec: UnicodeDecodeError ← 會失敗！
- Python cp950 codec: '裏' ← 正確解碼
```

### Python 使用方式
```python
# 錯誤
text = raw_bytes.decode('big5')         # F9xx 範圍會報錯
open(f, encoding='big5')                # 同上

# 正確
text = raw_bytes.decode('cp950')        # 完整支援
open(f, encoding='cp950')               # 完整支援

# 加上 -X utf8 旗標避免 Windows console 編碼問題
# python -X utf8 script.py
```

### C# 使用方式
```csharp
// 正確：使用 code page 950
var big5 = Encoding.GetEncoding(950);
string text = big5.GetString(bytes);
byte[] bytes = big5.GetBytes(text);

// 需要先註冊 provider（.NET Core）
Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
```

### 影響的字元（不完整清單）
\xF9D6（碁）、\xF9D7（銹）、\xF9D8（裏）、\xF9D9（墻）等約 30 個字。

## 行動
- 全域搜尋 `'big5'` 並替換為 `'cp950'`
- C# 確認有 `RegisterProvider` 呼叫
- Python 腳本用 `cp950` 並加 `-X utf8`

## 驗證
- `python -X utf8 -c "open('test.c','rb').read().decode('cp950')"` 無錯
- 輸出中文字正確，無 U+FFFD 替換字元

## 失敗時
→ atoms/encoding/fffd-detection.md（檢測解碼失敗）
