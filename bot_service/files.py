import os
import json
#Работа с файлом
class Files():
    def __init__(self):
        pass
    def add_data(self,key, info, file):
        '''Добавляет данные в фаил'''
        file = str(file) + '.json'
        if os.path.exists('files/'+file):
            with open('files/'+file, encoding='utf-8') as json_file:
                data = json.load(json_file)
        else:
            data = {}
        data[key] = info
        with open('files/'+file, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

    def delete_file(self,file):
        '''Удаляет фаил'''
        file = 'files/' + str(file) + '.json'
        if os.path.exists(file):
            os.remove(file)

    def get_par(self,key, file):
        file = str(file) + '.json'
        if os.path.exists('files/'+file):
            with open('files/'+file, encoding='utf-8') as json_file:
                data = json.load(json_file)
        return data[key]
