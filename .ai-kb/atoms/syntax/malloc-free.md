# 記憶體管理轉換

> 來源: DB.C, HANDLER.C, MERC.H
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/syntax/global-linked-list.md
> 觸發條件: 看到 malloc/calloc/free/ALLOC/DISPOSE/realloc

## 知識
C 手動記憶體管理 → C# 由 GC（垃圾回收器）自動處理。

基本轉換：
```c
// C: 分配
ALLOC(ch, CHAR_DATA, 1);
ch = (CHAR_DATA *) malloc(sizeof(CHAR_DATA));
ch = (CHAR_DATA *) calloc(1, sizeof(CHAR_DATA));
```
```csharp
// C#: 直接 new
var ch = new CharData();
```

釋放記憶體：
```c
// C: 手動釋放
free(ch);
DISPOSE(ch);
```
```csharp
// C#: 不需要，GC 自動回收
// 若需要明確釋放資源，實作 IDisposable
ch = null; // 可選，幫助 GC（通常不需要）
```

連結串列插入/刪除模式：
```c
// C: 手動維護 next 指標
ch->next = char_list;
char_list = ch;
```
```csharp
// C#: 使用 List<T>
CharList.Add(ch);
// 或插入到頭部：
CharList.Insert(0, ch);
```

刪除：
```c
// C: 手動斷鏈
if (ch == char_list) char_list = ch->next;
else { for (prev...) prev->next = ch->next; }
free(ch);
```
```csharp
CharList.Remove(ch);
```

## 行動
- 刪除所有 malloc/calloc/free/ALLOC/DISPOSE 呼叫
- 分配改用 `new`
- 連結串列操作改用 `List<T>` 方法
- realloc → 不需要，List 自動擴容

## 驗證
- 無記憶體洩漏相關的手動管理程式碼殘留
- List 操作的插入/刪除順序與原始碼一致

## 失敗時
→ atoms/syntax/global-linked-list.md（連結串列模式）
