#!/usr/bin/env python3 
#
# Renames subtitles files according to tv shows names found in a directory
# Acceped syntaxes for season/episode are: 304, s3e04, s03e04, 3x04 (case insensitive)
#
# Based on bash script: https://gist.github.com/colinux/799510
# v 1.1
# GUI version

import os
import re
import wx

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        
        self.btnselect = wx.Button(self, label="Select folder")
        self.Bind(wx.EVT_BUTTON, self.select_directory, self.btnselect)
        
        self.lblpath = wx.StaticText(self, label="Folder: <not selected>")
        
        self.entrysuffix = wx.TextCtrl(self,size = (410, -1))
        
        self.entrysuffix.SetHint('Optional subtitles suffix (_en, _fr, etc.)')
        self.Bind(wx.EVT_TEXT,self.rename_subs_preview,self.entrysuffix)
        
        self.preview = wx.TextCtrl(self, size = (600, 90), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.preview.SetHint('Preview and log')
        
        self.btnsubsrename = wx.Button(self, label="Rename")
        self.btnsubsrename.Disable()
        self.Bind(wx.EVT_BUTTON, self.rename_subs, self.btnsubsrename)
        
        self.btnabout = wx.Button(self, label="About")
        self.Bind(wx.EVT_BUTTON, self.show_about, self.btnabout)
        
        sizer = wx.GridBagSizer()
        sizer.Add(self.btnselect,       pos=(0,0), span=(1, 2), flag=wx.LEFT)
        sizer.Add(self.lblpath,         pos=(1,0), span=(1, 2), flag=wx.EXPAND|wx.LEFT)
        sizer.Add(self.entrysuffix,     pos=(2,0), span=(1, 2), flag=wx.EXPAND|wx.LEFT)
        sizer.Add(self.preview,         pos=(3,0), span=(1, 2), flag=wx.EXPAND|wx.LEFT)
        sizer.Add(self.btnsubsrename,   pos=(4,0),              flag=wx.LEFT)
        sizer.Add(self.btnabout,        pos=(4,1),              flag=wx.RIGHT)
        self.SetSizer(sizer)
        
        self.Fit()
        self.Show(True)

    def select_directory(self,e):
        """ Select directory and save path to self.dirname """
        dlg = wx.DirDialog(self, "Choose a directory", '')
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetPath()
            self.lblpath.SetLabel('Folder: {}'.format(os.path.basename(self.dirname)))
            self.rename_subs_preview(self)
        dlg.Destroy()
        self.btnsubsrename.Enable()

    def rename_subs_preview(self,e):
        self.preview.SetValue('')
        res = self.match_subs_and_video()
        
        for r in res:
            subtitle,newsubtitlename = r
            if os.path.isfile(newsubtitlename):
                self.preview.AppendText('Skipped (exist): "{}"\n'.format(newsubtitlename))
            else:
                self.preview.AppendText('"{}" -> "{}"\n'.format(subtitle,newsubtitlename))
                                
    def rename_subs(self,e):
        self.preview.SetValue('')
        res = self.match_subs_and_video()
        
        for r in res:
            subtitle,newsubtitlename = r
            if os.path.isfile(newsubtitlename):
                self.preview.AppendText('Skipped (exist): "{}"\n'.format(newsubtitlename))
            else:
                try:
                    os.rename(subtitle,newsubtitlename)
                    self.preview.AppendText('OK: "{}"\n'.format(newsubtitlename))
                except Exceptions as e:
                    self.preview.AppendText('Error: {} ({})\n'.format(e, newsubtitlename))
                
    def show_about(self,e):
        aboutmsg =  "py-subsrenamer home:\n"\
                    "https://github.com/qiwichupa/py-subsrenamer\n"\
                    "\n"\
                    "Python 3, wxPython"
        
        dlg = wx.TextEntryDialog(self, caption="About", message='', value=str(aboutmsg), style=wx.TE_MULTILINE|wx.OK)
        
        dlg.SetMinSize((350,200))
        dlg.SetMaxSize((350,200))
        dlg.SetSize((350,200))
        
        dlg.ShowModal()
    
    def match_subs_and_video(self):
        """ Find subtitles and videofiles according name rules. 
            Returns a list of tuples: [(old subtitle name, new subtitle name)]"""
        folder_path = self.dirname
        subsuffix = self.entrysuffix.GetValue()

        extsub = ('.srt','.ssa', '.sub')
        extmovie = ('.avi','.mkv', '.mp4')

        # accepted sub names (but without "p" - most likely it is a resolution marker (1080p etc))
        reexprsub = ['([0-9]+)([0-9][0-9])[^p]'
                , 's([0-9]+)e([0-9]+)[^p]'
                , '([0-9]+)x([0-9]+)[^p]']

        os.chdir(folder_path)
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
app = wx.App(False)
ver='1.1'
title='py-subsrenamer v.{}'.format(ver)
frame = MainWindow(None, title)
app.MainLoop()
