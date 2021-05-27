# Init file for this directory
# Mercier Wilfried - IRAP

import os.path     as     opath
import yaml
from   glob        import glob
from   PyQt5.QtGui import QIcon, QPixmap

def loadIcons(scriptPath, iconsPath, formats=['xbm', 'xpm', 'png', 'bmp', 'gif', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm']):
   '''
   Load icons appearing in the given icon directory as QIcons objects.

   :param str scriptPath: path where the main program is located
   :param str iconsPath: path where the icons are searched for
   :returns: icons dictionary, True if everything is ok or False otherwise, error message if any
   :rtype: dict[QIcons], bool, str
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
      msg           = ''
   else:
      ok            = False
      msg           = 'Icons path is incorrect.'

   return conf, ok, msg


def loadCorpus(scriptPath, corpusFile):
   '''
   Load a corpus file.

   :param str scriptPath: path where the main program is located
   :param str corpusFile: name of the corpus txt file relative to **scriptPath**

   :returns: corpus text, ok flag and error message if any
   :rtype: str, boolean, str
   '''

   file       = opath.join(scriptPath, corpusFile)

   if not opath.isfile(file):
      return '', False, 'No corpus file %s found in %s directory.' %(corpusFile, scriptPath)
   else:
      with open(file, 'r') as f:
         text = f.read()
         return text, True, ''


def setup(scriptPath, configFile):
   '''
   Setup program at startup.

   :param str scriptPath: path where the main program is located
   :param str configFile: name of the config file
   :returns: conf dictionary, True if everything is ok or False otherwise, error message if any
   :rtype: dict, bool, str
   '''

   file                  = opath.join(scriptPath, configFile)

   if not opath.isfile(file):
      return {}, False, 'Configuration file is missing.'
   else:
      with open(file, 'r') as f:
         conf            = yaml.load(f, Loader=yaml.Loader)

      # Generate icons
      iconsPath          = conf['iconDir']
      formats            = conf['formats']
      icons, ok, msg     = loadIcons(scriptPath, iconsPath, formats=formats)

      # Remove old icons keys and place loaded icons instead in conf dict
      conf.pop('iconDir')
      conf.pop('formats')
      conf['icons']      = icons

      # Load default corpus file if not empty
      corpusFile         = opath.join(conf['corpusDir'], conf['corpusDefault'])
      text, ok, msg      = loadCorpus(scriptPath, corpusFile)

      # Remove old corpus keys and place corpus text and file name instead in conf dict
      conf['corpusDir']  = opath.join(scriptPath, conf['corpusDir'])
      conf['corpusName'] = conf['corpusDefault']
      conf['corpusText'] = text
      conf.pop('corpusDefault')

      return conf, ok, msg

