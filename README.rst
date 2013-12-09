Character Table
===============

Lookup (and Insert) Unicode Character
-------------------------------------

Press ``ctrl-k,ctrl-l`` to open unicode selection panel. There 
you can find any unicode character (except those categorized as "Other").  Character you select with ``<return>`` will be inserted. There are following columns:

- Unicode Character
- Unicode Character Code
- Mnemonic (if present), see `Character Mnemonics ("Digraphs")`_
- Unicode Character Name

In Sublime Text 3, there is also a preview for selected character.

Character Mnemonics ("Digraphs")
--------------------------------

Character Mnemonics are ASCII character sequences, which 
represent a unicode character.  Mostly they are digraphs (two-character sequences), but some of them are longer. You can use
digraphs to write unicode characters without having them present on your keyboard.

If you find "ze" in mnemonic column of unicode lookup panel,
you can type ``ctrl-k,z,e`` to insert the corresponding unicode
character.

Mnemonics are at least two letters.  If you find a one-letter 
mnemonic in unicode lookup panel, you have to type the letter 
and ``<space>`` to get the unicode character.  E.g. there is "a" in mnemonic column of unicode lookup panel, you have to type``ctrl-k,a,<space>`` to get the latin character "a"


Toggle Digraph Mode
-------------------

You can toggle digraph mode with ``ctrl-k,ctrl-t``, where any characters you type are interpreted as digraphs.


History
-------

Starting with a VIM-Digraph clone, I found it usable to have
a full unicode table accessible in a quick-panel and I also 
found out that there is rfc1345, which defines mnemonics for 
characters.

I started with a manual created sublime-keymap, but then I found out, that it is easier to generate it from unicodedata
and rfc1345.



