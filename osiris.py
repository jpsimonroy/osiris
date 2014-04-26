import sublime, sublime_plugin
import glob
import os
import os.path
from .common import *

index={}
matches_from_index = []
selected_word = ""
page_index={}
usages_index = {}

class Reindexer(sublime_plugin.EventListener):
    def on_post_save(self, view):
        global index
        index.clear()
        fs=getallfiles(cwd_for_window(sublime.active_window()))
        for f in fs:
            build_index(f, index)

class UsagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        global usages_index
        global matches_from_index
        index_if_needed()
        usages_index.clear()
        fs=getallfiles(cwd_for_window(sublime.active_window()))
        word = current_word();
        for f in fs:
            build_usages_index(f, usages_index, word)
        possible_matches = usages_index.get(word);
        declarations = index.get(word)
        matches_from_index = [z for z in filter(lambda x: (x[1], x[3]) not in [(d[1],d[3]) for d in declarations], possible_matches)]
        if(matches_from_index == None):
            return
        if(len(matches_from_index) == 1):
            model = matches_from_index[0]
            view = self.window.open_file(model[3])
            navigate(view, model)
        elif(len(matches_from_index) > 1):
            show_matches()


class FileNavigatorCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        file_path=view.file_name()
        base_file_name = os.path.basename(file_path)
        if base_file_name.startswith("test"):
            self.navigate_test()
        else:
            self.navigate_source() 
        

    def navigate_source(self):
        global page_index
        global matches_from_index
        page_index = {}
        build_index(self.window.active_view().file_name(), page_index)
        matches_from_index = []
        for key in page_index:
            for match in page_index[key]:
                matches_from_index.append(match)
        show_matches()

    def navigate_test(self):
        global page_index
        global matches_from_index
        page_index = {}
        matches_from_index = []
        page_index = index_test(self.window.active_view().file_name(), {})
        matches_from_index = []
        for key in page_index:
            matches_from_index.append(page_index.get(key))
        matches_from_index = sorted(matches_from_index, key=lambda element: element[0])
        show_matches()                

class TheNavigatorCommand(sublime_plugin.WindowCommand):
    def run(self):
        global matches_from_index
        global selected_word
        global index
        view = self.window.active_view()
        selected_word=current_word()
        index_if_needed()
        matches_from_index = index.get(selected_word)
        if(matches_from_index == None):
            return
        if(len(matches_from_index) == 1):
            model = matches_from_index[0]
            view = self.window.open_file(model[3])
            navigate(view, model)
        elif(len(matches_from_index) > 1):
            show_matches()

def current_word(view=None):
    view=view or sublime.active_window().active_view()
    return(view.substr(view.word(view.sel()[0])))

def index_if_needed():
    global index
    if(len(index) == 0):
        fs=getallfiles(cwd_for_window(sublime.active_window()))
        for f in fs:
            build_index(f, index)

def show_matches():
    names = []
    for match in matches_from_index:
        item = []
        item.append(match[0] + "::" + match[2])
        item.append(match[3])
        names.append(item)
    sublime.active_window().show_quick_panel(names, match_selected)

def match_selected(match):
    global matches_from_index
    if match == -1:
        return
    model = matches_from_index[match]
    view = sublime.active_window().open_file(model[3])
    navigate(view, model)

def navigate(view, model):
    def navigate_after_load():
        if(view.is_loading()):
            sublime.set_timeout(navigate_after_load,10)
            return
        view.sel().clear()
        view.sel().add(sublime.Region(model[1], model[1] + len(model[0])))
        view.show_at_center(model[1])
    navigate_after_load()

def getallfiles(dir, extn = [".r", ".R"]):
    fs=[]
    for root, dirs, files in os.walk(dir):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in extn:
                fs.append(os.path.join(root, file))
    return fs

def build_index(file, index, search_pattern=r"([a-zA-Z0-9\_]+) *(=|<-|<<-) *(function\(.*?\))"):
    f=open(file,"r")
    text = f.read()
    for match in re.finditer(search_pattern, text):
        index[match.group(1)] = index.get(match.group(1)) or []
        index[match.group(1)].append([match.group(1),match.start(),match.group(3),file])
    file_name, ext = os.path.splitext(os.path.basename(file))
    index[file_name] = index.get(file_name) or []
    index[file_name].append([file_name, 0,'FILE',file])
    f.close()

def build_usages_index(file, index, search_keyword):
    f=open(file,"r")
    text = f.read()
    for match in re.finditer(search_keyword, text):
        index[match.group(0)] = index.get(match.group(0)) or []
        index[match.group(0)].append([match.group(0),match.start(),'',file])
    f.close()

def index_test(file, index):
    f = open(file, "r")
    text = f.read()
    context_searcher = r"context *\(\"(.*)\"\)|context *\(\'(.*)\'\)"
    context_locations = []
    for match in re.finditer(context_searcher, text):
        context_locations.append([match.group(1) or match.group(2), match.start()])
    test_searcher = r"test_that *\(\"(.*)\"|test_that *\(\'(.*)\'"
    test_locations = []
    for match in re.finditer(test_searcher, text):
        test_locations.append([match.group(1) or match.group(2), match.start()])

    tests_with_contexts = context_for_tests(context_locations, test_locations)
    for test in tests_with_contexts:
        context = test[2] or ['None', None]
        index[test[0]] = [context[0], test[1], test[0], file] 
    return index
    
def context_for_tests(context_locations, test_locations):
    return_index = {}
    if len(context_locations) == 0:
        for test in test_locations:
            return_index[''] = return_index.get('') or []
            return_index.get('').append(['', test[1], test[2]])
        return return_index

    def interpolator(test):
        for context in reversed(context_locations):
            if test[1] > context[1]:
                return(test.append(context))
        return(test.append(None))
    [interpolator(test) for test in test_locations]
    return(test_locations)
        
    
    


