# MCP 画像生成ツール

画像生成ツールのMCPサーバー

## 使い方

以下の手順でサーバを実行およびツールを利用できます。

### `.env`ファイルの設定
```env
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxx
OUTPUT_DIR='/path/to/output/dir'
```
出力ディレクトリは起動時に `--WORKDIR_OUT` を指定することも可能

### 開発モードでの起動
MCP Inspectorを使ってサーバをテスト・デバッグするには:
```bash
mcp dev server.py
```

### サーバーの直接起動
```bash
uv run python server.py
```