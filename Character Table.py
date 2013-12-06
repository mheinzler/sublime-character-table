import sublime_plugin, sublime, os, sys
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


class DigraphLookupCommand(sublime_plugin.WindowCommand):
    def run(self):
        is_digraph_spec = False

        s = sublime.load_binary_resource('Packages/Character Table/README.rst').decode('utf-8')

        options = []

        for line in s.splitlines():
            if not line: continue

            if is_digraph_spec:

                #import spdb ; spdb.start()
                if line.startswith("==== ======") or line.startswith("char "):
                    is_digraph_spec = False
                    continue

                try:
                    char, digraph, hex, decimal, desc = line.split(None, 4)
                except:
                    continue

                if line.startswith("\\"):
                    char = line[1]

                if u"MIDLINE HORIZONTAL ELLIPSIS" in desc:
                    digraph = u". "

                hex = hex.replace("0x", "00")

                options.append(u"%s %s U+%s %s" % (char, digraph, hex, desc))

            if line.startswith("==== ======"):
                is_digraph_spec = True
                continue

        def on_done(index):
            if index > -1:
                self.window.active_view().run_command("insert", {"characters": options[index][0]})

        #import spdb ; spdb.start()
        self.window.show_quick_panel(options, on_done, sublime.MONOSPACE_FONT)

class UnicodeLookupCommand(sublime_plugin.WindowCommand):
    def run(self):
        s = load_resource('UnicodeData.txt')
        rfc1345 = load_resource("rfc1345.txt")

        mnemonics = {}
        for line in rfc1345.splitlines():
            if len(line) < 4: continue
            if line[0] != " ": continue
            if line[1] == " ": continue

            mnemonic, number, iso_name = line[1:].split(None, 2)
            if len(mnemonic) == 1:
                mnemonic += " "
            mnemonics[iso_name] = mnemonic

        #import spdb ; spdb.start()

        import csv, unicodedata
        unicodedata_reader = csv.reader(s.splitlines(), delimiter=";", )

        unicode_data = []
        for row in unicodedata_reader:
            iso_name = row[1]

            # skip chars from "Other" Category
            if row[2].startswith("C"): continue

            try:
                unicode_data.append(u"%s U+%s %s %s" % (
                    unicodedata.lookup(iso_name), 
                    row[0],
                    mnemonics.get(iso_name, "  "),
                    iso_name,
                    ))

            except Exception as e:
                sys.stderr.write("Error processing %s: %s\n" % (row, e))
                continue

        def on_done(index):
            if index > -1:
                self.window.active_view().run_command("insert", {"characters": unicode_data[index][0]})

        #import spdb ; spdb.start()
        self.window.show_quick_panel(unicode_data, on_done, sublime.MONOSPACE_FONT)



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

if 0:
  class DigraphInsertInInsertModeCommand(sublime_plugin.TextCommand):

    def run(self, edit, characters=""):
        settings = view.settings()
        if 'Vintage' not in settings.get('ignored_packages'):
            if not settings.get('command_mode'):
                return

        self.view.run_command('insert', {'characters': characters})

