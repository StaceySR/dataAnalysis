import os
import pandas as pd
from datetime import datetime
import numpy as np

print(np.__version__)
import matplotlib.pyplot as plt
from plotnine import *
import xlwt
from itertools import groupby
from matplotlib.lines import Line2D


def process_csv_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            print('file: ', file)
            if file.endswith(".csv"):
                if "_processed" not in file and "_utf8" not in file:
                    file_path = os.path.join(root, file)
                    # 读取CSV文件，默认使用UTF-8编码
                    df = pd.read_csv(file_path)

                    # 将数据重新写入CSV文件，编码为GBK
                    new_file_path = os.path.splitext(file_path)[0] + "_gbk.csv"
                    df.to_csv(new_file_path, index=False, encoding="gbk")


def concatenate_csv_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        # print(":  ", root, dirs, files)
        if len(dirs) == 0:  # 判断是否为task文件夹（没有子文件夹）
            task_folder_path = root
            csv_files = [f for f in files if f.endswith(".csv") and "_gbk" in f]

            if not csv_files:
                print(f"在文件夹 {task_folder_path} 中没有找到CSV文件.")
                continue

            dfs = []
            for file in csv_files:
                file_path = os.path.join(task_folder_path, file)
                df = pd.read_csv(file_path, encoding='gbk')
                dfs.append(df)

            if not dfs:
                print(f"在文件夹 {task_folder_path} 中没有读取到CSV数据.")
                continue

            merged_df = pd.concat(dfs, ignore_index=True)
            merged_df.sort_values(by="time", inplace=True)

            merged_file_path = os.path.join(task_folder_path, "merged_data.csv")
            print("merged: ", merged_file_path)
            merged_df.to_csv(merged_file_path, index=False, encoding="gbk")
            print(f"合并完成，结果保存为: {merged_file_path}")


# def extract_fields(folder_path):
#     for root, dirs, files in os.walk(folder_path):
#         print(root, dirs, files)
#         if "merged_data.csv" in files:
#             task_folder = os.path.basename(root)
#             # print("task: ", task_folder)
#             # task_folder_path = os.path.join(folder_path, task_folder)
#             task_folder_path = root
#             merged_file_path = os.path.join(task_folder_path, "merged_data.csv")
#
#             df = pd.read_csv(merged_file_path, encoding='gbk')
#             type_values = df['type'].tolist()
#             time_values = df['time'].tolist()
#
#             # 提取出start、nodeClick、Modify相关的start和finished
#
#             task_output_path = os.path.join(task_folder_path, "output.csv")
#             output_df = pd.DataFrame({"type": type_values, "time": time_values})
#             output_df.to_csv(task_output_path, index=False)
#
#             print(f"任务文件夹 {task_folder} 中的数据已提取并保存至 {task_output_path}.")


def extract_fields(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith("_gbk.csv"):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path, encoding='gbk')
                type_values = df['type'].tolist()
                time_values = df['time'].tolist()

                print(f"文件 {file} 中的数据:")
                print("Type字段内容:", type_values)
                print("Time字段内容:", time_values)

                task_output_path = os.path.splitext(file_path)[0] + "_output.csv"
                output_df = pd.DataFrame({"type": type_values, "time": time_values})
                output_df.to_csv(task_output_path, index=False)
                print()


def timeCalculate(time_start, time_end):
    # print('time_start: ', time_start)
    # print('time_end: ', time_end)
    # 转换为时间格式
    time_format = '%H:%M:%S'
    time_start = datetime.strptime(time_start, time_format)
    time_end = datetime.strptime(time_end, time_format)

    # 计算时间差
    time_diff = time_end - time_start

    # 输出时间差
    # print('时间差:', time_diff)
    # print('相差秒数:', time_diff.total_seconds())
    return time_diff.total_seconds()


def processedDrawData(user_no, task_no, data):  # 将数据删减成画图需要的格式
    drawDataTimeLine = []
    drawDataTimeLineType = []
    for i in range(len(data)):
        drawDataTimeLine.append(data[i]['time_line'])
        drawDataTimeLineType.append(data[i]['time_line_type'])
    drawData = {"user_no": user_no, "task_no": task_no, "drawDataTimeLine": drawDataTimeLine, "drawDataTimeLineType": drawDataTimeLineType}
    print(drawData)
    return drawData


