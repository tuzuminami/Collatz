# Collatz 数列計算スクリプト

このリポジトリは、コラッツ数列を計算するためのシンプルな Python スクリプトのみで構成されています。Web アプリや外部ライブラリは不要で、標準ライブラリだけで動作します。

## 必要環境

- Python 3.10 以上

## 使い方

1. ターミナルでリポジトリのルートディレクトリに移動します。
2. 計算したい開始値を引数として `collatz.py` を実行します。

```bash
python3 collatz.py 27
```

実行すると、0 から始まるステップ番号と各ステップの値が表示されます。

```
Step  0: 27
Step  1: 82
Step  2: 41
...
Step 111: 1
```

## Python モジュールとして利用する

Python から関数を直接呼び出すこともできます。

```python
from collatz import collatz_sequence

print(collatz_sequence(27))
```

`collatz_sequence` は開始値から 1 に到達するまでの値をリストで返します。開始値が 1 未満の場合は `ValueError` を送出します。
