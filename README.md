# TrimLabelImg
TrimLabelImg fix any naming associated errors for images annotated with labelImg. https://github.com/tzutalin/labelImg

###
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
--basefilename, -b basename            :fallback filename.
