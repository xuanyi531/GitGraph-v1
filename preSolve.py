#!coding: utf-8
import subprocess
import os
import re
import pickle

import filetypes

pkl_file = open('API.pkl', 'rb')
classdic = pickle.load(pkl_file)


def check_file_type(filename, typelist):
    file_type = os.path.splitext(filename)[1]
    if file_type == "":
        return False

    file_type = file_type[1:]
    if file_type in typelist:
        return True

    return False


def is_pic(filename):
    return check_file_type(filename, filetypes.PICS)


def is_audio(filename):
    return check_file_type(filename, filetypes.AUDIOS)


def is_video(filename):
    return check_file_type(filename, filetypes.VIDEOS)


def is_custom(filename):
    return check_file_type(filename, filetypes.CUSTOM)


def get_commit(project_root):
    cwd = os.getcwd()
    os.chdir(project_root)
    output = subprocess.check_output("git log ", shell=True)
    output1 = subprocess.check_output("git log --pretty=oneline", shell=True)
    os.chdir(cwd)

    output = str(output, "utf-8")
    output1 = str(output1, "utf-8")

    pattern = re.compile(r"[a-z0-9]{40}")
    result = re.findall(pattern, output)

    pattern_author = re.compile(r"Author: (.*)")
    authors = re.findall(pattern_author, output)

    pattern_date = re.compile(r"Date: {3}(.*)")
    dates = re.findall(pattern_date, output)

    lines = filter(None, output1.splitlines())
    details = []
    for line in lines:
        details.append(line[41:])

    return result, authors, dates, details


def get_filename(project_root, id, picOps, audOps, vidOps, cusOps):

    cwd = os.getcwd()
    os.chdir(project_root)
    # output = subprocess.check_output("git diff " + id + " --stat", shell=True)
    output = subprocess.check_output("git diff " + id, shell=True)
    os.chdir(cwd)

    try:
        output = str(output, "utf-8")
    except(UnicodeDecodeError):
        return []
    """
    lines = output.splitlines()[:-2]
    files = []
    for line in lines:
        files.append(line.split("|")[0].strip(" "))
        
    "diff --git a/README.md b/README.md"
    """
    pattern = re.compile(r"diff --git a/(.*) b/")
    files = re.findall(pattern, output)

    if picOps:
        files = filter(lambda x: not is_pic(x), files)
    if audOps:
        files = filter(lambda x: not is_audio(x), files)
    if vidOps:
        files = filter(lambda x: not is_video(x), files)
    if cusOps:
        files = filter(lambda x: not is_custom(x), files)

    return list(files)


def remove_rename(files):
    t = "=>"
    # 遍历拷贝的list，操作原始的list
    for item in files[:]:
        if t in item:
            files.remove(item)

    return files


def parse_file(file_content):
    class_pattern = re.compile(r"(class +\w+)")  # 匹配类名
    class_list = re.findall(class_pattern, file_content)

    method_pattern = re.compile(r"((\w+\(([A-Za-z0-9_.]+ +[A-Za-z0-9_.]+)*( +, +[A-Za-z0-9_.]+ +[A-Za-z0-9_.]+)*\)).*\{)")  # 匹配函数名
    method_list = re.findall(method_pattern, file_content)
    method_list = [x[1] for x in method_list if "()" not in x[0]]  # 过滤内部类
    # print(method_list)

    import_pattern = re.compile(r"import (\S+);")
    import_list = re.findall(import_pattern, file_content)

    return class_list, method_list, import_list


def get_change_of_file(class_list, method_list, output):
    lines = output.splitlines()
    class_number = 0
    method_number = 0
    class_line = []
    method_line = []
    change_lines = []
    for line_number, line in enumerate(lines):
        if line[0] == "+" or line[0] == "-":
            change_lines.append(line_number)
        if class_number < len(class_list) and class_list[class_number] in line:
            class_line.append(line_number)
            class_number += 1
            continue
        if method_number < len(method_list) and method_list[method_number] in line:
            method_line.append(line_number)
            method_number += 1
            continue
    return lines, class_line, method_line, change_lines


def get_change_of_API(import_list, line):
    global classdic
    api_result = []
    pattern = re.compile(r"(\w+(\.\w+)*)\([A-Za-z0-9_.]*( +, +[A-Za-z0-9_.]+)*\)")
    apis = re.findall(pattern, line)
    apis = [x[0] for x in apis]
    apis = [x for x in apis if x not in ["if", "for", "while", "super", "Log.d", "getResources",
                                         "getWidth", "getHeight","setHeight", "setWidth"]]
    for aclass in import_list:
        if aclass in classdic:
            method_of_class = classdic[aclass]['Method']
            for x in apis:
                if x in method_of_class:
                    api_result.append(aclass + "." + x)
                elif 'SuperClass' in classdic[aclass]:
                    superclass = classdic[aclass]['SuperClass']
                    if superclass in classdic:
                        res = digui(superclass, x)
                        if res and res not in api_result: api_result.append(res)
    # if api_result: print(api_result)
    return api_result


