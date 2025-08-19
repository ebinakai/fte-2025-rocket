# 2025年度 新入生プロジェクト ロケットチーム5

2025年度 FTE16期の新入生プロジェクトのロケットに乗せる電装のプログラムです

## インストール

```bash
python -m venv env
source ./env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## 設定の変更

`main.py` の14行目の値を変更すると実行時間が変わります．ロケットに搭載する場合は `1200` 等に設定するといいかもしれません．

```python
# 実行時間
RUN_TIME = 10         # sec
```

## システム起動時にプログラムを実行する

`/home/pi/Develop/fte-2025-rocket`に設置することを前提に以下のスクリプトが組まれているので，パスを適宜変更してください．`i2c-launch.service` をサービス登録してください．

```bash
sudo mv i2c-launch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable i2c-launch.service
sudo systemctl start i2c-launch.service
```
