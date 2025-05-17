# PDF サイズ制限対応分割ツール

このツールは、ファイルサイズ制限のある環境で使用するために、PDFファイルを適切なサイズに分割するための便利なユーティリティです。

## 主な機能

### 基本機能
- PDFファイルを指定したサイズ制限に基づいて複数のファイルに分割
- 元のPDFファイルは変更せず、新しいファイルとして保存
- サイズ制限を超えている場合のみ分割処理を実行（それ以外は何もしない）

### 高度な分割アルゴリズム
- バイナリサーチを使用して最適な分割点を算出
- 実際のPDF出力サイズを一時ファイルで計算し、正確なサイズ分割を実現
- 各分割ファイルが指定サイズ以下になるように調整

### 直感的なユーザーインターフェース
- カスタマイズ可能なサイズ制限設定
  - キーボード入力による直接数値指定が可能
  - KB/MB/GBの単位切替
  - +/-ボタンによる値の調整
- PDFファイル情報の表示
  - ファイル名、ページ数、サイズなどの基本情報
  - 現在の制限設定での推定分割数
- ファイル選択と出力先指定の簡単な操作

### エラー耐性
- 全角数字を半角に自動変換
- 数字以外の文字を自動的に除去
- 単位に応じた適切な最大値/最小値の範囲チェック
- 入力が無効な場合はエラーを表示して終了

## インストール方法

### 実行ファイルを使用する方法（推奨）

1. [GitHub Releases](https://github.com/ユーザー名/PDF_Cutter/releases)ページから、お使いのOSに合ったファイルをダウンロードします。
   - Windows: `pdf-cutter-windows.zip`
   - macOS: `pdf-cutter-macos.zip`
   - Linux: `pdf-cutter-linux.zip`

2. ダウンロードしたZIPファイルを解凍します。

3. 解凍したフォルダ内の実行ファイルをダブルクリックして実行します。
   - Windows: `pdf_cutter.exe`
   - macOS/Linux: `pdf_cutter`

### 開発者向け: ソースコードから実行する方法

#### 前提条件
- Python 3.8以上
- pip（Pythonパッケージマネージャー）

#### セットアップ手順

**Windows:**
```
.\setup_dev.bat
```

**macOS/Linux:**
```
chmod +x setup_dev.sh
./setup_dev.sh
```

実行:
```
python main.py
```

## ビルド方法

このプロジェクトはNuitkaを使用して、実行ファイルを生成しています。ビルドは通常、GitHub Actionsによって自動的に行われますが、手動でビルドすることも可能です。

### 手動ビルド方法

#### standaloneモード (依存ファイルが展開される)

```bash
# 必要なパッケージのインストール
pip install nuitka

# Windowsでビルド
python -m nuitka --standalone --follow-imports --plugin-enable=tk-inter --disable-console main.py

# macOS/Linuxでビルド
python -m nuitka --standalone --follow-imports --plugin-enable=tk-inter main.py
```

#### onefileモード (単一実行ファイル)

```bash
# 必要なパッケージのインストール
pip install nuitka

# Windowsでビルド
python -m nuitka --onefile --follow-imports --plugin-enable=tk-inter --disable-console main.py

# macOS/Linuxでビルド
python -m nuitka --onefile --follow-imports --plugin-enable=tk-inter main.py
```

### onefileとstandaloneの違い

- **standalone**: 複数のファイルが生成され、より高速に起動しますが、ファイル構造を維持する必要があります
- **onefile**: 単一の実行ファイルが生成され、より配布が簡単ですが、起動時に一時フォルダに解凍されるため起動が遅くなります

### OS別の注意点

- **Windows**: 通常はonefileモードが推奨されます（使いやすさのため）
- **macOS**: セキュリティ制限により、アプリ初回起動時に「開発元を確認できないアプリ」の警告が表示されることがあります
- **Linux**: 必要なシステムライブラリがインストールされていることを確認してください

## 使用方法

1. **PDFファイルを選択**: 「参照...」ボタンでPDFファイルを選択します
2. **出力先を指定**: デフォルトは元のPDFと同じ場所です（オプションで変更可能）
3. **サイズ制限を設定**:
   - 値: 直接入力、または +/- ボタンで調整
   - 単位: KB/MB/GBから選択
4. **分割を実行**: 「実行」ボタンをクリックして処理を開始

### 入力値の処理

- **全角・半角数字の混合**: 
   - すべての全角数字は半角に変換されます
   - 例: 「１２３」→「123」
   - 例: 「1０9」→「109」

- **文字の混入**: 
   - 数字以外の文字は自動的に除去されます
   - 例: 「123abc」→「123」
   - 例: 「a1b2c3」→「123」
   - 例: 「1,000」→「1000」
   
- **文字のみ/無効な入力**: 
   - 数字が含まれていない場合（「abc」など）はエラーメッセージが表示されプログラムが終了します
   - スペースや特殊文字のみの場合も同様です

### 出力ファイル名

分割されたファイルは以下の命名規則で保存されます：
- 元のファイル名: `example.pdf`
- 分割後: `example_part1.pdf`, `example_part2.pdf`, `example_part3.pdf`, ...

## 技術仕様

- **GUI**: CustomTkinterを使用したモダンなインターフェース
- **PDF処理**: PyPDF2による高速で効率的なPDF操作
- **入力検証**: 正規表現と文字変換を使用した堅牢な入力処理

## 動作要件

- Python 3.x
- 必要パッケージ:
  - PyPDF2
  - customtkinter
  - packaging

## 注意事項

- 一部のPDFは、内部構造により1ページでもサイズ制限を超える場合があります。その場合は分割できません。
- PDFにセキュリティ設定がある場合は処理できない場合があります。

## ライセンス

MITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。