def missingTime(data, first_time, end_time, end_index):
    if data[0]['time_start_index'] != 1:
        start_missing_record = {
            'time_start': first_time,
            'time_start_index': 1,
            'time_start_type': 'nodeClick',
            'time_end': data[0]['time_start'],
            'time_end_index': data[0]['time_start_index'],
            'time_end_type': 'nodeClick',
            'time_line': str(timeCalculate(first_time, data[0]['time_start'])),
            'time_line_type': 'TIMELINE 0: nodeClick或者其他操作'
        }
        # print("没有start: ", start_missing_record)
        data.append(start_missing_record)
    for i in range(1, len(data)):
        prev_index = data[i-1]['time_end_index']
        next_index = data[i]['time_start_index']
        if next_index - prev_index > 1:
            missing_start_index = prev_index + 1
            missing_start = data[i-1]['time_end']
            missing_end_index = next_index - 1
            missing_end = data[i]['time_start']
            missing_interval = timeCalculate(missing_start, missing_end)

            missing_record = {
                'time_start': missing_start,
                'time_start_index': missing_start_index,
                'time_start_type': 'nodeClick',
                'time_end': missing_end,
                'time_end_index': missing_end_index,
                'time_end_type': 'nodeClick',
                'time_line': str(missing_interval),
                'time_line_type': 'TIMELINE 0: nodeClick或者其他操作'
            }
            # print(missing_record)
            data.append(missing_record)
        # 按照索引排序

    if data[-1]['time_end'] != end_time:
        print("最后缺失", data[-1]['time_end'], end_time)
        start_missing_record = {
            'time_start': data[-1]['time_end'],
            'time_start_index': data[-1]['time_end_index'],
            'time_start_type': 'nodeClick',
            'time_end': end_time,
            'time_end_index': end_index,
            'time_end_type': 'nodeClick',
            'time_line': str(timeCalculate(data[-1]['time_end'], end_time)),
            'time_line_type': 'TIMELINE 0: nodeClick或者其他操作'
        }
        # print("没有start: ", start_missing_record)
        data.append(start_missing_record)
    data = sorted(data, key=lambda x: x['time_start_index'])
    # print(data)
    return data


