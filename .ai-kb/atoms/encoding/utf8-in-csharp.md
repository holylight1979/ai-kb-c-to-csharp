# C# UTF-8 原始碼與 Big5 執行時轉換

> 來源: C# 專案架構，網路 I/O 設計
> 信心度: VERIFIED
> 前置知識: atoms/encoding/big5-what-is.md, atoms/encoding/cp950-vs-big5.md
> 相關原子: atoms/cstr/why-centralize.md
> 觸發條件: 撰寫 C# 原始碼中的中文字串；處理 telnet 輸出

## 知識
C# 原始碼與執行時期使用不同編碼。

### 原始碼層（.cs 檔案）
- 編碼：**UTF-8**（含 BOM 或不含皆可）
- 中文字串直接寫在 .cs 中：`"你好世界"`
- IDE/編輯器必須以 UTF-8 開啟
- **絕對不要**在 .cs 檔案中放 raw Big5 bytes

### 執行時層（網路 I/O）
MUD 客戶端（telnet）期望收到 Big5 編碼：
```csharp
// 初始化（程式啟動時執行一次）
Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
var big5 = Encoding.GetEncoding(950);

// 發送給玩家（UTF-16 → Big5 bytes）
byte[] output = big5.GetBytes(message);
socket.Send(output);

// 接收玩家輸入（Big5 bytes → UTF-16）
byte[] input = new byte[4096];
int len = socket.Receive(input);
string text = big5.GetString(input, 0, len);
```

### 檔案讀取層（區域檔案）
```csharp
// 讀取 Big5 區域檔案
using var reader = new StreamReader(path, Encoding.GetEncoding(950));
string content = reader.ReadToEnd();
// content 現在是 C# string (UTF-16)，可正常操作
```

### CStr.cs 中的字串
```csharp
// CStr.cs 是 UTF-8 .cs 檔案
public const string COMM_001 = "歡迎來到天乙神乩！";
// 編譯後存為 .NET 內部 UTF-16
// 輸出時由 Encoding.GetEncoding(950) 轉為 Big5
```

### NuGet 相依
```xml
<!-- .csproj 中需要 -->
<PackageReference Include="System.Text.Encoding.CodePages" Version="..." />
```

## 行動
- .cs 檔案一律 UTF-8 存檔
- 程式啟動時呼叫 RegisterProvider
- 網路 I/O 用 GetEncoding(950) 轉換
- 區域檔案用 GetEncoding(950) 讀取

## 驗證
- .cs 檔案用 `file` 命令確認為 UTF-8
- telnet 連入後中文正確顯示
- 區域檔案讀取無 U+FFFD

## 失敗時
→ atoms/encoding/cp950-vs-big5.md（確認編碼選擇）
