# coding:utf-8
import re
import pickle

def extract_API():
    with open("./pics/current.txt") as f:
        file_content = f.read().splitlines()
    with open("./pics/system-current.txt") as f:
        file_content2 = f.read().splitlines()
    result = {}
    packagename = ""
    class_path = ""
    for line in file_content:
        if "package" in line and "{" in line:
            packagename = re.findall(r"package\s+(\S+)\s+{", line)[0]
            continue
        if "class" in line and "{" in line:
            classname = re.findall(r"class\s+(\S+)\s+", line)[0]
            if packagename == "android.graphics" and classname == "Canvas":
                print("bingo!")

            class_path = packagename + "." + classname
            result[class_path] = {}
            result[class_path]['Method'] = []
            if "extends" in line:
                father = re.findall(r"extends\s+(\S+)\s+", line)[0]
                result[class_path]['SuperClass'] = father
            continue
        if "method " in line and "(" in line:
            methodname = re.findall(r"\s(\w+)\(", line)[0]
            result[class_path]['Method'].append(methodname)
            continue

    for line in file_content2:
        if "package" in line and "{" in line:
            packagename = re.findall(r"package\s+(\S+)\s+{", line)[0]
            continue
        if "class" in line and "{" in line:
            classname = re.findall(r"class\s+(\S+)\s+", line)[0]
            class_path = packagename + "." + classname
            if class_path not in result:
                result[class_path] = {}
                result[class_path]['Method'] = []
            if "extends" in line:
                father = re.findall(r"extends\s+(\S+)\s+", line)[0]
                result[class_path]['SuperClass'] = father
            continue
        if "method " in line and "(" in line:
            methodname = re.findall(r"\s(\w+)\(", line)[0]
            result[class_path]['Method'].append(methodname)
            continue

    print(result)
    return result

result = extract_API()
output = open('API.pkl', 'wb')
pickle.dump(result, output)
output.close()
