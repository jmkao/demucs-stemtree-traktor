# Imports from standard distribution libs
import codecs, json, base64
import os, platform, subprocess, sys

# Imports from external dependencies
import mutagen
import mutagen.mp4
import mutagen.id3

_defaultMetadataJSON = '''
{
  "mastering_dsp": {
    "compressor": {
      "enabled": false,
      "ratio": 2,
      "output_gain": 0.5,
      "release": 0.1,
      "attack": 0.01,
      "input_gain": 0.5,
      "threshold": 0,
      "hp_cutoff": 300,
      "dry_wet": 0
    },
    "limiter": {
      "enabled": false,
      "release": 0.05,
      "threshold": 0,
      "ceiling": 0
    }
  },
  "version": 1,
  "stems": [
    {"color": "#009E73", "name": "Drums"},
    {"color": "#D55E00", "name": "Bass"},
    {"color": "#CC79A7", "name": "Other"},
    {"color": "#56B4E9", "name": "Vox"}
  ]
}
'''

def encode(mixFilePath, drumFilePath, bassFilePath, otherFilePath, vocalFilePath, stemFilePath):
  # make sure the ffmpeg is present in env
  try:
    subprocess.check_call(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
  except FileNotFoundError:
    raise RuntimeError("ffmpeg is not in the environment. Make sure that it is installed and on your PATH")
  
  # make sure all of the input files exist
  allFilesExist = True
  for file in [mixFilePath, drumFilePath, bassFilePath, otherFilePath, vocalFilePath]:
    if not os.path.exists(file):
      print("ERROR - input file does not exist:", file)
      allFilesExist = False
  if not allFilesExist:
    raise RuntimeError("Input files are missing! Cannot continue.")

  # Use FFMPEG to mux all the files together including the original mix file's metadata/tags
  ffmpegArgs = ["ffmpeg", "-y", "-nostats", "-loglevel", "error",
    "-i", mixFilePath,
    "-i", drumFilePath,
    "-i", bassFilePath,
    "-i", otherFilePath,
    "-i", vocalFilePath,
    "-map", "0", "-map", "1", "-map", "2", "-map", "3", "-map", "4",
    # "-movflags", "+use_metadata_tags",
    "-c", "copy", "-c:a", "aac", "-b:a", "320k",
    stemFilePath
  ]
  subprocess.check_call(ffmpegArgs)
  sys.stdout.flush()

  # Add on the NI required additional JSON encoded metadata to identify the stem tracks
  metadata = base64.b64encode(_defaultMetadataJSON.encode("utf-8")).decode("utf-8")
  metadata = "0:type=stem:src=base64," + metadata
  mp4boxArgs = ["mp4box",
    "-udta", metadata,
    stemFilePath
  ]
  subprocess.check_call(mp4boxArgs)
  sys.stdout.flush()

  # Do I need this tag? The reference files have it but... apparently no, not necessary.
  # tags = mutagen.mp4.Open(stemFilePath)
  # tags['----:com.apple.iTunes:AUDIOTYPE'] = [mutagen.mp4.MP4FreeForm(b'STEM', mutagen.mp4.AtomDataType.UTF8)]
  # tags.save(stemFilePath)


def _test():
  encode("02 Hatsune Miku's Counter Attack.mp3", "separated/mdx_extra/02 Hatsune Miku's Counter Attack/drums.wav", "separated/mdx_extra/02 Hatsune Miku's Counter Attack/bass.wav", "separated/mdx_extra/02 Hatsune Miku's Counter Attack/other.wav", "separated/mdx_extra/02 Hatsune Miku's Counter Attack/vocals.wav", "test.stem.mp4")

if __name__ == "__main__":
  _test()