def splitTimeline(folder_path, txtFile):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith("_gbk_output.csv"):
                file_path = os.path.join(root, file)
                print("file_path: ", file_path)
                # 提取01和T0位置的数据
                split_path = file_path.split("\\")
                user_no = split_path[1]
                task_no = split_path[2]

                df = pd.read_csv(file_path, encoding='gbk')
                type_values = df['type'].tolist()
                time_values = df['time'].tolist()

                time_start = -1
                time_start_index = -1
                time_start_type = ''
                time_end = -1
                time_end_index = -1
                time_end_type = ''
                time_line = -1
                time_line_type = None
                time_line_list = []
                # TIMELINE 0: nodeClick或者其他操作
                # 剩下的没被捕捉到的时间段
                authoring_type = False
                for i in range(len(type_values)):
                    if 'authoring' in type_values[i]:
                        authoring_type = True

                for i in range(len(type_values)):
                    if time_start != -1:
                        print(type_values[i], time_start, time_end)
                    # TIMELINE 1: Service Program Authoring through Natural Language
                    # 一开始先找type==authoringNEW-start (start)
                    # 接下去找第一个遇到的type==js2flow-finished，timeline=authoringNEW-start--js2flow-finished
                    # if type_values[i] == 'start' and authoring_type:
                    if type_values[i] == 'authoringNEW-start' and authoring_type:
                        time_start = time_values[i-1]
                        time_start_index = i
                        # time_start_type = 'start'
                        time_start_type = 'authoringNEW-start'
                        authoring_type = False

                        for j in range(i, len(type_values)):
                            if type_values[j] == 'js2flow-finished' and time_start != -1:
                                time_end = time_values[j]
                                time_end_index = j
                                time_end_type = 'js2flow-finished'
                                time_line = timeCalculate(time_start, time_end)  # 时间差 14:34:57-14:33:24
                                time_line_type = 'TIMELINE 1: Service Program Authoring through Natural Language'
                                if time_line_type:
                                    time_line_list.append(
                                        {'time_start': time_start, 'time_start_index': time_start_index,
                                         'time_start_type': time_start_type,
                                         'time_end': time_end, 'time_end_index': time_end_index,
                                         'time_end_type': time_end_type,
                                         'time_line': time_line, 'time_line_type': time_line_type})
                                    print({'time_start': time_start, 'time_start_index': time_start_index,
                                           'time_start_type': time_start_type,
                                           'time_end': time_end, 'time_end_index': time_end_index,
                                           'time_end_type': time_end_type,
                                           'time_line': time_line, 'time_line_type': time_line_type})
                                    time_start = -1
                                    time_start_index = -1
                                    time_start_type = ''
                                    time_end = -1
                                    time_end_index = -1
                                    time_line_type = None
                                    time_end_type = ''
                                    break

                    # TIMELINE 2: Program Modify through natural language
                    # 一开始先找type==nl2jswithContext-start
                    # 接下去找第一个遇到的type==js2flow-finished，timeline=nl2jswithContext-start--js2flow-finished
                    if type_values[i] == 'nl2jswithContext-start' and time_start == -1 and time_end == -1:
                        if i > 1:
                            time_start = time_values[i - 1]
                            time_start_index = i - 1
                            time_start_type = type_values[i - 1]
                        else:
                            time_start = time_values[i]
                            time_start_index = i
                            time_start_type = 'nl2jswithContext-start'

                        for j in range(i, len(type_values)):
                            if type_values[j] == 'js2flow-finished':
                                time_end = time_values[j]
                                time_end_index = j
                                time_end_type = 'js2flow-finished'
                                time_line = timeCalculate(time_start, time_end)
                                time_line_type = 'TIMELINE 2: Program Modify through natural language'
                                if time_line_type:
                                    time_line_list.append(
                                        {'time_start': time_start, 'time_start_index': time_start_index,
                                         'time_start_type': time_start_type,
                                         'time_end': time_end, 'time_end_index': time_end_index,
                                         'time_end_type': time_end_type,
                                         'time_line': time_line, 'time_line_type': time_line_type})
                                    print({'time_start': time_start, 'time_start_index': time_start_index,
                                           'time_start_type': time_start_type,
                                           'time_end': time_end, 'time_end_index': time_end_index,
                                           'time_end_type': time_end_type,
                                           'time_line': time_line, 'time_line_type': time_line_type})
                                    time_start = -1
                                    time_start_index = -1
                                    time_start_type = ''
                                    time_end = -1
                                    time_end_index = -1
                                    time_line_type = None
                                    time_end_type = ''
                                    break

                    # TIMELINE 3: Program Modify through flowchart editing
                    # 一开始先找type==flow2js-start，然后返回去找前面一行的type==nodeUpdate || nodeAdd
                    # 接下去找第一个遇到的type==explainModifiedJS-finished，timeline=nodeUpdate--explainModifiedJS-finished
                    if type_values[i] == 'flow2js-start' and time_start == -1 and time_end == -1:
                        if i > 1:
                            time_start = time_values[i - 1]
                            time_start_index = i - 1
                            time_start_type = type_values[i - 1]

                        else:
                            time_start = time_values[i]
                            time_start_index = i
                            time_start_type = 'flow2js-start'

                        for j in range(i, len(type_values)):
                            if type_values[j] == 'explainModifiedJS-finished':
                                time_end = time_values[j]
                                time_end_index = j
                                time_end_type = 'explainModifiedJS-finished'
                                time_line = timeCalculate(time_start, time_end)
                                time_line_type = 'TIMELINE 3: Program Modify through flowchart editing'
                                if time_line_type:
                                    time_line_list.append(
                                        {'time_start': time_start, 'time_start_index': time_start_index,
                                         'time_start_type': time_start_type,
                                         'time_end': time_end, 'time_end_index': time_end_index,
                                         'time_end_type': time_end_type,
                                         'time_line': time_line, 'time_line_type': time_line_type})
                                    print({'time_start': time_start, 'time_start_index': time_start_index,
                                           'time_start_type': time_start_type,
                                           'time_end': time_end, 'time_end_index': time_end_index,
                                           'time_end_type': time_end_type,
                                           'time_line': time_line, 'time_line_type': time_line_type})
                                    time_start = -1
                                    time_start_index = -1
                                    time_start_type = ''
                                    time_end = -1
                                    time_end_index = -1
                                    time_line_type = None
                                    time_end_type = ''
                                    break
                        time_start = -1
                        time_start_index = -1
                        time_start_type = ''
                        time_end = -1
                        time_end_index = -1
                        time_line_type = None
                        time_end_type = ''

                    # TIMELINE 4: Debug/Modify by Magic Modfiy
                    # 一开始先找type==magicModify-start，然后返回去找前面一行的type==nodeClick的
                    # 接下去找第一个遇到的type==magicModifyPhase-finished
                    # if找到了，那就继续往下找第一个type==js2flow-finished，timeline=nodeClick--js2flow-finished
                    # else没找到，就找第一个遇到的type==magicModify-finished，timeline=nodeClick--magicModify-finished
                    if type_values[i] == 'magicModify-start' and time_start == -1 and time_end == -1:
                        if i > 1:
                            time_start = time_values[i - 1]
                            time_start_index = i - 1
                            time_start_type = type_values[i - 1]
                        else:
                            time_start = time_values[i]
                            time_start_index = i
                            time_start_type = 'magicModify-start'
                        # print(time_start, time_start_index, time_start_type)

                        for j in range(i + 1, len(type_values)):
                            if type_values[j] == 'magicModify-finished':
                                time_end = time_values[j]
                                time_end_index = j
                                time_end_type = 'magicModify-finished'
                                time_line = timeCalculate(time_start, time_end)
                                time_line_type = 'TIMELINE 4: Debug/Modify by Magic Modfiy'

                            if type_values[j] == 'magicModify-start' and time_line_type:  # 中间有穿插了magicModify-start
                                break

                            if type_values[j] == 'magicModifyPhase-finished':
                                for k in range(j, len(type_values)):
                                    if type_values[k] == 'js2flow-finished':
                                        time_end = time_values[k]
                                        time_end_index = k
                                        time_end_type = 'js2flow-finished'
                                        time_line = timeCalculate(time_start, time_end)
                                        time_line_type = 'TIMELINE 4: Debug/Modify by Magic Modfiy'
                                        break
                                break

                        if time_line_type:
                            time_line_list.append({'time_start': time_start, 'time_start_index': time_start_index,
                                                   'time_start_type': time_start_type,
                                                   'time_end': time_end, 'time_end_index': time_end_index,
                                                   'time_end_type': time_end_type,
                                                   'time_line': time_line, 'time_line_type': time_line_type})
                            print({'time_start': time_start, 'time_start_index': time_start_index,
                                   'time_start_type': time_start_type,
                                   'time_end': time_end, 'time_end_index': time_end_index,
                                   'time_end_type': time_end_type,
                                   'time_line': time_line, 'time_line_type': time_line_type})
                            time_start = -1
                            time_start_index = -1
                            time_start_type = ''
                            time_end = -1
                            time_end_index = -1
                            time_line_type = None
                            time_end_type = ''

                print(time_line_list)
                # 补全缺失掉的nodeClick的时间间隔
                if len(time_line_list) > 0:
                    # print(time_values[0])
                    time_line_list = missingTime(time_line_list, time_values[0], time_values[-1], len(type_values)-1)
                    print("补全之后：", time_line_list)
                    draw_time_line_list = processedDrawData(user_no, task_no, time_line_list)
                    txtFile.write(str(draw_time_line_list) + "\n")  # 写入数据并换行
                    # 将数据写入excel表格
            print()


