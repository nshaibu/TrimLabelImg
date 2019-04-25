#!/usr/bin/python3

#===========================================================================================
# Copyright (C) 2019 Nafiu Shaibu.
# Purpose: 
#-------------------------------------------------------------------------------------------
# This is a free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your option)
# any later version.

# This is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#===========================================================================================

import os, sys, getopt, shutil
import xml.etree.ElementTree as ET
import logging as logger
from glob import glob
import random

log_filename = os.sep.join([os.path.expanduser('~'), "trimLabelImg.log"])
logger.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", filename=log_filename, level=logger.DEBUG)

baseFileName = "VVM_IMAGE"

DIR_FOR_IMG_WITHOUT_XML = "IMG_WITHOUT_XML"
DIR_FOR_XML_WITHOUT_IMG = "XML_WITHOUT_IMG"
DIR_FOR_UNNEEDED_FILES = "FILES_NOT_NEEDED"

class ProcessingXMLFailed(Exception):
    pass

class IMGFileDoesNotExist(Exception):
    pass

class XMLFileDoesNotExist(Exception):
    pass

class PathDoesNotExist(OSError):
    pass

class TrimLabelImgXML(object):

    def __init__(self, path):
        self.path = path
        self.tree = None
        self.root = None
        self.filename = None
        self.IMGName = None
        self.processedFiles = []

    def run(self):
        if os.path.exists(self.path):
            self.path = os.path.abspath(self.path)
            for file in glob(os.sep.join([self.path, "*.xml"])):
                try:
                    self.IMGName = self.getIMGName(file)
                    self.processXMLFile(file)
                except ProcessingXMLFailed:
                    continue
                except IMGFileDoesNotExist:
                    logger.warning("Image file for %s not found" % file)
                    continue

                #Rename Image
                _, IMG_ext = os.path.splitext(self.IMGName)
                newIMGName = os.path.splitext(self.filename)[0] + IMG_ext
                os.rename(self.IMGName, os.sep.join([self.path, newIMGName]))
        else:
            raise PathDoesNotExist("Path <%s> not a valid path" % self.path)

    def scanner(self, path, callbacks):
        if os.path.exists(path):
            self.path = os.path.abspath(path)
            
            for root, dirs, files in os.walk(self.path):
                if dirs == [] and files == []:
                    return
                
                for filename in files:
                    file = os.sep.join([root, filename])
                    for callback, args in callbacks:
                        callback(file, args)

                for dirp in dirs:
                    if dirp not in (DIR_FOR_IMG_WITHOUT_XML,
                                        DIR_FOR_UNNEEDED_FILES,
                                         DIR_FOR_XML_WITHOUT_IMG):
                        directory = os.sep.join([root, dirp])
                        self.scanner(directory, callbacks)
                        self.path = directory
                
                if dirs == [] or files == []: return
        return

    def move_img_without_xml(self, file, *args):
        if os.path.exists(file):
            dirname = os.path.dirname(file)
            
            _, ext = os.path.splitext(file)
            isImageFile = False
            if ext and ext.upper() in (".PNG", ".JPEG", ".JPG"):
                isImageFile = True
            
            if isImageFile:
                dirpath = os.sep.join([dirname, DIR_FOR_IMG_WITHOUT_XML])
                if not os.path.exists(dirpath):
                    os.mkdir(dirpath)
                try:
                    self.getXMLFileName(file)
                except XMLFileDoesNotExist:
                    try:
                        shutil.move(file, dirpath)
                    except shutil.Error:
                        destFile = os.sep.join([dirpath, os.path.basename(file)])
                        shutil.move(file, destFile)
                except ValueError:
                    pass

    def move_xml_without_img(self, file, *args):
        if os.path.exists(file):
            dirname = os.path.dirname(file)

            _, ext = os.path.splitext(file)
            isXMLFile = False
            if ext.upper() == ".XML":
                isXMLFile = True

            if isXMLFile:
                dirpath = os.sep.join([dirname, DIR_FOR_XML_WITHOUT_IMG])
                if not os.path.exists(dirpath):
                    os.mkdir(dirpath)
                try:    
                    self.getIMGName(file)
                except IMGFileDoesNotExist:
                    try:
                        shutil.move(file, dirpath)
                    except shutil.Error:
                        destFile = os.sep.join([dirpath, os.path.basename(file)])
                        shutil.move(file, destFile)
                except ValueError:
                    pass

    def move_unnecessary_files(self, file, *args):
        if os.path.exists(file):
            dirname = os.path.dirname(file)

            _, ext = os.path.splitext(file)
            isNotNeeded = False
            if ext and ext.upper() not in (".XML", ".PNG", ".JPEG", ".JPG"):
                isNotNeeded = True
            if ext == "":
                isNotNeeded = True

            if isNotNeeded:
                dirpath = os.sep.join([dirname, DIR_FOR_UNNEEDED_FILES])
                if not os.path.exists(dirpath):
                    os.mkdir(dirpath)
                try:
                    shutil.move(file, dirpath)
                except shutil.Error:
                    destFile = os.sep.join([dirpath, os.path.basename(file)])
                    shutil.move(file, destFile)

    def getIMGName(self, file):
        filename, ext = os.path.splitext(file)
        IMGName = None

        if ext and ext.upper() != ".XML":
            raise ValueError("File is not an xml")

        if os.path.exists(os.path.normpath('.'.join([filename, 'png']))):
            IMGName = os.path.normpath('.'.join([filename, 'png']))
        elif os.path.exists(os.path.normpath('.'.join([filename, 'PNG']))):
            IMGName = os.path.normpath('.'.join([filename, 'PNG']))
        elif os.path.exists(os.path.normpath('.'.join([filename, 'jpg']))):
            IMGName = os.path.normpath('.'.join([filename, 'jpg']))
        elif os.path.exists(os.path.normpath('.'.join([filename, 'JPG']))):
            IMGName = os.path.normpath('.'.join([filename, 'JPG']))
        elif os.path.exists(os.path.normpath('.'.join([filename, 'jpeg']))):
            IMGName = os.path.normpath('.'.join([filename, 'jpeg']))
        elif os.path.exists(os.path.normpath('.'.join([filename, 'JPEG']))):
            IMGName = os.path.normpath('.'.join([filename, 'JPEG']))

        if IMGName == None:
            raise IMGFileDoesNotExist("Image for XML file <%s> does not exist" % file)
        return IMGName

    def getXMLFileName(self, imgfile):
        filename, ext = os.path.splitext(imgfile)
        if ext and ext.upper() not in (".PNG", ".JPG", ".JPEG"):
            raise ValueError("File is not in any img format")

        XMLFile = ".".join([filename, "xml"])
        if not os.path.exists(XMLFile):
            raise XMLFileDoesNotExist("XML file <%s> does not exist" % XMLFile)
        return XMLFile

    def changeFileExtension(self, file, *args):
        if os.path.exists(file):
            filename, ext = os.path.splitext(file)
            fromExt, toExt = args[0]
            newFileName = None

            fromExt = fromExt if fromExt[0] != "." else fromExt[1:]
            toExt = toExt if toExt[0] != "." else toExt[1:]
            if ext and ext.upper()[1:] == fromExt.upper():
                newFileName = os.path.normpath(".".join([filename, toExt]))
            if ext and ext[1:].isupper():
                newFileName = os.path.normpath(filename + ext.lower())
            
            if newFileName:
                os.rename(file, newFileName)

    def displayStats(self):
        if self.filename and self.IMGName:
            print("Successfully scanned %d files\n" % len(self.processedFiles))

            for data in self.processedFiles:
                print("%s ------convert------> %s\n" % (
                    list(data.keys())[0],
                    list(data.values())[0] ))

    def processXMLFile(self, file):
        processedFile = dict()

        try:
            self.tree = ET.parse(file)
            self.root = self.tree.getroot()
        except:
            logger.warning("Processing %s filed" % file)
            logger.info(' '.join(["This files have been processed", str(self.processedFiles)]))
            raise ProcessingXMLFailed("Processing %s failed" % file)
    
        self.filename = "%s_%d_%s.xml" % (
            baseFileName,
            random.randrange(0, 1000),
            ''.join(random.sample(['a', 'b', 'B', 'zB', 'P', 'p', 'F', 'f'], 4)) 
            )

        for child in self.root.iter():
            _, ext = os.path.splitext(self.IMGName)
            if child.tag == "filename":
                child.text = os.path.splitext(self.filename)[0] + ext
            elif child.tag == "path":
                newIMGName = os.path.splitext(self.filename)[0] + ext 
                child.text = str(os.sep.join([self.path, newIMGName]))

        self.tree.write(str(os.sep.join([self.path, self.filename])))
        os.remove(file)
        processedFile[file] = str(os.sep.join([self.path, self.filename]))
        self.processedFiles.append(processedFile)

