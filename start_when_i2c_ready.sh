#!/bin/bash

# 監視間隔（秒）
INTERVAL=1

# パスを設定
SCRIPT_DIR="/home/pi/Develop/fte-2025-rocket"
PYTHON_SCRIPT="$SCRIPT_DIR/env/bin/python $SCRIPT_DIR/main.py"

while true; do
    # i2cdetect 実行結果を取得
    output=$(i2cdetect -y 1)

    # 0x28 と 0x76 が両方検出されたら
    if echo "$output" | grep -q "28" && echo "$output" | grep -q "76"; then
        echo "I2Cデバイス 0x28 と 0x76 を検出しました。スクリプトを起動します..."
        $PYTHON_SCRIPT
        break
    fi

    sleep $INTERVAL
done
