import glob
import os
import time

from PyQt5 import uic

while True:
    start_time = time.time()

    for file in glob.glob("*.ui"):
        start = time.time()
        module_name = file.split(".")[0]
        # https://github.com/pyqt/python-qt5-mavericks/blob/master/PyQt5/uic/pyuic.py
        # Line 108: H:\Profile\Appdata\Python\Python36\site-packages\PyQt5\uic\Compiler\compiler.py
        # def compileUi(self, input_stream, output_stream, from_imports, resource_suffix, import_from):
        output_file = open("{}.py".format(module_name), "w")
        uic.compileUi("{}.ui".format(module_name), output_file, False, 4, True, "_rc", "ui")
        output_file.close()
        
        print("Successfully built \"{}\". Time taken: {:.3f}s.".format(module_name, (time.time() - start)))

        
    print(" ")
    print("----------------------------")
    print("Finished building UI. Time taken: {:.3f}s.".format(time.time() - start_time))
    print("----------------------------")
    print(" ")

    from PyQt5.pyrcc_main import main
    import sys

    start_time = time.time()

    for file in glob.glob("*.qrc"):
        start = time.time()

        # Line 93
        # C:\Users\Josh\AppData\Local\Programs\Python\Python36\Lib\site-packages\PyQt5\pyrcc_main.py
        module_name = file.split(".")[0]
        sys.argv = ["pyrcc5", "-o", os.path.abspath("{}_rc.py".format(module_name)), os.path.abspath(file)]
        main()
        
        print("Successfully built \"{}\". Time taken: {:.3f}s.".format(module_name, (time.time() - start)))
        
    print(" ")
    print("----------------------------")
    print("Finished building resource file. Time taken: {:.3f}s.".format(time.time() - start_time))
    print("----------------------------")

    input("")
