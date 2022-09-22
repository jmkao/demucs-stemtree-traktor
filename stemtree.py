from fileinput import filename
from importlib.abc import SourceLoader
import os, shutil, subprocess, sys
import dircmp, nistem

srcLibraryPath = "C:/Users/James Kao/Dropbox/Music/iTunes/iTunes Media/Music"
stemLibraryPath = "C:/Users/James Kao/Dropbox/Music/Traktor Stems/demucs"
tmpDir = "./tmp"

demucsModelName = "mdx_extra"

stemSuffix = "stem.mp4"
stemFileNames = ["drums.wav", "bass.wav", "other.wav", "vocals.wav"]

try:
  subprocess.check_call(["demucs", "-h"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
except FileNotFoundError:
  raise RuntimeError("ffmpeg is not in the environment. Make sure that it is installed and on your PATH")  

srcLibraryPath = os.path.normpath(srcLibraryPath)
stemLibraryPath = os.path.normpath(stemLibraryPath)
tmpDir = os.path.abspath(tmpDir)

allPathsExist = True
for path in [srcLibraryPath, stemLibraryPath, tmpDir]:
  if not os.path.exists(path):
      print("ERROR - required directory path does not exist:", path)
      allPathsExist = False
  if not allPathsExist:
    raise RuntimeError("Required library or tmp pths missing! Cannot continue.")

print("Temp directory: ", tmpDir)
print("Stem library: ", stemLibraryPath)
print("Source library: ", srcLibraryPath)

filesToStem = dircmp.scanMissingFiles(srcLibraryPath, stemLibraryPath, "stem.mp4")
print("Found", len(filesToStem), "music files in source library not present in stem library")

for i, relFilePath in enumerate(filesToStem):
  absSrcFilepath = os.path.join(srcLibraryPath, relFilePath)
  relDirname, relSrcFilename = os.path.split(relFilePath)
  filenameNoExt = os.path.splitext(relSrcFilename)[0]
  relDestFilename = filenameNoExt  + "." + stemSuffix

  print(f"({i}/{len(filesToStem)}) Generating stems from: {absSrcFilepath}")
  demucsArgs = ["demucs",
    "--clip-mode", "clamp",
    "-n", demucsModelName,
    "--float32",
    absSrcFilepath
  ]
  subprocess.run(demucsArgs, cwd=tmpDir, check=True)

  separatedDir = os.path.join(tmpDir, "separated", demucsModelName , filenameNoExt)
  drumFilePath = os.path.join(separatedDir, stemFileNames[0])
  bassFilePath = os.path.join(separatedDir, stemFileNames[1])
  otherFilePath = os.path.join(separatedDir, stemFileNames[2])
  vocalFilePath = os.path.join(separatedDir, stemFileNames[3])

  absDestDirpath = os.path.join(stemLibraryPath, relDirname)
  os.makedirs(absDestDirpath, exist_ok=True)
  absDestFilepath = os.path.join(absDestDirpath, relDestFilename)

  print(f"({i}/{len(filesToStem)}) Muxing stem MP4 to: {absDestFilepath}")
  nistem.encode(absSrcFilepath, drumFilePath, bassFilePath, otherFilePath, vocalFilePath, absDestFilepath)

  shutil.rmtree(separatedDir)