def visualData():
    # categories = ['TIMELINE 0: nodeClick或者其他操作',
    #           'TIMELINE 1: Service Program Authoring through Natural Language',
    #           'TIMELINE 2: Program Modify through natural language',
    #           'TIMELINE 3: Program Modify through flowchart editing',
    #           'TIMELINE 4: Debug/Modify by Magic Modfiy']  # 类别
    # 示例数据
    categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
    values1 = [15, 20, 25, 10]
    values2 = [10, 25, 15, 30]
    values3 = [5, 15, 30, 20]

    # 创建堆叠条形图
    fig, ax = plt.subplots()

    # 设置条形图的位置和高度
    bar_height = 0.35
    bar_positions = np.arange(len(categories))

    # 绘制每个类别的条形图
    ax.barh(bar_positions, values1, bar_height, label='Value 1')
    ax.barh(bar_positions, values2, bar_height, left=values1, label='Value 2')
    ax.barh(bar_positions, values3, bar_height, left=np.add(values1, values2), label='Value 3')

    # 设置y轴标签和标题
    ax.set_ylabel('Categories')
    ax.set_xlabel('Values')
    ax.set_title('Stacked Horizontal Bar Chart')

    # 设置y轴刻度标签
    ax.set_yticks(bar_positions)
    ax.set_yticklabels(categories)

    # 设置图例
    ax.legend([])

    # 显示图形
    plt.show()


# def visualData_1(data):
#     # 展示每个用户的4个task的数据
#     # 创建空的DataFrame
#     # 创建空的DataFrame
#     df = pd.DataFrame()
#     print("visual data: ", data)
#     # 遍历每个数据
#     for group_data in data:
#         # print("group data: ", group_data)
#         user_no = group_data['user_no']
#         task_no = group_data['task_no']
#         drawDataTimeLine = group_data['drawDataTimeLine']
#         drawDataTimeLineType = group_data['drawDataTimeLineType']
#
#         # 创建每个数据的DataFrame
#         df_group = pd.DataFrame({'time_line': drawDataTimeLine, 'time_line_type': drawDataTimeLineType})
#
#         # 添加分组信息
#         df_group['user_no'] = user_no
#         df_group['task_no'] = task_no
#
#         # print("df_group: ", df_group)
#         # 将每个数据的DataFrame添加到总体DataFrame中
#         df = pd.concat([df, df_group])
#
#     # 按照user_no分组并绘制图形
#     grouped = df.groupby('user_no')
#     colors = {'TIMELINE 0: nodeClick': 'red', 'TIMELINE 1: Service Program Authoring through Natural Language': 'blue',
#               'TIMELINE 2: Program Modify through natural language': 'green',
#               'TIMELINE 3: Program Modify through flowchart editing': 'orange',
#               'TIMELINE 4: Debug/Modify by Magic Modify': 'purple'}
#
#     for user_no, group_df in grouped:
#         plt.figure(figsize=(10, 6))
#         plt.title(f'User {user_no} Timeline')
#         print("group_df_: ", group_df)
#         x = range(len(group_df))
#         print("len:group_df: ", x)
#         bottom = None
#         for index, row in group_df.iterrows():
#             time_line_type = row['time_line_type']
#             color = colors.get(time_line_type, 'gray')
#             if bottom is None:
#                 plt.bar(x, row['time_line'], color=color, label=time_line_type)
#                 bottom = float(row['time_line'])
#             else:
#                 plt.bar(x, row['time_line'], bottom=bottom, color=color, label=time_line_type)
#                 bottom += float(row['time_line'])

        # # 设置图例
        # plt.legend()
        #
        # # 显示图形
        # plt.show()


