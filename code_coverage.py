__author__ = "kumar reddy"

import os
import sys
import json
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Generating coverage report from .xcresult')
parser.add_argument('project',type=str, help="Provide the .xcproject name if not give empty like empty quotes")
parser.add_argument('workspace',type=str, help="Provide the .xcworkspace name, if not give empty like empty quotes  ")
parser.add_argument('scheme',type=str, help="provide the scheme")
args = parser.parse_args()

project = sys.argv[1]
workspace = sys.argv[2]
scheme = sys.argv[3]
folder = ""
if workspace:
    folder = sys.argv[2].split('.xcworkspace')
else:
    folder = sys.argv[2].split('.xcodeproj')

folderName = folder[0]

packages = []
for r, d, f in os.walk(folderName):
    packages = d
    # for file1 in f:
    #     print(file1)
    break

executableLines = 0.0
coveredLines = 0.0
derivedDataPath = ""
if project:
    derivedDataPath = "xcodebuild -project {} -scheme {} -showBuildSettings | grep OBJROOT | cut -d = -f 2".format(project, scheme)
else:
    derivedDataPath = "xcodebuild -workspace {} -scheme '{}' -showBuildSettings | grep OBJROOT | cut -d = -f 2".format(workspace, scheme)
dPath = subprocess.check_output(derivedDataPath, shell= True)
resultPath = dPath.replace('/Build/Intermediates.noindex', '/Logs/Test')
latestXCResultPath = "ls -atr {}".format(resultPath).rstrip('\n') + "| grep .xcresult | tail -n 1"
latestXCResult = subprocess.check_output(latestXCResultPath, shell= True)
finalPath = resultPath.rstrip('\n')+'/'+latestXCResult
resultPath = finalPath.rstrip('\n')
trimmedResultPath = resultPath.lstrip()
reportOutput = "xcrun xccov view --report '{}' --json > coverage_report.json".format(trimmedResultPath)
subprocess.check_output(reportOutput, shell=True)

html_str = """
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>
  <style> 
            table { 
                border-collapse: collapse; 
            } 
            th { 
                background-color:green; 
                Color:white; 
            } 
            th, td { 
                width:150px; 
                text-align:center; 
                border:1px solid black; 
                padding:5px 
              
            } 
            .geeks { 
                border-right:hidden; 
            } 
            .gfg { 
                border-collapse:separate; 
                border-spacing:0 15px; 
            } 
            h1 { 
                color:green; 
            } 
            
        </style> 
</head>
"""

reportFile = open("coverage_report.json", "r")
jsonFile = json.load(reportFile)

# print(folderName)

for package in packages:
    files = []
    executableLines = 0.0
    coveredLines = 0.0
    for r, d, f in os.walk(folderName+"/"+package):
        for file1 in f:
            # print(file1)
            if '.swift' in file1:
                files.append(file1)
    # print(files)

    inner_html_str=""        
    for target in jsonFile['targets']:
        if target['name'] == folderName+'.app':
            for tFile in target['files']:
                if tFile['name'] in files:
                    execLines = float(tFile['executableLines'])
                    coverLines = float(tFile['coveredLines'])
                    executableLines += execLines
                    coveredLines += coverLines
                    inner_html_str += "<tr>"
                    inner_html_str += "<td>"+tFile['name']+"</td>"
                    inner_html_str += "<td>"+str(execLines)+"</td>"
                    inner_html_str += "<td>"+str(coverLines)+"</td>"
                    coverage12 = (coverLines/execLines)*100        
                    inner_html_str += "<td><progress value="+str(coverage12)+" max=100></progress></td>"
                    inner_html_str += "</tr>"
    packageCoverage = "NA"
    if coveredLines == 0.0:
        packageCoverage = "No Test Cases"
    else:
        packageCoverage = str(round(((coveredLines/executableLines)*100),2))+"%"
    html_str += """
<div class="container">
  <h4 type="button" data-toggle="collapse" data-target="#{demo}">{pkgname} &emsp; {percentage}</h4>
  <div id="{demo}" class="collapse">
    <table style="width:100%">
    <tr>
    <th>FileName</th>
    <th>Executable Lines</th>
    <th>Covered Lines</th>
    <th>Progress</th>
    </tr>
""".format(pkgname=package, demo = package, percentage = packageCoverage)
    html_str += inner_html_str
    html_str += "</table></div></div>"

html_str += """
  </div>
</div>
</body>
"""

f = open("coverage_report.html","w")
f.write(html_str)
f.close()
os.remove("coverage_report.json")
print("Generated report at coverage_report.html")