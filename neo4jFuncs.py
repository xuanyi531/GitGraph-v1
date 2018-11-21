# coding:utf-8
import hashlib
import os

from py2neo import Graph, Node, Relationship, NodeMatcher
import pickle

if_clear = True


def get_graph(commit_ids, authors, dates, details, file_map, file_change):

    global if_clear
    graph = Graph("http://localhost:7474", username="neo4j", password="2333")
    # if clear
    if if_clear:
        graph.delete_all()

    commit_count = 0
    last_commit = Node("Commit", name="start", count=commit_count)
    for i in range(len(commit_ids)):
        commit_count += 1
        commit_name = commit_ids[i]
        commit_node = Node("Commit", name=commit_name, count=commit_count)
        commit_node['developer'] = authors[i]
        commit_node['time'] = dates[i]
        commit_node['remark'] = details[i]
        graph.create(commit_node)
        commit_to_commit = Relationship(last_commit, "Next", commit_node)
        graph.create(commit_to_commit)

        files_of_commit = file_map[commit_name]
        for j in range(len(files_of_commit)):
            file_name = files_of_commit[j]
            node_name = hashlib.md5((commit_name + file_name).encode("utf-8")).hexdigest()
            file_type = os.path.splitext(file_name)[1][1:]
            file_node = Node("File", name=node_name, filename=file_name, file_type=file_type)

            if file_type == "java":
                change_of_file = file_change[node_name]
                if "class_list" in change_of_file:
                    file_node['class_list'] = change_of_file['class_list']
                    file_node['method_list'] = change_of_file['method_list']
                    graph.create(file_node)
                    commit_to_file = Relationship(commit_node, "Edit", file_node)
                    graph.create(commit_to_file)

                    # 建立file到class的节点
                    change_of_class = change_of_file['changes']

                    for class_name in change_of_class:
                        change_of_class1 = change_of_class[class_name]
                        class_node_name = hashlib.md5((commit_name + file_name + class_name).encode("utf-8")).hexdigest()
                        class_node = Node("Class", name=class_node_name, class_name=class_name)
                        class_node['definition'] = change_of_class1['definition']
                        graph.create(class_node)
                        file_to_class = Relationship(file_node, "Update", class_node)
                        graph.create(file_to_class)

                        for method_name in change_of_class1['method']:
                            method_node_name = hashlib.md5((commit_name + file_name + class_name + method_name).encode("utf-8")).hexdigest()
                            method_node = Node("Method", name=method_node_name, method_name=method_name)
                            method_node['changed_lines'] = change_of_class1['method'][method_name]['lines']
                            method_node['add_API'] = change_of_class1['method'][method_name]['addAPI']
                            method_node['remove_API'] = change_of_class1['method'][method_name]['removeAPI']
                            graph.create(method_node)
                            class_to_method = Relationship(class_node, "Change", method_node)
                            graph.create(class_to_method)

                            for api_name in change_of_class1['method'][method_name]['addAPI']:
                                matcher = NodeMatcher(graph)
                                api_node = matcher.match("API", name=api_name).first()
                                if api_node is None:
                                    api_node = Node("API", name=api_name)
                                    graph.create(api_node)
                                method_to_api = Relationship(method_node, "Add", api_node)
                                graph.create(method_to_api)

                            for api_name in change_of_class1['method'][method_name]['removeAPI']:
                                matcher = NodeMatcher(graph)
                                api_node = matcher.match("API", name=api_name).first()
                                if api_node is None:
                                    api_node = Node("API", name=api_name)
                                    graph.create(api_node)
                                method_to_api = Relationship(method_node, "Remove", api_node)
                                graph.create(method_to_api)


        last_commit = commit_node





"""
matcher = NodeMatcher(graph)
find_code_1 = matcher.match(label="file", name=file_name).first()
if find_code_1 is None:
    find_code_1 = Node(label="file", name=file_name)
    graph.create(find_code_1)
    print("Create!")
else:
    print(find_code_1)

pkl_file = open('data.pkl', 'rb')

commit_ids = pickle.load(pkl_file)
authors = pickle.load(pkl_file)
dates = pickle.load(pkl_file)
details = pickle.load(pkl_file)
file_map = pickle.load(pkl_file)
file_change = pickle.load(pkl_file)
pkl_file.close()
get_graph(commit_ids, authors, dates, details, file_map, file_change)
"""