def visualData_1(data):
    # 按照'user_no'进行分组
    grouped_data = groupby(data, key=lambda x: x['user_no'])
    # 遍历分组后的数据
    for key, group in grouped_data:
        print(f"user_no: {key}")
        zero_vector_length = 0
        each_user_timeline_concat = []
        group_list = list(group)  # 将 group 转换为列表
        for item in group_list:
            # print(item)
            each_user_timeline_concat.extend(item['drawDataTimeLineType'])
            # 计算零向量的长度
            zero_vector_length += len(item['drawDataTimeLineType'])
        print(zero_vector_length)
        result = []
        # for sublist in group_list:
        for i in range(len(group_list)):
            sublist = group_list[i]
            index = group_list.index(sublist)
            # print("index: ", group_list.index(sublist))
            zero_vector = [0] * zero_vector_length
            if i >= 1:
                zero_vector[index * len(group_list[i-1]['drawDataTimeLineType']):(index + 1) * len(sublist['drawDataTimeLineType'])] = [float(item) for item in sublist['drawDataTimeLine']]
            else:
                zero_vector[0:(index + 1) * len(sublist['drawDataTimeLineType'])] = [float(item) for item in sublist['drawDataTimeLine']]

            result.append(zero_vector)

        print(result)
        print(len(result))
        for lis in result:
            print(len(lis))

        # # 原始二维数组
        # array_2d = np.array(result)
        #
        # # 转换维度
        # array_2d_transposed = np.transpose(array_2d)
        #
        # print("原始二维数组:")
        # print(array_2d)
        # print("转换维度后的数组:")
        # print(array_2d_transposed)


def visualData_2(data):
    plt.figure(figsize=(10, 6))
    plt.title(f'All Timeline')

    colors = {'TIMELINE 0: nodeClick或者其他操作': 'red', 'TIMELINE 1: Service Program Authoring through Natural Language': 'blue',
              'TIMELINE 2: Program Modify through natural language': 'green',
              'TIMELINE 3: Program Modify through flowchart editing': 'orange',
              'TIMELINE 4: Debug/Modify by Magic Modfiy': 'purple'}

    # 创建堆积柱形图
    # for i in range(len(data)):
    #     bottom = 0
    #     for j in range(len(data[i]['drawDataTimeLine'])):
    #         plt.bar([i], [float(data[i]['drawDataTimeLine'][j])], bottom=bottom, label=data[i]['drawDataTimeLineType'][j])
    #         bottom += float(data[i]['drawDataTimeLine'][j])

    # 创建堆叠条形图
    fig, ax = plt.subplots(figsize=(10, 10))

    # 设置条形图的位置和高度
    bar_height = 0.35
    for i in range(len(data)):
        left = 0
        for j in range(len(data[i]['drawDataTimeLine'])):
            # 绘制每个类别的条形图
            ax.barh([i], [float(data[i]['drawDataTimeLine'][j])], left=left, label=data[i]['drawDataTimeLineType'][j], color=colors[data[i]['drawDataTimeLineType'][j]])
            left += float(data[i]['drawDataTimeLine'][j])

    # 设置y轴标签和标题
    # ax.set_ylabel('Categories')
    # ax.set_xlabel('Values')
    # ax.set_title('Stacked Horizontal Bar Chart')

    # # 设置y轴刻度标签
    # ax.set_yticks(data)
    # 去掉y轴刻度
    ax.set_yticks([])
    # ax.set_yticklabels(categories)

    # 设置图例
    # 设置自定义图例项
    custom_legend = [Line2D([], [], color='red', label='TIMELINE 0: nodeClick'),
                     Line2D([], [], color='blue', label='TIMELINE 1: Authoring'),
                     Line2D([], [], color='green', label='TIMELINE 2: natural language'),
                     Line2D([], [], color='orange', label='TIMELINE 3: flowchart editing'),
                     Line2D([], [], color='purple', label='TIMELINE 4: Magic Modfiy'),]

    # 设置图例
    ax.legend(handles=custom_legend)
    # ax.legend()

    # 显示图形
    plt.show()


