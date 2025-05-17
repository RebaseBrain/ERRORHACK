import json


class error:
    enamepackage = ""
    errortype = ""
    pathToLogFile = ""
    nameCluster = ""

    def __init__(self, namepackage, errortype, pathToLogFile, nameCluster):
        self.namepackage = namepackage
        self.errortype = errortype
        self.pathToLogFile = pathToLogFile
        self.nameCluster = nameCluster


def parse_json(pathToJSON):
    with open(pathToJSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def aboba_sort(data, nameCluster):
    out = []
    for item in data:
        if item["nameCluster"] == nameCluster:
            out.append(item)
    return out


if __name__ == '__main__':
    data = parse_json('./list_data.json')
    allTypes = list(set([item["nameCluster"] for item in data]))
    out = []
    for i in allTypes:
        out.append(aboba_sort(data, i))

    for i in range(len(allTypes)):
        file = open(
            f"./clusters/{allTypes[i]}.json", "w", encoding="utf-8")
        json.dump(out[i], file, indent=2, ensure_ascii=False)
