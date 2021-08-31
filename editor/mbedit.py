import gi
import json
import re
import os, os.path
gi.require_version('Gtk', '3.0') 

from gi.repository import Gtk, Pango, GLib, GdkPixbuf



class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title = 'MBEdit', icon_name = "document-edit-symbolic", default_width = 1250, default_height = 750)
        
        self.connect("destroy", Gtk.main_quit)
        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.add(self.box)

        self.menuBar = Gtk.MenuBar()
        self.box.add(self.menuBar)

        self.fileMenu = Gtk.Menu()
        self.newItem = Gtk.MenuItem.new_with_label("New Book")
        self.openItem = Gtk.MenuItem.new_with_label("Open")
        self.saveItem = Gtk.MenuItem.new_with_label("Save")
        self.saveAsItem = Gtk.MenuItem.new_with_label("Save As")
        self.quitItem = Gtk.MenuItem.new_with_label("Quit")

        self.fileMenu.append(self.newItem)
        self.fileMenu.append(self.openItem)
        self.fileMenu.append(Gtk.SeparatorMenuItem())
        self.fileMenu.append(self.saveItem)
        self.fileMenu.append(self.saveAsItem)
        self.fileMenu.append(Gtk.SeparatorMenuItem())
        self.fileMenu.append(self.quitItem)

        
        self.editMenu = Gtk.Menu()
        self.undoItem = Gtk.MenuItem.new_with_label("Undo")
        self.redoItem = Gtk.MenuItem.new_with_label("Redo")
        self.insertMenu = Gtk.Menu()
        self.insertImageItem = Gtk.MenuItem.new_with_label("Image")
        self.insertTextItem = Gtk.MenuItem.new_with_label("Text")
        self.insertMenu.append(self.insertImageItem)
        self.insertMenu.append(self.insertTextItem)
        self.insertItem = Gtk.MenuItem(label = "Insert...", submenu = self.insertMenu)
        self.findItem = Gtk.MenuItem.new_with_label("Find")
        self.printItem = Gtk.MenuItem.new_with_label("Print")
        self.configItem = Gtk.MenuItem.new_with_label("Preferences")

        self.editMenu.append(self.undoItem)
        self.editMenu.append(self.redoItem)
        self.editMenu.append(Gtk.SeparatorMenuItem())
        self.editMenu.append(self.findItem)
        self.editMenu.append(self.printItem)
        self.editMenu.append(Gtk.SeparatorMenuItem())
        self.editMenu.append(self.insertItem)
        self.editMenu.append(Gtk.SeparatorMenuItem())
        self.editMenu.append(self.configItem)

        self.fileMenuItem = Gtk.MenuItem(label = "File", submenu = self.fileMenu)
        self.editMenuItem = Gtk.MenuItem(label = "Edit", submenu = self.editMenu)
        self.recipesMenuItem = Gtk.MenuItem(label = "Recipes")
        self.formatMenuItem = Gtk.MenuItem(label = "Format")

        self.menuBar.append(self.fileMenuItem)
        self.menuBar.append(self.editMenuItem)
        self.menuBar.append(self.recipesMenuItem)
        self.menuBar.append(self.formatMenuItem)
        

        self.show_all()

win = Window()
Gtk.main()