def concatTask(data):
    # 将用户在不同task下的多项数据拼接合并
    # 处理用户在同一个task下有多项数据
    # 按照'user_no'进行分组
    newData = []
    grouped_data = groupby(data, key=lambda x: x['user_no'])
    # 遍历分组后的数据
    for key, group in grouped_data:
        print(f"user_no: {key}")
        group_list = list(group)  # 将 group 转换为列表
        group_task = groupby(group_list, key=lambda x: x['task_no'])
        for key_t, task in group_task:
            task_list = list(task)
            # print(key_t, task_list)
            # if len(task_list) > 1:  # 预测试T0的数据被包含
            if task_list[0]['task_no'] != 'T0':
                if len(task_list) > 1:  # 让预测试T0的数据不被包含
                    # print(len(task_list))
                    # 将同一个task下的几个数据文件拼接起来
                    user_no = task_list[0]['user_no']
                    task_no = task_list[0]['task_no']
                    drawDataTimeLine = []
                    drawDataTimeLineType = []
                    for i in range(len(task_list)):
                        drawDataTimeLine.extend(task_list[i]['drawDataTimeLine'])
                        drawDataTimeLine.extend([50])  # gap时间为100

                        drawDataTimeLineType.extend(task_list[i]['drawDataTimeLineType'])
                        drawDataTimeLineType.extend(['TIMELINE 5: GAP in one task'])
                    if drawDataTimeLineType[-1] == 'TIMELINE 5: GAP in one task':
                        drawDataTimeLine = drawDataTimeLine[:-1]
                        drawDataTimeLineType = drawDataTimeLineType[:-1]
                    concatOne = {'user_no': user_no, 'task_no': task_no, 'drawDataTimeLine': drawDataTimeLine, 'drawDataTimeLineType': drawDataTimeLineType}
                    # print(concatOne)
                    newData.append(concatOne)
                else:
                    newData.append(task_list[0])
    return newData


def concatUser(data):
    # 将用户在不同task下的多项数据拼接合并
    # 处理用户在同一个task下有多项数据
    # 按照'user_no'进行分组
    newData = []
    grouped_data = groupby(data, key=lambda x: x['user_no'])
    # 遍历分组后的数据
    for key, group in grouped_data:
        print(f"user_no: {key}")
        group_list = list(group)
        user_no = group_list[0]['user_no']
        task_no = group_list[0]['task_no']
        drawDataTimeLine = []
        drawDataTimeLineType = []
        for i in range(len(group_list)):
            drawDataTimeLine.extend(group_list[i]['drawDataTimeLine'])
            drawDataTimeLine.extend([40])  # gap时间为100

            drawDataTimeLineType.extend(group_list[i]['drawDataTimeLineType'])
            drawDataTimeLineType.extend(['TIMELINE 6: Task dividing line'])
        if drawDataTimeLineType[-1] == 'TIMELINE 6: Task dividing line':
            drawDataTimeLine = drawDataTimeLine[:-1]
            drawDataTimeLineType = drawDataTimeLineType[:-1]
        concatOne = {'user_no': user_no, 'task_no': task_no, 'drawDataTimeLine': drawDataTimeLine, 'drawDataTimeLineType': drawDataTimeLineType}
        print(concatOne)
        newData.append(concatOne)
    return newData


def visualData_user(data):
    # 按照'user_no'进行分组
    grouped_data = groupby(data, key=lambda x: x['user_no'])
    # 遍历分组后的数据
    for key, group in grouped_data:
        print(f"user_no: {key}")
        group_list = list(group)  # 将 group 转换为列表
        # print(group_list)
        colors = {'TIMELINE 0: nodeClick或者其他操作': 'red',
                  'TIMELINE 1: Service Program Authoring through Natural Language': 'blue',
                  'TIMELINE 2: Program Modify through natural language': 'green',
                  'TIMELINE 3: Program Modify through flowchart editing': 'orange',
                  'TIMELINE 4: Debug/Modify by Magic Modfiy': 'purple',
                  'TIMELINE 5: GAP in one task': '#EDEDED'}

        # 创建堆叠条形图
        fig, ax = plt.subplots(figsize=(10, 5))

        # 设置条形图的位置和高度
        bar_height = 0.35  # 间隙
        for i in range(len(group_list)):
            left = 0
            print(group_list[i])
            for j in range(len(group_list[i]['drawDataTimeLine'])):
                # 绘制每个类别的条形图
                ax.barh([i], [float(group_list[i]['drawDataTimeLine'][j])], bar_height, left=left, label=group_list[i]['drawDataTimeLineType'][j],
                        color=colors[group_list[i]['drawDataTimeLineType'][j]])
                left += float(group_list[i]['drawDataTimeLine'][j])

        # 设置y轴刻度标签
        ax.set_yticklabels(['', 'T0', '', 'T1', '', 'T2', '', 'T3'])
        ax.set_title(f"user_no: {key}")

        # 设置自定义图例项
        custom_legend = [Line2D([], [], color='red', label='nodeClick'),
                         Line2D([], [], color='blue', label='Authoring'),
                         Line2D([], [], color='green', label='Natural Language'),
                         Line2D([], [], color='orange', label='Flowchart Editing'),
                         Line2D([], [], color='purple', label='Magic Modfiy'),
                         Line2D([], [], color='#EDEDED', label='GAP in one task'),]

        # 设置图例
        ax.legend(handles=custom_legend, fontsize=7)

        # 显示图形
        plt.show()


