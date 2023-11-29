import sys
import re
from computer.register import InstructionType, NO_ARGUMENT


def translate(source_name: str, target_name: str):
    """
    翻译：
    1、获取asm文件内容
    2、翻译内容后写入指定文件
    @param source_name 源文件
    @param target_name 数据写入文件
    """
    result, function_point, label_in_fun, variable, instruction_index = read_asm_file(source_name)
    write_translate(target_name, result, function_point, label_in_fun, variable, instruction_index)


def process_line(line, result, instruction_index, last_fun, function_point, label_in_fun, index, is_first_fun):
    if check_string("^\\S*:$", line):
        line = pre_translation(line)
        if check_string("^\\.\\S*:$", line):
            line = line.replace(":", "")
            label_in_fun[last_fun][line] = instruction_index
        else:
            line = line.replace(":", "")
            function_point[line] = instruction_index
            label_in_fun[line] = dict()
            last_fun = line
            if is_first_fun:
                assert last_fun == '_START', 'Your first function should be _start'
    else:
        line = line.split(";")[0]
        line = re.sub(r"\t+", "", line)
        line = re.sub(r"\n", "", line)
        line = re.sub(r" +", " ", line)
        split = line.split(" ")
        split[0] = split[0].upper()
        assert split[0] in InstructionType.__members__, f"Line {index}, no such instrument"
        if InstructionType[split[0]] in NO_ARGUMENT:
            assert len(split) == 1, f"Line {index}, this instrument has no argument"
        else:
            assert len(split) == 2, f"Line {index}, only one argument allowed"
        if line != "":
            if len(split) == 2:
                if not check_string("^\'[A-Za-z]{1}\'$", split[1]):
                    split[1] = split[1].upper()
                result += f"{instruction_index} {InstructionType[split[0]].value} {split[1]}\n"
            else:
                result += f"{instruction_index} {InstructionType[split[0]].value}\n"
        instruction_index += 1
    return result, instruction_index, last_fun


def read_asm_file(source_name):
    result, last_fun = "", ""
    variable, function_point, label_in_fun = dict(), dict(), dict()
    index, instruction_index = 0, 0

    with open(source_name, "r") as f:
        line = f.readline()
        index += 1
        line = pre_translation(line)
        read_all_data = True
        if line == "SECTION .DATA":
            read_all_data = False
        while line and not read_all_data:
            line = f.readline()
            index += 1
            line = line.split(";")[0]
            line = re.sub(r"\t+", "", line)
            line = re.sub(r"\n", "", line)
            section = pre_translation(line)
            if section == "SECTION .TEXT":
                break
            key, value = read_variable(line)
            key = key.upper()
            assert key not in variable.keys(), f"Line {index}: You can't declare a variable two or more times"
            variable[key] = value

        line = f.readline()
        index += 1
        line = pre_translation(line)
        is_first_fun = True
        while line:
            if line != "" and line != "\n":
                result, instruction_index, last_fun = process_line(
                    line, result, instruction_index, last_fun, function_point, label_in_fun, index, is_first_fun
                )
            line = f.readline()
            index += 1

    return result, function_point, label_in_fun, variable, instruction_index


def write_translate(target_name: str, result, function_point, label_in_fun, variable, instruction_index):
    # Write to file
    with open(target_name, "w") as f:
        f.write(result)
        f.write("FUNCTION\n")
        for func, value in function_point.items():
            line = f"{func}:{value}\n"
            f.write(line)

        f.write("LABEL\n")
        for func, labels in label_in_fun.items():
            for label, value in labels.items():
                line = f"{func}:{label}:{value}\n"
                f.write(line)

        f.write("VARIABLE\n")
        for var, value in variable.items():
            line = f"{var}:{value}\n"
            f.write(line)

    # Read from file and process
    with open(target_name, "r") as f:
        index = 0
        while index < instruction_index:
            index += 1
            line = f.readline()
            line = pre_translation(line)
            term = line.split(" ")[1:]
            while "" in term:
                term.remove("")
            print(term)


def check_string(re_exp: str, target: str) -> bool:
    """
    判断字符串和正则表达式是否匹配
    :param re_exp: 正则表达式
    :param target: 需要判断的字符串
    :return: bool
    """
    return bool(re.search(re_exp, target))


def read_variable(line: str) -> tuple[str, str]:
    """  读取变量  """
    assert any(check_string(pattern, line) for pattern in [
        "^.*: *0 *$",
        "^.*: *[1-9]+[0-9]* *$",
        "^.*: *\".*\" *, *[1-9]+[0-9]* *$",
        "^.*: *\".*\" *$"
    ]), f"Illegal variable {line}"

    key, value = map(str.strip, line.split(":", 1))
    key = re.findall("\\S*", key)[0]

    if check_string("^.*: *-?[1-9]+[0-9]* *$", line):  # 数字
        value = re.findall("-?[1-9]+[0-9]*", value)[0]
    elif check_string("^.*: *0 *$", line):
        value = '0'
    elif check_string("^.*: *\".*\" *$", line):  # 字符串
        value = re.findall("\".*\"", value)[0] + f",{len(value) - 2}"
    else:
        left, right = map(str.strip, value.rsplit(',', 1))
        left = left.rsplit("\"", 1)[0] + "\""
        value = f"{left},{re.sub(r' ', '', right)}"

    return key, value


def pre_translation(line: str) -> str:
    """
    翻译内容预处理
    1、将每行内容转换为大写
    2、去掉";"之后的内容(仅作为注释使用)
    3、去掉制表符(\t)和换行符(\n)
    """
    line = line.upper()
    line = line.split(";")[0]
    line = re.sub(r"\t+", "", line)
    line = re.sub(r"\n", "", line)
    return line


if __name__ == "__main__":
    assert len(sys.argv) == 3, '参数错误'
    translate(sys.argv[0], sys.argv[1])
