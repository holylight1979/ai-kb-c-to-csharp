# Empty Stub Pattern

> 來源: audit-findings.md, 移植實務經驗
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: stub-simplified, function-call-vs-assign
> 觸發條件: 移植新檔案時、審計既有 C# 程式碼時

## 知識
空殼 stub 是最容易辨識的未完成模式。方法簽名存在，但函式本體只有：

```csharp
// TODO: implement from C source
public static void Interpret(CharData ch, string argument)
{
    // TODO
}
```

或使用 NotImplementedException：

```csharp
public static void LoadCharObj(Descriptor d, string name)
{
    throw new NotImplementedException("LoadCharObj not ported yet");
}
```

這類 stub 在編譯時不會報錯，但執行時會導致功能完全缺失或崩潰。
COMM.C 中已知有 6 個 CRITICAL stub：Interpret、UpdateHandler、
LoadCharObj、SaveCharObj、Crypt、BootDb delegation。

常見陷阱：stub 被其他模組呼叫時，不會有編譯錯誤，
只有在 runtime 才會發現問題。相關陷阱：E-fake-completion。

## 行動
1. 執行 stub-scan 工具找出所有空殼
2. 對照原始 C 原始碼實作完整邏輯
3. 使用 `decode-big5` 讀取 C 原始碼
4. 實作後執行 `dotnet build` 確認編譯通過

## 驗證
```bash
python -X utf8 verify.py stub-scan --path {CSHARP_DIR}/MudGM/Src
```
目標檔案的 stub 數量應為 0。

## 失敗時
→ stub-scan (重新掃描確認遺漏)
→ build-check (確認編譯通過)
