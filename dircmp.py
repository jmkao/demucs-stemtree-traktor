import os

# Walk tree of srcDirPath and return list of files not present in destDirPath where
# src file names would have their suffix replaced by altSuffix (e.g. .mp3 --> .stem.mp4)
def scanMissingFiles(srcDirPath, destDirPath, altSuffix):
  # Recurse through srcDirPath checking if transformed destDirPath filename exists
  srcDirPath = os.path.normpath(srcDirPath)
  destDirPath = os.path.normpath(destDirPath)

  missingFiles = []
  for dirpath, dirs, files in os.walk(srcDirPath):
    for fileName in files:
      ext = os.path.splitext(fileName)[1].lower()
      if not (ext == '.m4a' or ext == '.mp3'):
        continue
      fileRelPath = os.path.join(dirpath, fileName)
      fileRelPath = fileRelPath.replace(srcDirPath, '.')
      if not _destFileExists(destDirPath, fileRelPath, altSuffix):
        missingFiles.append(fileRelPath)

  return missingFiles

def _destFileExists(destDirRoot, fileRelPath, altSuffix):
  # Two transformations to get from srcRoot/fileRelPath to altFileFullPath
  # (1) Prepend destDirRoot to fileRelPath
  # (2) Replace fileRelPath file suffix with altSuffix

  altFileFullPath = os.path.splitext(fileRelPath)[0]
  altFileFullPath = os.path.join(destDirRoot, altFileFullPath + '.' + altSuffix)

  return os.path.exists(altFileFullPath)

def _test():
  result = scanMissingFiles("C:/Users/James Kao/Dropbox/Music/iTunes/iTunes Media/Music", "C:\\Users\\James Kao\\Dropbox\\Music\\Traktor Stems\\NUO-STEMS Output", "stem.m4a")
  print(len(result))

if __name__ == "__main__":
  _test()