def visualData_all_user(data):
    colors = {'TIMELINE 0: nodeClick或者其他操作': 'red',
              'TIMELINE 1: Service Program Authoring through Natural Language': 'blue',
              'TIMELINE 2: Program Modify through natural language': 'green',
              'TIMELINE 3: Program Modify through flowchart editing': 'orange',
              'TIMELINE 4: Debug/Modify by Magic Modfiy': 'purple',
              'TIMELINE 5: GAP in one task': '#B9B9B9',
              'TIMELINE 6: Task dividing line': '000000'}

    # 创建堆叠条形图
    fig, ax = plt.subplots(figsize=(17, 10))

    # 设置条形图的位置和高度
    bar_height = 0.35  # 间隙
    user_list = []
    for i in range(len(data)):
        left = 0
        print(data[i])
        # user_list.append('')
        user_list.append(data[i]['user_no'])
        for j in range(len(data[i]['drawDataTimeLine'])):
            # 绘制每个类别的条形图
            if data[i]['drawDataTimeLineType'][j] == 'TIMELINE 6: Task dividing line':
                bar_height = 0.8
            elif data[i]['drawDataTimeLineType'][j] == 'TIMELINE 5: GAP in one task':
                bar_height = 0.6
            else:
                bar_height = 0.45

            ax.barh([i], [float(data[i]['drawDataTimeLine'][j])], bar_height, left=left, label=data[i]['drawDataTimeLineType'][j],
                    color=colors[data[i]['drawDataTimeLineType'][j]])
            left += float(data[i]['drawDataTimeLine'][j])

    # 设置y刻度和标签
    yticks = range(len(user_list))
    yticklabels = user_list
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    # ax.set_title(f"all users")

    ax.set_xlabel('Duration(s)')
    ax.set_ylabel('User')

    # 设置自定义图例项
    custom_legend = [Line2D([], [], color='red', label='NodeClick'),
                     Line2D([], [], color='blue', label='Authoring'),
                     Line2D([], [], color='green', label='Natural Language'),
                     Line2D([], [], color='orange', label='Flowchart Edit'),
                     Line2D([], [], color='purple', label='Magic Modify'),
                     Line2D([], [], color='#EDEDED', label='Gap of Multiple Attempts on One Task'),
                     Line2D([], [], color='#000000', label='Task1,2,3 Dividing Line')]

    # 设置图例
    ax.legend(handles=custom_legend, fontsize=10)

    # 显示图形
    plt.show()


def eachTimeline(data):
    # 创建一个新的工作簿
    workbook = xlwt.Workbook()
    # 添加一个工作表
    sheet = workbook.add_sheet('Sheet1')
    sheet.write(0, 0, 'user_no')
    sheet.write(0, 1, 'task_no')
    sheet.write(0, 2, 'timeline0:nodeClick')
    sheet.write(0, 3, 'timeline1:Authoring')
    sheet.write(0, 4, 'timeline2:natural language')
    sheet.write(0, 5, 'timeline3:flowchart editing')
    sheet.write(0, 6, 'timeline4:Magic Modify')
    sheet.write(0, 7, 'timeline5:Gap of Multiple Attempts on One Task（次）')

    # 计算每个用户在完成每个任务时的timeline类型时长统计情况
    timeline0 = 'TIMELINE 0: nodeClick或者其他操作'
    timeline1 = 'TIMELINE 1: Service Program Authoring through Natural Language'
    timeline2 = 'TIMELINE 2: Program Modify through natural language'
    timeline3 = 'TIMELINE 3: Program Modify through flowchart editing'
    timeline4 = 'TIMELINE 4: Debug/Modify by Magic Modfiy'
    timeline5 = 'TIMELINE 5: GAP in one task'
    for i in range(len(data)):
        print(data[i])
        # timelineTotal = []
        timeline0_total = 0
        timeline1_total = 0
        timeline2_total = 0
        timeline3_total = 0
        timeline4_total = 0
        timeline5_total = 0
        for j in range(len(data[i]['drawDataTimeLineType'])):
            if data[i]['drawDataTimeLineType'][j] == timeline0:
                timeline0_total += float(data[i]['drawDataTimeLine'][j])
            elif data[i]['drawDataTimeLineType'][j] == timeline1:
                timeline1_total += float(data[i]['drawDataTimeLine'][j])
            elif data[i]['drawDataTimeLineType'][j] == timeline2:
                timeline2_total += float(data[i]['drawDataTimeLine'][j])
            elif data[i]['drawDataTimeLineType'][j] == timeline3:
                timeline3_total += float(data[i]['drawDataTimeLine'][j])
            elif data[i]['drawDataTimeLineType'][j] == timeline4:
                timeline4_total += float(data[i]['drawDataTimeLine'][j])
            elif data[i]['drawDataTimeLineType'][j] == timeline5:
                timeline5_total += float(data[i]['drawDataTimeLine'][j])

        # 向单元格写入数据
        sheet.write(i+1, 0, data[i]['user_no'])
        sheet.write(i+1, 1, data[i]['task_no'])
        sheet.write(i+1, 2, timeline0_total)
        sheet.write(i + 1, 3, timeline1_total)
        sheet.write(i + 1, 4, timeline2_total)
        sheet.write(i + 1, 5, timeline3_total)
        sheet.write(i + 1, 6, timeline4_total)
        sheet.write(i + 1, 7, timeline5_total/50)
    # 保存工作簿
    workbook.save('new_new_每个用户在完成每个任务时的timeline类型时长统计情况.xls')


