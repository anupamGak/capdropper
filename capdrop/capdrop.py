import zipfile
from lxml import html, etree
import re
from os.path import *


class CapDrop:
	def __init__(self, filename, fontfile):
		self.inbook = zipfile.ZipFile(filename, 'r')
		newbase = "(NEW)_" + basename(filename)
		self.outbook = zipfile.ZipFile(join(dirname(filename), newbase), 'w')

		self.filelist = self.inbook.namelist()
		self.fontfile = fontfile

		self.add_styledata()
		self.edit_htmls()
		self.complete()

	def add_span(self, tree):
		paras = tree.xpath("//p")

		chosen = False
		for para in paras[:4]:
			if para.text and len(para.text) > 20:
				intro = para
				chosen = True
				break
			else:
				for child in para.xpath("descendant::*"):
					if child.text and re.search(r"\w", child.text) and len(child.text) > 50:
						intro = child
						chosen = True
						break
				if chosen:
					break

		if chosen:
			pos = re.search(r"\S",intro.text).start()
			cont = intro.text[pos:pos+1]
			tail = intro.text[pos+1:]
			intro.text = ""

			dc_span = etree.Element("span")
			intro.insert(0, dc_span)
			dc_span.set("class", "dropcap")
			dc_span.text = cont
			dc_span.tail = tail

	def add_styledata(self):
		with open('resources/dropcap.css', 'r') as incss:
			self.outbook.writestr('dropcap-adder/dropcap.css', incss.read())
		
		self.outbook.write(self.fontfile, 'dropcap-adder/fonts/dropcap-font.ttf')

		content_file = [i for i in self.filelist if 'content.opf' in i][0]
		with self.inbook.open(content_file, 'r') as cxml:
			line = cxml.readline()
		content = html.fromstring(self.inbook.read(content_file))
		manif = content.xpath("//manifest")[0]

		itemfont = etree.SubElement(manif, "item")
		attr = itemfont.attrib
		itemfont.attrib.update({
			"id" : "dropcap-font",
			"href" : relpath("dropcap-adder/fonts/dropcap-font.ttf", content_file)[3:],
			"media-type" : "application/x-font-truetype"
		})
		itemcss = etree.SubElement(manif, "item")
		itemcss.attrib.update({
			"id" : "dropcap-css",
			"href" : relpath("dropcap-adder/dropcap.css", content_file)[3:],
			"media-type" : "text/css"
		})

		self.outbook.writestr(content_file, line + etree.tostring(content))

	def edit_htmls(self):
		htmfiles = [i for i in self.filelist if 'htm' in i]

		for htmfile in htmfiles:
			tree = html.fromstring(self.inbook.read(htmfile))
			self.add_span(tree)

			head = tree.xpath("//head")[0]
			link = etree.SubElement(head, "link")
			link.attrib.update({
				"rel" : "stylesheet",
				"href" : relpath("dropcap-adder/dropcap.css", htmfile)[3:],
				"type" : "text/css"
			})

			self.outbook.writestr(htmfile, etree.tostring(tree))

	def complete(self):
		remfiles = [i for i in self.filelist if i not in self.outbook.namelist()]

		for file in remfiles:
			self.outbook.writestr(file, self.inbook.read(file))

		print "File writing completed"


drop = CapDrop("samples/Do Androids Dream of Electric Sheep - Philip K. Dick.epub", 'resources/dropcap.ttf')
drop2 = CapDrop("samples/Lolita - Vladimir Nabokov.epub", 'resources/dropcap.ttf')
drop3 = CapDrop("samples/Philip Reeve - [Mortal Engines 05 - Fever Crumb 01] - Fever Crumb (epub).epub", 'resources/dropcap.ttf')