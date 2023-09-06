import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from plotnine import *


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
    drawData = {"user_no":user_no, "task_no": task_no, "drawDataTimeLine": drawDataTimeLine, "drawDataTimeLineType": drawDataTimeLineType}
    print(drawData)
    return drawData


def missingTime(data):
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
                'time_line_type': 'TIMELINE 0: nodeClick'
            }
            # print(missing_record)
            data.append(missing_record)
        # 按照索引排序
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

                for i in range(len(type_values)):
                    if time_start != -1:
                        print(type_values[i], time_start, time_end)
                    # TIMELINE 1: Service Program Authoring through Natural Language
                    # 一开始先找type==authoringNEW-start (start)
                    # 接下去找第一个遇到的type==js2flow-finished，timeline=authoringNEW-start--js2flow-finished
                    if type_values[i] == 'start':
                        time_start = time_values[i]
                        time_start_index = i
                        time_start_type = 'start'

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
                    time_line_list = missingTime(time_line_list)
                    draw_time_line_list = processedDrawData(user_no, task_no, time_line_list)
                    txtFile.write(str(draw_time_line_list) + "\n")  # 写入数据并换行

            print()


def visualData():
    # categories = ['TIMELINE 0: nodeClick或者其他操作',
    #           'TIMELINE 1: Service Program Authoring through Natural Language',
    #           'TIMELINE 2: Program Modify through natural language',
    #           'TIMELINE 3: Program Modify through flowchart editing',
    #           'TIMELINE 4: Debug/Modify by Magic Modfiy']  # 类别
    colors = ['#1D2F6F', '#8390FA', '#6EAF46', '#FAC748', '#000000']  # 类别对应颜色
    labels = ['TIMELINE 0', 'TIMELINE 1', 'TIMELINE 2', 'TIMELINE 3', 'TIMELINE 4']  # 类别别名

    # 数据
    categories = ['TIMELINE 0', 'TIMELINE 1', 'TIMELINE 2', 'TIMELINE 3', 'TIMELINE 4']  # 类别别名

    # categories = ['Category 1', 'Category 2', 'Category 3']
    values1 = [20, 30, 25]
    values2 = [15, 25, 20]
    values3 = [10, 15, 12]

    # 创建一个numpy数组，表示每个值的起始位置
    start_values = np.zeros(len(categories))

    # 绘图
    plt.barh(categories, values1, label='Value 1', left=start_values)
    plt.barh(categories, values2, label='Value 2', left=start_values + values1)
    plt.barh(categories, values3, label='Value 3', left=start_values + values1 + values2)

    # 设置标签和标题
    plt.xlabel('Values')
    plt.ylabel('Categories')
    plt.title('Stacked Horizontal Bar Chart')

    # 添加图例
    plt.legend()

    # 显示图表
    plt.show()


def visualData_1(data):
    # 展示每个用户的4个task的数据
    # 创建空的DataFrame
    # 创建空的DataFrame
    df = pd.DataFrame()

    # 遍历每个数据
    for group_data in data:
        user_no = group_data['user_no']
        task_no = group_data['task_no']
        drawDataTimeLine = group_data['drawDataTimeLine']
        drawDataTimeLineType = group_data['drawDataTimeLineType']

        # 创建每个数据的DataFrame
        df_group = pd.DataFrame({'time_line': drawDataTimeLine, 'time_line_type': drawDataTimeLineType})

        # 添加分组信息
        df_group['user_no'] = user_no
        df_group['task_no'] = task_no

        # 将每个数据的DataFrame添加到总体DataFrame中
        df = pd.concat([df, df_group])

    # 按照user_no分组并绘制图形
    grouped = df.groupby('user_no')
    colors = {'TIMELINE 0: nodeClick': 'red', 'TIMELINE 1: Service Program Authoring through Natural Language': 'blue',
              'TIMELINE 2: Program Modify through natural language': 'green',
              'TIMELINE 3: Program Modify through flowchart editing': 'orange',
              'TIMELINE 4: Debug/Modify by Magic Modify': 'purple'}

    for user_no, group_df in grouped:
        plt.figure(figsize=(10, 6))
        plt.title(f'User {user_no} Timeline')
        x = range(len(group_df))
        bottom = None
        for index, row in group_df.iterrows():
            time_line_type = row['time_line_type']
            color = colors.get(time_line_type, 'gray')
            if bottom is None:
                plt.bar(x, row['time_line'], color=color, label=time_line_type)
                bottom = float(row['time_line'])
            else:
                plt.bar(x, row['time_line'], bottom=bottom, color=color, label=time_line_type)
                bottom += float(row['time_line'])

        # 设置图例
        plt.legend()

        # 显示图形
        plt.show()


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
    # output_file = "drawData.txt"
    # # 打开文件并逐行写入数据
    # with open(output_file, 'w') as file:
    #     splitTimeline(folder_path, file)
    #     file.close()


    # # 5.事件顺序堆叠图可视化visual
    input_file = "drawData.txt"
    # 逐行读取文件并处理数据
    data_list = []
    with open(input_file, 'r') as file:
        for line in file:
            line = eval(line.strip())  # 去除行尾的换行符和空白字符
            data_list.append(line)

    # 展示每个用户的4个task的数据
    visualData_1(data_list)

    # 展示所有用户的所有task的数据

    # 展示所有用户的task0的数据

    # 展示所有用户的task1的数据

    # 展示所有用户的task2的数据

    # 展示所有用户的task3的数据

