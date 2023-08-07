import json
import os
import re

defaultTranslationsFile = 'translation.json'

def getTranslationFiles():
  return [
      f for f in os.listdir('.')
      if (os.path.isfile(f)
          and f.endswith('.json')           # noqa: W503
          and f != defaultTranslationsFile) # noqa: W503
  ]

def getFileLines(filename):
  fil = open(filename, 'r', encoding='utf8')
  lines = fil.readlines()
  fil.close()
  return lines

def removeComments(string):
  return re.sub(r'(\/\/.+)', '', string)

def parseLines(lines):
  parsedLines = []
  for line in lines:
    parsedLines.append(removeComments(line))
  return parsedLines

def getDictKeys(transDict):
  return [key for key in transDict]


defaultTranslation = json.loads(''.join(parseLines(getFileLines(defaultTranslationsFile))))[0]
defaultTranslationKeys = getDictKeys(defaultTranslation["*"])
translationFiles = getTranslationFiles()

for translationFile in translationFiles:
  print(f'Parsing {translationFile}')
  lines = parseLines(getFileLines(translationFile))
  translationJson = json.loads(''.join(lines))[0]
  language = getDictKeys(translationJson)[-1]
  translationKeys = getDictKeys(translationJson[language])
  for key in defaultTranslationKeys:
    if key not in translationKeys:
      translationJson[language][key] = defaultTranslation['*'][key]
      print(f'Adding missing {key} translation string')
  with open(translationFile, 'r+', encoding='utf8') as f:
    f.seek(0)
    json.dump([translationJson], f, indent=2, ensure_ascii=False)
    f.truncate()
