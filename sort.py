import os
import shutil
import sys


main_path = sys.argv[1]

extensions = {'images': ['jpeg', 'png', 'jpg', 'svg'], 'video': ['avi', 'mp4', 'mov', 'mkv'],
'documents': ['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'], 'audio': ['mp3', 'ogg', 'wav', 'amr'],
'archives': ['zip', 'gz', 'tar', 'rar']}

dict_fact_files = {'images': [], 'video': [], 'documents': [], 'audio': [], 'archives': [], 'unknown_extension': []}

dict_extensions = {'known extensions': set(), 'unknown extensions': set()}

lst_all_files = []


def correct_path():

    try:
        main_path = sys.argv[1]
    except IndexError:
        sys.exit('Write path!')
    if not os.path.exists(main_path):
        sys.exit('Not exist folder, write correct!')


def list_all_files(folder_path, files):

    for ob in os.scandir(folder_path):
        if ob.is_file():
            files.append(ob)
        elif ob.is_dir():
            list_all_files(ob, files)

    return files


def create_folders(folder_path, folder_names):

    for folder in folder_names:
        file_path = os.path.join(folder_path, folder)
        if not os.path.exists(file_path):
            os.mkdir(file_path)

    os.mkdir(os.path.join(folder_path, 'unknown_extension'))


def normalize(name):

    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
    TRANS = {}
    cor_name = ''

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c.lower())] = l.lower()
        TRANS[ord(c.upper())] = l.upper()

    for i in name[:name.rfind('.')]:
        if ord(i) in TRANS.keys():
            cor_i = i.translate(TRANS)
        elif i.isdigit() or i.isalpha():
            cor_i = i
        else:
            cor_i = '_'
        cor_name += cor_i
    cor_name += name[name.rfind('.'):]

    return cor_name


def sort_normalize_files(folder_path, extensions, lst_all_files):

    for file in lst_all_files:
        moved = False

        for key, value in extensions.items():
            if file.name[(file.name).rfind('.')+1:] in value and key != 'archives':
                shutil.move(file, os.path.join(folder_path, key, normalize(file.name)))
                moved = True
                dict_fact_files[key].append(normalize(file.name))
            elif file.name[(file.name).rfind('.')+1:] in value and key == 'archives':
                shutil.unpack_archive(file, os.path.join(folder_path, key, normalize(file.name[:(file.name).rfind('.')])))
                moved = True
                dict_fact_files[key].append(normalize(file.name))
                os.remove(os.path.join(folder_path, file.name))

        if moved == False:
            shutil.move(file, os.path.join(folder_path, 'unknown_extension', normalize(file.name)))
            dict_fact_files['unknown_extension'].append(normalize(file.name))


def normalize_archive(folder_path):

    for zp in os.scandir(folder_path):
        if zp.is_file():
            os.rename(zp, os.path.join(folder_path, normalize(zp.name)))
        elif zp.is_dir():
            normalize_archive(zp)
            os.rename(zp, os.path.join(folder_path, normalize(os.path.basename(zp))))


def remove_empty_folders(folder_path):

    for em in os.scandir(folder_path):
        if em.is_dir() and em.name not in extensions.keys() and em.name != 'unknown_extension':
            shutil.rmtree(em, ignore_errors=True)


def result(dict_fact_files, dict_extensions):

    for key, value in dict_fact_files.items():
        print(f"All files in category '{key}': {', '.join(value)}")
        if key == 'unknown_extension':
            dict_extensions['unknown extensions'].update(k[(k).rfind('.'):] for k in value)
        else:
            dict_extensions['known extensions'].update(k[(k).rfind('.'):] for k in value)

    for key, value in dict_extensions.items():
        print(f"{key}: {', '.join(value)}")


if __name__ == "__main__":
    correct_path()
    lst_all_files = list_all_files(main_path, lst_all_files)
    create_folders(main_path, extensions)
    sort_normalize_files(main_path, extensions, lst_all_files)
    normalize_archive(os.path.join(main_path, 'archives'))
    remove_empty_folders(main_path)
    result(dict_fact_files, dict_extensions)
