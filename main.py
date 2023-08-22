import csv
import json
import os.path
import sqlite3

# constants
FILE_CONVERTING = 1
DIRECTORY_CONVERTING = 2


# float_check
def float_check(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


# Convert function
def csv_to_sqllite(sql_filename, csv_reader, csv_filename, csv_sz):
    table_colums = next(csv_reader)
    table_colums[0] = table_colums[0][3:]
    colums = len(table_colums)
    if not os.path.isfile(sql_filename+'.db'):
        open(sql_filename+'.db', 'x')
    con = sqlite3.connect(sql_filename+'.db')
    cur = con.cursor()
    query = "CREATE TABLE IF NOT EXISTS abcd("
    for i in range(colums-1):
        query = query + table_colums[i] + " TEXT" + ','
    query = query + table_colums[colums-1] + " TEXT" + ")"
    print(query)
    cur.execute(query)
    con.commit()
    query = "ALTER TABLE abcd RENAME TO " + csv_filename
    cur.execute(query)
    con.commit()
    insert_query_el = "INSERT INTO " + csv_filename
    insert_query_el += " VALUES ("
    count = csv_sz
    count1 = 0
    for line in csv_reader:
        query = insert_query_el
        for i in range(colums):
            line[i] = "'" + line[i] + "'"
        for i in range(colums-1):
            query += line[i] + ", "
        query += line[colums-1] + ")"
        res = int((100 * count1 / count))
        print("Converting file " + csv_filename + " " + str(res) + "%")
        cur.execute(query)
        con.commit()
        count1 += 1
    con.close()


# function to find how many lines in csv
def csv_sz(path):
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        return sum(1 for _ in reader) - 1


# Scan directory for csv files function
def scan_directory(list_of_csv_path, path):
    files = os.listdir(path)
    for file in files:
        if len(file.split('.')) == 1:
            scan_directory(list_of_csv_path, path+"\\"+file)
        elif file.split('.')[1] == "csv":
            list_of_csv_path.append(path+"\\"+file)


# main part
if __name__ == "__main__":
    while True:
        try:
            choose_way = int(input("Обработать файл или директорию: 1 или 2? \n"))
            break
        except ValueError:
            print("Неправильный формат ввода")
    if choose_way == FILE_CONVERTING:
        while True:
            path_to_file = input("Введите путь до файла в этой директории, если же он находится в той же папке,"
                                 "что и main.py напишите название файла\n")
            if path_to_file[-4:] == ".csv" and os.path.isfile(path_to_file):
                sz = csv_sz(path_to_file)
                with open(path_to_file, 'r') as file:
                    reader = csv.reader(file, delimiter=',')
                    csv_filename = path_to_file.split('\\')[-1][:-4]
                    sql_filename = input("Введите имя конечного файла базы данных без типа файла \n")
                    csv_to_sqllite(sql_filename.split('.')[0], reader, csv_filename, sz)
                    print("Все прошло успешно, в файле " + sql_filename + " создана таблица " + csv_filename)
                    break
            else:
                print("Something went wrong, try again")
    if choose_way == DIRECTORY_CONVERTING:
        while True:
            path_to_directory = input("Выберите путь до папки, в которой находятся csv - файлы\n")
            if os.path.isdir(path_to_directory):
                files = os.listdir(path_to_directory)
                csv_files_path = []
                scan_directory(csv_files_path, path_to_directory)
                if csv_files_path == []:
                    print("В указанной директории нет файлов формата csv, попробуйте снова")
                    continue
                files_to_convert = {}
                for file_path in csv_files_path:
                    files_to_convert[file_path] = (True, "user", os.path.getsize(file_path))
                with open("files_to_convert.json", "w") as json_file:
                    json.dump(files_to_convert, json_file)
                agree_with_converting = input("In file files_to_convert.json change what you need:\n"
                                              "the first item is true and anything else will be ignored\n"
                                              "the second is the name of db file where the information will place in\n"
                                              "write anything to continue\n")
                with open("files_to_convert.json") as json_file:
                    data = json.load(json_file)
                    for el in csv_files_path:
                        if data[el][0]:
                            with open(el, "r") as csv_file:
                                reader = csv.reader(csv_file, delimiter=",")
                                csv_to_sqllite(data[el][1], reader, el.split("\\")[-1].split(".")[0], csv_sz(el))
                print("Все прошло удачно")
                os.remove("files_to_convert.json")
                break