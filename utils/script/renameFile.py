import os

folder = "C:/Users/andry/Desktop/pyTiePie/data/2022_10_05/FLOAT_12_12 - Copia"
for count, filename in enumerate(os.listdir(folder)):
    row_new = (filename.split("x")[0])
    column_new = filename.split("x")[1].split(".")[0]
    frmt= filename.split("x")[1].split(".")[1]
    dst = f"{str(column_new)}x{str(row_new)}.{str(frmt)}"
    src =f"{folder}/{filename}"  # foldername/filename, if .py file is outside folder
    dst =f"{folder}/nuova_cartella/{dst}"
     
    # rename() function will
    # rename all the files
    os.rename(src, dst)