def digui(classname, x):
    global classdic
    if x in classdic[classname]['Method']:
        return classname + "." + x
    elif 'SuperClass' in classdic[classname]:
        return digui(classdic[classname]['SuperClass'], x)
    else:
        return None


def get_change_of_class(lines, class_lines, method_lines, change_lines, class_list, method_list, method_of_class, import_list):
    changes = {}
    for item in change_lines:
        if item < class_lines[0]:
            continue  # 直接丢掉
        class_list_len = len(class_lines)

        for i in range(class_list_len):  # 遍历类
            class_name_now = class_list[i]

            if (i < class_list_len - 1 and class_lines[i] <= item < class_lines[i+1]) or\
                    (i == class_list_len - 1 and item >= class_lines[i]):
                if class_name_now not in changes:
                    changes[class_name_now] = {}  # class_list存的是类名
                    changes[class_name_now]['definition'] = []
                    changes[class_name_now]['method'] = {}
                flag = 0
                for j in range(len(method_of_class)):
                    if method_of_class[j] == class_name_now:  # 如果方法对应的类名与当前类名匹配
                        if j < len(method_of_class) - 1 and method_lines[j] <= item < method_lines[j + 1] or \
                                                 j == len(method_of_class) - 1 and item >= method_lines[j]:
                            if method_list[j] not in changes[class_name_now]['method']:
                                changes[class_name_now]['method'][method_list[j]] = {}
                                changes[class_name_now]['method'][method_list[j]]['lines'] = []
                                changes[class_name_now]['method'][method_list[j]]['addAPI'] = []
                                changes[class_name_now]['method'][method_list[j]]['removeAPI'] = []

                            changes[class_name_now]['method'][method_list[j]]['lines'].append(lines[item])

                            if '+' == lines[item][0]:
                                changes[class_name_now]['method'][method_list[j]]['addAPI'] += get_change_of_API(import_list, lines[item])
                                changes[class_name_now]['method'][method_list[j]]['addAPI'] = list(set(changes[class_name_now]['method'][method_list[j]]['addAPI']))
                            elif '-' == lines[item][0]:
                                changes[class_name_now]['method'][method_list[j]]['removeAPI'] += get_change_of_API(import_list, lines[item])
                                changes[class_name_now]['method'][method_list[j]]['removeAPI'] = list(set(changes[class_name_now]['method'][method_list[j]]['removeAPI']))
                            flag = 1
                            break
                if flag == 0:
                    changes[class_name_now]['definition'].append(lines[item])
                    break

    return changes


# git diff b55e1c1bae45ce7d05fd0a5f1e9e39d9610f65fd app/src/main/java/onboarding/yahoo/com/yahoonewsonboarding/MainActivity.java


def get_change(project_root, commit_id, file_name):
    cwd = os.getcwd()
    os.chdir(project_root)
    output = subprocess.check_output("git diff -U10000 " + commit_id + " " + file_name, shell=True)
    os.chdir(cwd)
    output = str(output, "utf-8")
    class_list, method_list, import_list = parse_file(output)
    lines, class_lines, method_lines, change_lines = get_change_of_file(class_list, method_list, output)
    """
    class_list: 类名
    method_list: 方法名
    method_of_class: method对应的类名
    import_list: import的类名
    """
    if class_lines == []:
        return [], [], [], {}
    method_of_class = []
    len_of_class = len(class_lines)
    for i in range(len(method_lines)):
        if method_lines[i] < class_lines[0]:
            method_of_class.append(None)
            continue
        if method_lines[i] > class_lines[len_of_class - 1]:
            method_of_class.append(class_list[len_of_class - 1])
            continue
        else:
            for j in range(len_of_class):
                if j != len_of_class - 1 and class_lines[j] < method_lines[i] < class_lines[j + 1]:
                    method_of_class.append(class_list[j])
                    break
                elif j == len_of_class - 1:
                    print("error!")

    changes = get_change_of_class(lines, class_lines, method_lines, change_lines, class_list, method_list, method_of_class, import_list)

    # 修改method_list
    method_list2 = []
    for i in range(len(method_list)):
        method_list2.append(method_of_class[i] + ":" + method_list[i])

    return class_list, method_list, method_list2, changes