def computeAverage():
    # 读取 Excel 表格数据
    data = pd.read_excel('new_new_每个用户在完成每个任务时的timeline类型时长统计情况.xls')

    # 按照 'user_no' 进行分组，并计算 'timeline0:nodeClick' 的平均值和总和
    # grouped_data = data.groupby('user_no')['timeline0:nodeClick'].agg(['mean', 'sum'])
    # grouped_data = list(data.groupby('user_no')['timeline0:nodeClick'].agg(['mean'])['mean'])

    # grouped_data = data.groupby('user_no')['timeline1:Authoring'].agg(['mean', 'sum'])
    grouped_data = list(data.groupby('user_no')['timeline1:Authoring'].agg(['mean'])['mean'])

    # grouped_data = data.groupby('user_no')['timeline2:natural language'].agg(['mean', 'sum'])
    # grouped_data = list(data.groupby('user_no')['timeline2:natural language'].agg(['mean'])['mean'])

    # grouped_data = data.groupby('user_no')['timeline3:flowchart editing'].agg(['mean', 'sum'])
    # grouped_data = list(data.groupby('user_no')['timeline3:flowchart editing'].agg(['mean'])['mean'])

    # grouped_data = data.groupby('user_no')['timeline4:Magic Modify'].agg(['mean', 'sum'])
    # grouped_data = list(data.groupby('user_no')['timeline4:Magic Modify'].agg(['mean'])['mean'])

    # grouped_data = data.groupby('user_no')['timeline5:Gap of Multiple Attempts on One Task（次）'].agg(['mean', 'sum'])
    # grouped_data = list(data.groupby('user_no')['timeline5:Gap of Multiple Attempts on One Task（次）'].agg(['mean'])['mean'])

    for one_mean in grouped_data:
        print(one_mean)
    # 打印结果
    print(grouped_data)


if __name__ == '__main__':
    # # 1.编码处理为gbk
    # folder_path = "02rawCSVData"  # 替换为实际的文件夹路径
    # process_csv_files(folder_path)


    # # 2.将每个task下面的csv文件按照time字段拼接
    # folder_path = "02rawCSVData"  # 替换为实际的文件夹路径
    # concatenate_csv_files(folder_path)


    # 3.分析每个task下面合并之后的csv文件
    # folder_path = "02rawCSVData"  # 替换为实际的文件夹路径
    # extract_fields(folder_path)


    # # 4.切分时间段，splitTimeline
    # folder_path = "02rawCSVData"  # 替换为实际的文件夹路径
    # # 指定输出文件路径
    # output_file = "new_new_drawData.txt"
    # # 打开文件并逐行写入数据
    # with open(output_file, 'w') as file:
    #     splitTimeline(folder_path, file)
    #     file.close()


    # 5.事件顺序堆叠图可视化visual
    input_file = "new_new_drawData.txt"
    # input_file = "new_drawData.txt"
    # input_file = "drawData.txt"
    # 逐行读取文件并处理数据
    data_list = []
    with open(input_file, 'r') as file:
        for line in file:
            line = eval(line.strip())  # 去除行尾的换行符和空白字符
            data_list.append(line)

    # visualData_2(data_list)
    # 展示每个用户的4个task的数据
    # visualData_1(data_list)

    new_task_data_list = concatTask(data_list)
    # 对每个用户画一张图，展示完成各任务的情况
    # visualData_user(new_data_list)

    # 对所有用户画一张图，展示完成所有任务的情况
    new_user_data_list = concatUser(new_task_data_list)
    visualData_all_user(new_user_data_list)

    #
    # 6.计算每个用户在每个task下面包含的timeline的类型及其分别的总时长。
    # eachTimeline(new_task_data_list)

    # # 7.计算每个用户在完成所有任务时用的几个timeline的平均数和总时长。
    # computeAverage()

