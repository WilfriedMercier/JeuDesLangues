# Init file for this directory
# Mercier Wilfried - IRAP

import os.path     as     opath
from   glob        import glob
from   PyQt5.QtGui import QIcon, QPixmap

def loadIcons(scriptPath, iconsPath, formats=['xbm', 'xpm', 'png', 'bmp', 'gif', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm']):
   '''
   Load icons appearing in the given icon directory as QIcons objects.

   :param str scriptPath: path where the main program is located
   :param str iconsPath: path where the icons are searched for
   :returns: icons dictionary
   :rtype: dict[QIcons]
   '''

   path             = opath.join(scriptPath, iconsPath)
   conf             = {}

   if opath.isdir(path):
      files         = [file for file in glob(opath.join(path, '*')) if file.split('.')[-1].lower() in formats]

      for file in files:

         # Name in dict are without extension and in upper cases only
         nameList   = opath.basename(file).split('.')[:-1]
         name       = ""
         for n in nameList:
            name   += n.upper()

         conf[name] = QIcon(QPixmap(file))

      ok            = True
   else:
      ok            = False

   return conf, ok


def setup(scriptPath, configFile):
   '''
   Setup program at startup.

   :param str scriptPath: path where the main program is located
