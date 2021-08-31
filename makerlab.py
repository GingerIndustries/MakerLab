#! /usr/bin/python3

import gi
import json
import re
import os, os.path
gi.require_version('Gtk', '3.0') 

from gi.repository import Gtk, Pango, GLib, GdkPixbuf

VERSION = "1.0"

try:
	confFile = open("makerlab.conf", "r")
	conf = json.load(confFile)
	confFile.close()
except FileNotFoundError:
	confFile = open("makerlab.conf", "x")
	conf = {"darkmode": False, "fontsize": 1, "bookpaths": [".", "~/Documents/MakerBooks"]}
	
def getImgPaths(a):
	r = re.compile("<img .+?>")
	s = []
	e = 0
	while True:
		q = r.search(a, pos = e)
		if type(q) == type(None):
			break
		e = q.end()
		s.append(q)
	res = []
	for match in s:
		res.append((match.start()+2, match.group().split("<img ")[1][:-1]))
	return res

class SettingsBoxRow(Gtk.ListBoxRow):
	def __init__(self, contentWidget, label = None, labelWidget = None, activatable = False, selectable = False):
		Gtk.ListBoxRow.__init__(self)
		self.activatable = activatable
		self.selectable = selectable
		if label and labelWidget:
			raise ValueError("Cannot specify both label and labelWidget, it has to be one or the other!")
		if label:
			assert isinstance(label, str), "label must be a string!"
			self.label = Gtk.Label(label=label)
		if labelWidget:
			assert isinstance(labelWidget, Gtk.Widget), "labelWidget must be a Gtk.Widget or a subclass of it!"
			self.label = labelWidget
		assert isinstance(contentWidget, Gtk.Widget), "contentWidget must be a Gtk.Widget or a subclass of it!"
		
		self.label.props.xalign = 0
		self.box = Gtk.Box(spacing = 25)
		self.contentWidget = contentWidget
		self.contentWidget.props.valign = Gtk.Align.CENTER
		self.box.pack_start(self.label, True, True, 0)
		self.box.pack_start(self.contentWidget, False, True, 0)
		self.add(self.box)
		self.show_all()

class BooksWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title = 'MakerBook Configuration', icon_name = "accessories-dictionary", modal = True, resizable = False, default_width = 400, transient_for = parent)
		self.connect('delete-event', lambda w, e: w.hide() or True)
		
		self.contentBox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.contentBox.add(Gtk.Label(label="<span size='large'>MakerBook Configuration</span>", use_markup = True))
		self.contentBox.add(Gtk.Label(label="This is a list of directories where MakerLab\nwill look for MakerBook (.mb) files."))
		self.pathsListBox = Gtk.ListBox(margin = 10)
		self.pathsListBox.set_selection_mode(Gtk.SelectionMode.NONE)
		self.contentBox.add(self.pathsListBox)
		for path in conf["bookpaths"]:
			#editButton = Gtk.Button.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
			#editButton.connect("clicked", self.editBook)
			deleteButton = Gtk.Button.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
			deleteButton.connect("clicked", self.deleteBook)
			deleteButton.get_style_context().add_class("destructive-action")
			if path == ".":
				#editButton.set_sensitive(False)
				deleteButton.set_sensitive(False)
			buttonBox = Gtk.Box(spacing = 6)
			#buttonBox.add(editButton)
			buttonBox.add(deleteButton)
			self.pathsListBox.add(SettingsBoxRow(buttonBox, label = (os.path.expanduser(path) if path != "." else "(Installation folder)")))
		addItemButton = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
		addItemButton.connect("clicked", self.addBook)
		self.pathsListBox.add(addItemButton)
		self.add(self.contentBox)
		
	def editBook(self, button):
		pass
	def deleteBook(self, button):
		book = button.get_parent().get_parent().get_parent().label.get_text() # where have i seen this before
		dialog = Gtk.Dialog(use_header_bar = True)
		dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
		okButton = dialog.add_button("Remove", Gtk.ResponseType.OK)
		okButton.get_style_context().add_class("destructive-action")
		contentArea = dialog.get_content_area()
		deleteLabel = Gtk.Label(label = "Remove book path: " + book + "?\n(Changes take effect upon restart)")
		contentArea.add(deleteLabel)
		dialog.show_all()
		results = dialog.run()
		dialog.hide()
		if results == Gtk.ResponseType.OK:
			conf["bookpaths"].remove(book)
	def addBook(self, button):
		dialog = Gtk.Dialog(use_header_bar = True)
		dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
		okButton = dialog.add_button("Apply", Gtk.ResponseType.OK)
		okButton.get_style_context().add_class("suggested-action")
		contentArea = dialog.get_content_area()
		infoLabel = Gtk.Label(label = "Changes take effect upon restart.\nNonexistent directories will be created.\nUse \"~\" to represent the home directory.")
		pathEntry = Gtk.Entry(placeholder_text = "Directory path", max_length = 25, margin_bottom = 10, margin_end = 50)
		contentArea.add(infoLabel)
		contentArea.add(pathEntry)
		dialog.show_all()
		okButton.grab_focus()
		results = dialog.run()
		dialog.hide()
		if results == Gtk.ResponseType.OK:
			path = os.path.expanduser(pathEntry.get_text())
			if not os.path.isdir(path):
				os.makedirs(path)
			conf["bookpaths"].append(path)
	def show(self, *args):
		self.set_position(Gtk.WindowPosition.CENTER)
		super().show_all()

class SettingsWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title = 'Settings', icon_name = "preferences-system", modal = True, resizable = False, default_width = 350, transient_for = parent)
		self.connect('delete-event', lambda w, e: w.hide() or True)
		self.bookConfig = BooksWindow(parent=self)
		self.about = Gtk.AboutDialog(authors = ["The Ginger"], title = "About MakerLab", program_name = "MakerLab", version = "Version " + VERSION, logo_icon_name = "application-x-appliance-symbolic", wrap_license = True, comments = "A sort of digital cookbook for anything", copyright = "Copyright Ginger Industries 2021. See license for more details.", license = open("LICENSE", "r").read())
		
		self.contentBox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.contentBox.add(Gtk.Label(label="<span size='large'>Settings</span>", use_markup = True))
		self.settingsListBox = Gtk.ListBox(margin = 10)
		self.settingsListBox.set_selection_mode(Gtk.SelectionMode.NONE)
		
		self.bookConfigButton = Gtk.Button(label = "Books  ", image = Gtk.Image.new_from_icon_name("view-dual-symbolic", Gtk.IconSize.LARGE_TOOLBAR), image_position = Gtk.PositionType.RIGHT, always_show_image = True)
		self.bookConfigButton.connect("clicked", self.bookConfig.show)
		self.bookConfigRow = SettingsBoxRow(self.bookConfigButton, label = "Configure MakerBooks")
		windowSettings = Gtk.Settings.get_default()
		self.themeSwitch = Gtk.Switch()
		self.themeSwitch.set_active(conf["darkmode"])
		windowSettings.set_property("gtk-application-prefer-dark-theme", conf["darkmode"])
		def z(x, y):
			windowSettings.set_property("gtk-application-prefer-dark-theme", y)
			conf["darkmode"] = y
		self.themeSwitch.connect("state-set", z)
		self.themeRow = SettingsBoxRow(self.themeSwitch, label = "Dark mode")
		self.fontSizeSpinBox = Gtk.SpinButton(adjustment = Gtk.Adjustment(lower = 6, upper = 20, step_increment = 1), value = conf["fontsize"] * 10)
		def u(d):
			parent.fontSizeTag.props.scale = int(d.get_text()) / 10
			conf["fontsize"] = int(d.get_text()) / 10
		self.fontSizeSpinBox.connect("value-changed", u)
		self.fontSizeRow = SettingsBoxRow(self.fontSizeSpinBox, label = "Font size")
		self.aboutButton = Gtk.Button.new_from_icon_name("help-about", Gtk.IconSize.LARGE_TOOLBAR)
		self.aboutButton.connect("clicked", self.showAbout)
		self.aboutRow = SettingsBoxRow(self.aboutButton, label = "About")
		
		self.settingsListBox.add(self.bookConfigRow)
		self.settingsListBox.add(self.themeRow)
		self.settingsListBox.add(self.fontSizeRow)
		self.settingsListBox.add(self.aboutRow)
		
		self.contentBox.add(self.settingsListBox)
		self.add(self.contentBox)
		self.show_all()
		self.hide()
	
	def showAbout(self, widget):
		self.about.run()
		self.about.hide()
	
	def show(self):
		self.set_position(Gtk.WindowPosition.CENTER)
		super().show()

