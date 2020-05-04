#!/usr/bin/env python3 
#
# Renames subtitles files according to tv shows names found in a directory
# Acceped syntaxes for season/episode are: 304, s3e04, s03e04, 3x04 (case insensitive)
#
# Based on bash script: https://gist.github.com/colinux/799510
# v 1.0
# GUI version

import os
import re

from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import *


def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    global btnrename
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    btnrename['state'] = 'normal'
    print(filename)

def rename_subs():
    global folder_path
    global suffixentry
    
    extsub = ('.srt','.ssa', '.sub')
    extmovie = ('.avi','.mkv', '.mp4')

    # accepted sub names (but without "p" - most likely it is a resolution marker (1080p etc))
    reexprsub = ['([0-9]+)([0-9][0-9])[^p]'
            , 's([0-9]+)e([0-9]+)[^p]'
            , '([0-9]+)x([0-9]+)[^p]']

    subsuffix=suffixentry.get()
    
    os.chdir(folder_path.get())
    
    # search subtitle...
    for sfile in sorted(os.listdir()):
        # ... with right extension...
        if sfile.endswith(extsub):
            subfound = False
            # ... and pattern in filename
            for r in reexprsub:
                s = re.search(r,sfile,re.IGNORECASE)
                if s:
                    subfound = True
                    regex = r
                    break
            if subfound:
                subtitle = sfile
                # get season and episode numbers
                for se in re.finditer(regex, subtitle,re.IGNORECASE):
                    season = se.groups()[0].lstrip('0') # remove leading zeroes
                    episode = se.groups()[1]
                    # set patterns for movie finding (but without "p" - most likely it is a resolution marker (1080p etc))
                    reexprmovie = [ '{}{}[^p]'.format(season,episode)
                                ,'s0*{}e{}[^p]'.format(season,episode)
                                ,'0*{}x{}[^p]'.format(season,episode)]
                # search movie...
                for mfile in sorted(os.listdir()):
                    # ... with right extension...
                    if mfile.endswith(extmovie):
                        moviefound = False
                        # ... and pattern in filename
                        for r in reexprmovie:
                            s = re.search(r,mfile,re.IGNORECASE)
                            if s:
                                moviefound = True
                                break
                        if moviefound:
                            movie = mfile
                            moviebasename = os.path.splitext(movie)[0]
                            subtitleext = os.path.splitext(subtitle)[1]

                            newsubtitlename = moviebasename + subsuffix + subtitleext
                            if os.path.isfile(newsubtitlename):
                                print('Skipped (exist): "{}"'.format(newsubtitlename))
                            else:
                                os.rename(subtitle,newsubtitlename)
                                print('OK: "{}"'.format(newsubtitlename))


root = Tk()
root.title("py-subsrenamer (gui) # v 1.0")
root.resizable(False, False)

folder_path = StringVar()
lbl1 = Label(textvariable=folder_path,width=20, anchor="e")
lbl1.grid(row=0, column=1)


btnbrowse = Button(text="Browse", width=12, command=browse_button)
btnbrowse.grid(row=0, column=2)

lbl2 = Label(text='Optional suffix (ex: _en):')
lbl2.grid(row=2, column=1)

suffixentry = Entry(width=14)
suffixentry.grid(row=2, column=2, )

btnrename = Button(text="Rename Subs", command=rename_subs)
btnrename['state'] = 'disabled'
btnrename.grid(row=3, column=1, columnspan=2)

mainloop()
