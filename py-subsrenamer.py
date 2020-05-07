#!/usr/bin/env python3 
#
# Renames subtitles files according to tv shows names found in a directory
# Acceped syntaxes for season/episode are: 304, s3e04, s03e04, 3x04 (case insensitive)
#
# Based on bash script: https://gist.github.com/colinux/799510
# v 1.1

import os
import re


def rename_subs_preview(extsub, extmovie, subsuffix):
    
    print("\nPreview:")
    
    res = match_subs_and_video(extsub, extmovie, subsuffix)

    for r in res:
        subtitle,newsubtitlename = r
        if os.path.isfile(newsubtitlename):
            print('Skipped (exist): "{}"\n'.format(newsubtitlename))
        else:
            print('old: "{}"\nnew: "{}"\n'.format(subtitle,newsubtitlename))

def rename_subs(extsub, extmovie, subsuffix):
    
    res = match_subs_and_video(extsub, extmovie, subsuffix)

    for r in res:
        subtitle,newsubtitlename = r
        if os.path.isfile(newsubtitlename):
            print('Skipped (exist): "{}"\n'.format(newsubtitlename))
        else:
            try:
                os.rename(subtitle,newsubtitlename)
                print('OK: "{}"'.format(newsubtitlename))
            except Exceptions as e:
                print('Error: {} ({})'.format(e, newsubtitlename))
                    
def match_subs_and_video(extsub, extmovie, subsuffix):
    """ Find subtitles and videofiles according name rules.
        Returns a list of tuples: [(old subtitle name, new subtitle name)]"""

    # accepted sub names (but without "p" - most likely it is a resolution marker (1080p etc))
    reexprsub = ['([0-9]+)([0-9][0-9])[^p]'
            , 's([0-9]+)e([0-9]+)[^p]'
            , '([0-9]+)x([0-9]+)[^p]']


    result=[]
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
                            result.append((subtitle,newsubtitlename))
    return result


ver = "1.1"

extsub = ('.srt','.ssa', '.sub')
extmovie = ('.avi','.mkv', '.mp4')


print("py-subsrenamer. Ver. " + ver)
print()

subsuffix = input("Enter lang suffix for subs(optional, ex: _en): ")
rename_subs_preview(extsub, extmovie, subsuffix)

rename = input("Rename? [y/N]: ").lower()
if rename in ['y','yes']:
    rename_subs(extsub, extmovie, subsuffix)
else:
    print("Exit")
