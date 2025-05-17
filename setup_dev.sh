#!/bin/bash
# 開発環境のセットアップスクリプト

# Pythonの仮想環境を作成
if [ ! -d ".venv" ]; then
  echo "Pythonの仮想環境を作成しています..."
  python -m venv .venv
fi

# 仮想環境の有効化
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
fi

# 必要なパッケージをインストール
echo "必要なパッケージをインストールしています..."
pip install -r requirements.txt

echo "開発環境のセットアップが完了しました！"
echo "アプリケーションを実行するには："
echo "python main.py"
