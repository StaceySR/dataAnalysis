# # 大列表，包含多个小列表
# big_list = [
#     ['t0_a', 't0_b', 't0_c'],
#     ['t1_a', 't1_b', 't1_c'],
#     ['t2_a', 't2_b', 't2_c']
#     # 可以继续添加更多的小列表
# ]
#
# # 计算零向量的长度
# zero_vector_length = 9
#
# result = []
#
# for sublist in big_list:
#     index = big_list.index(sublist)
#     print("index: ", big_list.index(sublist))
#     zero_vector = [0] * zero_vector_length
#     zero_vector[index * len(sublist):(index+1) * len(sublist)] = sublist
#     result.append(zero_vector)
#
# print(result)
#
#
# import numpy as np
#
# # 原始二维数组
# array_2d = np.array(result)
#
# # 转换维度
# array_2d_transposed = np.transpose(array_2d)
# # 或者使用T属性
# # array_2d_transposed = array_2d.T
#
# print("原始二维数组:")
# print(array_2d)
# print("转换维度后的数组:")
# print(array_2d_transposed)

# import matplotlib.pyplot as plt
# import numpy as np
#
# # 数据
# categories = ['Category 1', 'Category 2', 'Category 3']
# values1 = [20, 30, 25]
# values2 = [15, 25, 20]
# values3 = [10, 15, 12]
#
# # 创建一个numpy数组，表示每个值的起始位置
# start_values = np.zeros(len(categories))
#
# # 绘图
# plt.barh(categories, values1, label='Value 1', left=start_values)
# plt.barh(categories, values2, label='Value 2', left=start_values+values1)
# plt.barh(categories, values3, label='Value 3', left=start_values+values1+values2)
#
# # 设置标签和标题
# plt.xlabel('Values')
# plt.ylabel('Categories')
# plt.title('Stacked Horizontal Bar Chart')
#
# # 添加图例
# plt.legend()
#
# # 显示图表
# plt.show()


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# 创建图形和坐标轴对象
fig, ax = plt.subplots()

# 数据
x = [1, 2, 3, 4]
y1 = [10, 20, 30, 40]
y2 = [15, 25, 35, 45]

# 绘制图形
line1, = ax.plot(x, y1, label='Line 1', color='red')
line2, = ax.plot(x, y2, label='Line 2', color='blue')

# 设置自定义图例项
custom_legend = [Line2D([], [], color='red', label='Custom Label 1'),
                 Line2D([], [], color='blue', label='Custom Label 2')]

# 设置图例
ax.legend(handles=custom_legend)

# 显示图形
plt.show()