def main(argv):
    path = None
    displayinfo = False
    movefiles = False

    scantype = "shallow"
    fromExt = ""
    toExt = ""
    callbacks = []

    if len(argv) > 1:
        try:
            opts, _ = getopt.getopt(argv[1:], "hcp:b:s:im", 
                                    ["help", "info", "move", "changefileextension=",  "scantype=", "path=", "basefilename="])
        except getopt.GetoptError:
            print("%s" % (" ".join([argv[0], "[-hpcsimb]"])))
            sys.exit(0)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print("""
  Usage: trimLabelImgXML.py [-h] [-p path] [-s type] [-m] [-i] [-c transition_string] [-b basename]
--help,     -h                         :Print this help message and exit.
--path,     -p <directory>             :Specify the directory to scan.
--scantype, -s [shallow|deep]          :Specify the type of scanning to perform.
                              shallow  :only scan the toplevel of the specified 
                                        directory.
                              deep     :Scan the toplevel and all subdirectory 
                                        of the specified directory.
--move, -m                             :Move all unneccessary files into their own folders
--changefileextension, -c ext_string   :Change the extension of files in the given path to a
                                        different file extension.
                                        ext_string is formated in this form fromExt->toExt
                                        Example: jpeg->jpg means change all files with 'jpeg'
                                        extension to 'jpg'.
--basefilename, -b basename            :
                """)
                return
            elif opt in ("-b", "--basefilename"):
                global baseFileName
                baseFileName = arg
            elif opt in ("-p", "--path"):
                path = arg
            elif opt in ("-i", "info"):
                displayinfo = True
            elif opt in ("m", "--move"):
                movefiles = True
            elif opt in ("s", "--scantype"):
                if arg.lower() in ("shallow", "deep"):
                    scantype = arg.lower()
            elif opt in ("c", "--changefileextension"):
                arglist = str(arg).split("->")
                if len(arglist) == 2:
                    fromExt = arglist[0]
                    toExt = arglist[1]
        
        if path:
            trimmer = TrimLabelImgXML(path)
            try:
                if scantype == "shallow":
                    if fromExt != "" and toExt != "":
                        if os.path.exists(path):
                            rootPath = os.path.abspath(path)
                            callbacks.append( (trimmer.changeFileExtension, (fromExt, toExt)) )
                            trimmer.scanner(rootPath, callbacks)
                        callbacks = []

                    trimmer.run()
                elif scantype == "deep":
                    if os.path.exists(path):
                        rootPath = os.path.abspath(path)
                        
                        def callback(file, *args):
                            _, ext = os.path.splitext(file)

                            if ext.upper() != '.XML':
                                return
                            try:
                                trimmer.IMGName = trimmer.getIMGName(file)
                                trimmer.processXMLFile(file)
                            except ProcessingXMLFailed:
                                return
                            except IMGFileDoesNotExist:
                                logger.warning("Image file for %s not found" % file)
                                return

                            #Rename Image
                            _, IMG_ext = os.path.splitext(trimmer.IMGName)
                            newIMGName = os.path.splitext(trimmer.filename)[0] + IMG_ext
                            os.rename(trimmer.IMGName, os.sep.join([trimmer.path, newIMGName]))

                        if fromExt != "" and toExt != "":
                            callbacks.append( (trimmer.changeFileExtension, (fromExt, toExt)) )
                            trimmer.scanner(rootPath, callbacks)
                        
                        callbacks.append((callback, ()))
                        
                        if movefiles and scantype.lower() == "deep":
                            callbacks.extend([
                                (trimmer.move_img_without_xml, ()),
                                (trimmer.move_xml_without_img, ()),
                                (trimmer.move_unnecessary_files, ())
                            ])
                        trimmer.scanner(rootPath, callbacks)
                        callbacks = []
                    else:
                        raise PathDoesNotExist("Path <%s> not a valid path" % path)
            except PathDoesNotExist as e:
                logger.error(e.args)
                print("%s" % e.args)
                return
            except ValueError:
                return

            if movefiles and scantype.lower() != "deep":
                callbacks.extend([
                    (trimmer.move_img_without_xml, ()),
                    (trimmer.move_xml_without_img, ()),
                    (trimmer.move_unnecessary_files, ())])

            if len(callbacks) > 0:
                trimmer.scanner(trimmer.path, callbacks)
            if displayinfo:
                trimmer.displayStats()
        else:
            print("Please give a path to search")
    return


if __name__ == '__main__':
    main(sys.argv)
    sys.exit(0)