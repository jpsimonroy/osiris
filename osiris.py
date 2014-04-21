import sublime, sublime_plugin
import glob
import os
import os.path
from .common import *

index={}
matches_from_index = []
selected_word = ""

class Reindexer(sublime_plugin.EventListener): 
    def on_post_save(self, view):  
        global index
        print("Rebuilding index")
        index.clear()
        fs=getallfiles(cwd_for_window(sublime.active_window()))
        for f in fs:
            build_index(f)    

class TheNavigatorCommand(sublime_plugin.WindowCommand):
    def run(self):
        global matches_from_index
        global selected_word
        view = self.window.active_view()
        selected_word=view.substr(view.word(view.sel()[0]))
        if(len(index) == 0):
            fs=getallfiles(cwd_for_window(self.window))
            for f in fs:
                build_index(f)    
        matches_from_index = index.get(selected_word)
        if(matches_from_index == None):
            return
        if(len(matches_from_index) == 1):
            model = matches_from_index[0]
            view = self.window.open_file(model[2])
            navigate(view, model)
        elif(len(matches_from_index) > 1):
            self.show_matches(selected_word)

    def show_matches(self, function_name):
        names = []
        for match in matches_from_index:
            item = []
            item.append(function_name + ":" + match[1])
            item.append(match[2])
            names.append(item)
        self.window.show_quick_panel(names, self.match_selected)

    def match_selected(self, match):
        global matches_from_index
        if match == -1:
            return
        model = matches_from_index[match]
        view = self.window.open_file(model[2])
        navigate(view, model)

def navigate(view, model):
    def navigate_after_load():
        if(view.is_loading()):
            sublime.set_timeout(navigate_after_load,10)
            return
        view.sel().clear()
        view.sel().add(sublime.Region(model[0], model[0] + len(selected_word)))
        view.show_at_center(model[0])
    navigate_after_load()

def getallfiles(dir, extn = [".r", ".R"]):
    fs=[]
    for root, dirs, files in os.walk(dir):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in extn:
                fs.append(os.path.join(root, file))
    return fs

def build_index(file):
    global index
    f=open(file,"r")
    text = f.read()
    search_pattern = r"([a-zA-Z0-9\_]+) *(=|<-|<<-) *(function\(.*?\))"
    for match in re.finditer(search_pattern, text):
        index[match.group(1)] = index.get(match.group(1)) or []
        index[match.group(1)].append([match.start(),match.group(3),file])
    file_name, ext = os.path.splitext(os.path.basename(file))
    index[file_name] = index.get(file_name) or []
    print(file_name)
    index[file_name].append([0,'FILE',file])
    f.close()
