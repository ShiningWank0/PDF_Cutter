@echo off
REM 開発環境のセットアップスクリプト (Windows用)

REM Pythonの仮想環境を作成
if not exist .venv (
  echo Pythonの仮想環境を作成しています...
  python -m venv .venv
)

REM 仮想環境の有効化
call .venv\Scripts\activate.bat

REM 必要なパッケージをインストール
echo 必要なパッケージをインストールしています...
pip install -r requirements.txt

echo 開発環境のセットアップが完了しました！
echo アプリケーションを実行するには：
echo python main.py

pause
