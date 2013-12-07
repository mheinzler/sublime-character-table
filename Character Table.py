import sublime_plugin, sublime, os, sys, json
ST3 = sublime.version() >= '3000'

def load_resource(name, encoding="utf-8"):
    if ST3:
        return sublime.load_resource("Packages/Character Table/"+name)
    else:
        fn = os.path.join(sublime.packages_path(), 'Character Table', name)
        with open(fn, "r") as f:
            return f.read().decode(encoding)

def load_binary_resource(name):
    if ST3:
        return sublime.load_binary_resource("Packages/Character Table/"+name)
    else:
        fn = os.path.join(sublime.packages_path(), 'Character Table', name)
        with open(fn, "rb") as f:
            return f.read()

class UnicodeLookupCommand(sublime_plugin.WindowCommand):
    def run(self):
        def on_done(index):
            if index > -1:
                self.window.active_view().run_command("insert", {"characters": UNICODE_DATA[index][0]})

        preview = self.window.create_output_panel("unicode_preview")

        preview.settings().set("font_size", 72)
        self.window.run_command("show_panel", {"panel": "output.unicode_preview"})

        def on_highlighted(index):
            char = UNICODE_DATA[index][0]
            preview.run_command("select_all")
            preview.run_command("insert", {"characters": char})

        self.window.show_quick_panel(UNICODE_DATA, on_done, 
            sublime.MONOSPACE_FONT, -1, on_highlighted)



ALL_DIGRAPH = False

class DigraphToggleCommand(sublime_plugin.ApplicationCommand):
    def is_checked(self):
        return ALL_DIGRAPH

    def run(self):
        toggle_digraph(sublime.active_window().active_view())


def toggle_digraph(view, set_state=True):
    dir = sublime.packages_path()
    user_digraph_path = os.path.join(dir, 'User', 'Character Table')
    extreme_digraph = os.path.join(user_digraph_path, 'Default.sublime-keymap')

    global ALL_DIGRAPH

    if os.path.exists(extreme_digraph):
        os.remove(extreme_digraph)
        os.rmdir(user_digraph_path)
        if set_state:
            ALL_DIGRAPH = False

    elif ST3:
        s = sublime.load_binary_resource('Packages/Character Table/Extreme-Keymap.json')
        os.mkdir(user_digraph_path)
        with open(extreme_digraph, 'wb') as f:
            f.write(s)
        if set_state:
            ALL_DIGRAPH = True

    else:
        import shutil
        os.mkdir(user_digraph_path)
        shutil.copy(
            os.path.join(dir, 'Character Table', 'Extreme-Keymap.json'),
            extreme_digraph
            )
        if set_state:
            ALL_DIGRAPH = True

    if set_state:
        digraph_set_status(view)

def digraph_set_status(view):
    if ALL_DIGRAPH:
        view.set_status('digraph', 'digraph (ctrl+k,ctrl+t to quit)')
    else:
        view.set_status('digraph', '')
        view.erase_status('digraph')

class DigraphListener(sublime_plugin.EventListener):

    def on_activated(self, view):
        digraph_set_status(view)

RFC1345_MNEMONICS = {}
UNICODE_DATA = []

def load_character_table():
    s = load_resource('UnicodeData.txt')
    rfc1345 = load_resource("rfc1345.txt")

    mnemonics = RFC1345_MNEMONICS
    mnemonics.clear()
    for line in rfc1345.splitlines():
        if len(line) < 4: continue
        if line[0] != " ": continue
        if line[1] == " ": continue

        mnemonic, number, iso_name = line[1:].split(None, 2)
        if len(mnemonic) == 1:
            mnemonic += " "
        try:
            char = eval( ('u"\\U%08s"'%number).replace(" ", "0") )
        except:
            sys.stderr.write("Error decoding: %s, %s\n" % (number, iso_name))
        mnemonics[char] = mnemonic

    import csv, unicodedata
    unicodedata_reader = csv.reader(s.splitlines(), delimiter=";", )

    unicode_data = UNICODE_DATA
    unicode_data[:] = []
    for row in unicodedata_reader:
        iso_name = row[1]

        # skip chars from "Other" Category
        if row[2].startswith("C"): continue

        try:
            char = eval( ('u"\\U%08s"'%row[0]).replace(" ", "0") )
            unicode_data.append(u"%s U+%s %s %s" % (
                char,
                row[0],
                mnemonics.get(char, "  "),
                iso_name,
                ))

        except Exception as e:
            sys.stderr.write("Error processing %s: %s\n" % (row, e))
            continue

ADD_REVERSED_MNEMONICS = True

def plugin_loaded():
    load_character_table()
    user_dir = os.path.join(sublime.packages_path(), 'User', "Character Table", "Default")

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    def makekeydef(chars, unichr):
        return {
            "keys": ["ctrl+k"]+[x for x in chars],
            "command": "insert",
            "args": {"characters": unichr},
        }

    keymap = []

    import unicodedata, re

    mnemonics = set(RFC1345_MNEMONICS.values())

    for k,v in RFC1345_MNEMONICS.items():

        if ADD_REVERSED_MNEMONICS:
            if len(v) == 2:
                rev = "".join([ x for x in reversed(v)])
                if rev[0] != " " and rev not in mnemonics:
                    keymap.append(makekeydef(rev, k))

        keymap.append(makekeydef(v, k))

    fn = os.path.join(user_dir, "Default.sublime-keymap")
    with open(fn+'.tmp', "w") as f:
        json.dump(keymap, f, indent=4, ensure_ascii=False)
    os.rename(fn+'.tmp', fn)

if not ST3:
    plugin_loaded()