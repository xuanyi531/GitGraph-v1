# coding:utf-8
from preSolve import *
from neo4jFuncs import *
import pickle
import hashlib
import sys

if __name__ == '__main__':
    path = "./YahooNewsOnboarding/"
    picOps = False
    audOps = False
    vidOps = False
    cusOps = False

    """
    argv[1] is the path of project
    argv[2] is the filtering options
    """
    if len(sys.argv) > 1:
        path = sys.argv[1]

    if len(sys.argv) == 3:
        if "p" in sys.argv[2]:
            picOps = True
        if "a" in sys.argv[2]:
            audOps = True
        if "v" in sys.argv[2]:
            vidOps = True
        if "c" in "cav":
            cusOps = True
    print("Starting...")
    # extract commit id
    commit_ids, authors, dates, details = get_commit(path)

    # extract from commit
    """
    file_map: {
        index: commit_id
        value: file_list
    }
    
    file_change: {
        index: MD5(commit_id + file_name)
        value: {
            file_type: java / xml / png or ...
            class_list: [class_nameA, class_nameB, ...]
            method_list: [class_nameA:method_name1, class_nameA:method_name2, ... ]
            changes: {
                classA{
                    definition: [line1, line2, line3, ...]
                    method: {
                        method1: {
                            lines: [line1, line2, ...]
                            addAPI: [API1, API2, ...]
                            removeAPI: [API3, API4, ...]
                        }
                        method2: {
                            ...
                        }
                    }
                }
                classB: {
                    ...
                }
            }
        }
    }
    """
    file_map = {}
    file_change = {}
    for item in commit_ids:
        file = get_filename(path, item, picOps, audOps, vidOps, cusOps)
        # filter the rename operation
        file = remove_rename(file)
        file_map[item] = file

    print("Extracting all of the classes and methods of each file...")
    for item in commit_ids:
        for file in file_map[item]:
            file_node_name = hashlib.md5((item + file).encode("utf-8")).hexdigest()
            file_change[file_node_name] = {}
            file_type = os.path.splitext(file)[1][1:]
            file_change[file_node_name]['file_type'] = file_type

            if file_type == "java" and os.path.exists(path + file):
                # print("dealing with " + path + file + "...")
                class_list, method_list, method_list2, changes = get_change(project_root=path, commit_id=item, file_name=file)
                file_change[file_node_name]['class_list'] = class_list
                file_change[file_node_name]['method_list'] = method_list2
                file_change[file_node_name]['changes'] = changes
                """
                method_list is method_name
                method_list2 is class_name:method_name
                """

    # save as files
    output = open('data.pkl', 'wb')

    # Pickle the list using the highest protocol available.
    pickle.dump(commit_ids, output, -1)
    pickle.dump(authors, output, -1)
    pickle.dump(dates, output, -1)
    pickle.dump(details, output, -1)
    # Pickle dictionary using protocol 0.
    pickle.dump(file_map, output)
    pickle.dump(file_change, output)
    output.close()
    print("Drawing Knowledge graph...")
    get_graph(commit_ids, authors, dates, details, file_map, file_change)
    print("Done.")