def destroy(x):
	confFile = open("makerlab.conf", "w")
	json.dump(conf, confFile)
	confFile.close()
	Gtk.main_quit()
	return True

class Window(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title = 'MakerLab', icon_name = "application-x-appliance-symbolic", default_width = 1250, default_height = 750)
		
		self.connect("destroy", destroy)
		self.chemibook = None
		self.nameKey = {}
		self.settingsWindow = SettingsWindow(self)
		
		self.header = Gtk.HeaderBar(show_close_button=True, has_subtitle=True, title="MakerLab", decoration_layout="icon:minimize,maximize,close")
		self.settingsButton = Gtk.Button.new_from_icon_name("applications-system-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
		self.printButton = Gtk.Button.new_from_icon_name("document-print-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
		self.settingsButton.set_relief(Gtk.ReliefStyle.NONE)
		self.settingsButton.set_size_request(45, -1)
		self.settingsButton.connect("clicked", lambda x: self.settingsWindow.show())
		self.printButton.set_relief(Gtk.ReliefStyle.NONE)
		self.printButton.set_size_request(45, -1)
		self.header.pack_end(self.settingsButton)
		self.header.pack_end(self.printButton)
		self.set_titlebar(self.header)
		
		self.printDialog = Gtk.PrintOperation()
		self.printDialog.connect("draw-page", self.printHandler)
		
		self.contentBox = Gtk.Box()
		
		self.recipesListStackBox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.recipesListStack = Gtk.Stack()
		self.recipesListStackSwitcher = Gtk.StackSwitcher(stack = self.recipesListStack)
		self.recipesListStack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
		self.recipesListStack.set_transition_duration(500)
		self.recipesListStackBox.add(self.recipesListStackSwitcher)
		self.recipesListStackBox.add(self.recipesListStack)
		self.contentBox.pack_start(self.recipesListStackBox, False, True, 0)
		
		self.recipeScroll = Gtk.ScrolledWindow(propagate_natural_height = True, propagate_natural_width = False, margin = 4, overlay_scrolling = False, vexpand = True, vexpand_set = True)
		self.recipeBuffer = Gtk.TextBuffer()
		self.centerTag = self.recipeBuffer.create_tag("title", justification = Gtk.Justification.CENTER, scale = 3, weight = 500)
		self.fontSizeTag = self.recipeBuffer.create_tag("fontSize", scale = conf["fontsize"])
		self.recipeTextView = Gtk.TextView(buffer = self.recipeBuffer, wrap_mode = Gtk.WrapMode.WORD_CHAR, vexpand = True, vexpand_set = True, margin = 4, cursor_visible = False, editable = False)
		self.recipeScroll.add(self.recipeTextView)
		self.contentBox.pack_start(self.recipeScroll, True, True, 0)
		
		self.recipeBuffer.set_text("MAKERLAB")
		_ = self.recipeBuffer.get_start_iter()
		_.forward_chars(8)
		self.recipeBuffer.apply_tag_by_name("title", self.recipeBuffer.get_start_iter(), _)
		self.recipeBuffer.insert_markup(_, "\n\nWelcome to <b>MakerLab!</b> Select a recipe to get started.", -1)
		_ = self.recipeBuffer.get_start_iter()
		_.forward_chars(8)
		self.recipeBuffer.apply_tag_by_name("fontSize", _, self.recipeBuffer.get_end_iter())
		self.add(self.contentBox)
		self.show_all()
		self.loadRecipes()
	
	def printHandler(self, dialog, context, n):
		#ctx = context.
		pass
	
	def buildBook(self, parent, name, title):
		treeStore = Gtk.TreeStore(str, str)
		recipesList = Gtk.TreeView(model = treeStore)


		recipesList.connect("row-activated", self.loadRecipe)
		renderer = Gtk.CellRendererText(ellipsize = Pango.EllipsizeMode.END)
		titleColumn = Gtk.TreeViewColumn("Title", renderer, text = 0)
		titleColumn.props.expand = True
		difficultyColumn = Gtk.TreeViewColumn("Difficulty", renderer, text = 1)
		difficultyColumn.props.alignment = 1.0
		recipesList.append_column(titleColumn)
		recipesList.append_column(difficultyColumn)
		recipesListFrame = Gtk.ScrolledWindow(propagate_natural_height = True, propagate_natural_width = True, margin = 4, min_content_height = 300, min_content_width = 500, max_content_width = 400, overlay_scrolling = False, vexpand = True, vexpand_set = True)
		recipesListFrame.add(recipesList)
		parent.add_titled(recipesListFrame, name, title)
		parent.show_all()
		return treeStore
	
	def loadRecipes(self):
		def fail(self, error, path):
			dialog = Gtk.MessageDialog(
				transient_for=self,
				flags=0,
				message_type=Gtk.MessageType.ERROR,
				buttons=Gtk.ButtonsType.CLOSE,
				text="Unable to load MakerBook!",
				title = "Unable to load MakerBook",
				icon_name = "dialog-error"
			)
			dialog.format_secondary_text(
				"Failed to load MakerBook at:\n" + path + "\nwith error:\n" + str(error)
			)
			dialog.run()
			dialog.destroy()
			Gtk.main_quit()
			exit(-2)
		for path in conf["bookpaths"]:
			if not os.path.isdir(os.path.expanduser(path)):
				os.makedirs(os.path.expanduser(path))
			for item in os.scandir(os.path.expanduser(path)):
				if os.path.splitext(item.name)[1] == ".mb":
					try:
						chemibook = json.load(open(item.path, "r"))
						treeStore = self.buildBook(self.recipesListStack, item.name, chemibook["header"]["name"])
						
						for category in chemibook:
							if category == "header":
								continue
							recipes = treeStore.append(None, [chemibook[category]["name"], ""])
							for recipe in chemibook[category]:
								if recipe == "name":
									continue
								recipeData = chemibook[category][recipe]
								recipeData["dir"] = os.path.expanduser(path)
								treeStore.append(recipes, [recipeData["name"], recipeData["difficulty"]])
								self.nameKey[recipeData["name"]] = recipeData
					except Exception as e:
						GLib.idle_add(lambda: fail(self, e, os.path.abspath(item.path)))
						self.hide()
						Gtk.main()
	def loadRecipe(self, widget, path, column):
		try:
			data = self.nameKey[widget.props.model[path][0]]
		except KeyError:
			return
		os.chdir(data["dir"])
		self.recipeBuffer.set_text(data["name"])
		instructions = data["instructions"]
		instructions = re.sub("<img.+?>", "", instructions)

		self.recipeBuffer.insert_markup(self.recipeBuffer.get_end_iter(), "\n\n" + instructions, -1)
		for match in getImgPaths(data["instructions"]):
			p = self.recipeBuffer.get_start_iter()
			p.set_offset(len(data["name"]) + match[0])
			self.recipeBuffer.insert_pixbuf(p, GdkPixbuf.Pixbuf.new_from_file(match[1]))

		_ = self.recipeBuffer.get_start_iter()
		_.forward_chars(len(data["name"]))
		self.recipeBuffer.apply_tag_by_name("title", self.recipeBuffer.get_start_iter(), _)
		self.recipeBuffer.apply_tag_by_name("fontSize", _, self.recipeBuffer.get_end_iter())


win = Window()
win.set_position(Gtk.WindowPosition.CENTER)
Gtk.main()
