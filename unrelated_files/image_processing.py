from PIL import Image
import os

# 入力画像のパスとアイコンを保存するディレクトリ
input_image_path = "Food-CookItem-Pack-32-02-Nooutline.png"
output_dir = "output_icons"

# 出力ディレクトリが存在しない場合は作成
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 画像を開く
img = Image.open(input_image_path)

# アイコンサイズとスケーリング後のサイズ
icon_size = 32
scaled_size = 840

# 画像の幅と高さ
img_width, img_height = img.size

# 横と縦のアイコンの数
icons_across = img_width // icon_size
icons_down = img_height // icon_size

# すべてのアイコンを抽出して保存
for row in range(icons_down):
    for col in range(icons_across):
        # 各アイコンの座標を計算
        left = col * icon_size
        upper = row * icon_size
        right = left + icon_size
        lower = upper + icon_size

        # アイコンを切り抜く
        icon = img.crop((left, upper, right, lower))

        # アイコンを840x840にスケーリング
        icon = icon.resize((scaled_size, scaled_size))

        # ファイル名を生成
        icon_name = f"icon_{row}_{col}.png"

        # アイコンを保存
        icon.save(os.path.join(output_dir, icon_name))

print(f"すべてのアイコンが {output_dir} に保存されました。")
