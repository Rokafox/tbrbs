import random
import time

def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = random.normalvariate(mean, std)
        if min_value <= value <= max_value:
            return value

# 時間計測開始
start_time = time.time()

# 関数を400,000回呼び出し
for _ in range(400000):
    normal_distribution(1, 4000, 1000, 1000)

# 時間計測終了
end_time = time.time()

# 実行時間を計算
execution_time = end_time - start_time
print(f"400,000回の関数呼び出しにかかった時間: {execution_time:.2f} 秒")