import zipfile
from lxml import html, etree
import re


class CapDrop:
	def __init__(self, filename, fontfile):
		self.inbook = zipfile.ZipFile(filename, 'r')
		self.outbook = zipfile.ZipFile('(NEW)_' + filename, 'w')

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
					if child.text and re.search(r"\w", child.text) and len(child.text) > 15:
						intro = child
						chosen = True
						break
				if chosen:
					break

		if chosen:
			cont = intro.text[0]
			tail = intro.text[1:]
			intro.text = ""

			dc_span = etree.Element("span")
			intro.insert(0, dc_span)
			dc_span.set("class", "dropcap")
			dc_span.text = cont
			dc_span.tail = tail

	def add_styledata(self):
		with open('resources/dropcap.css', 'r') as incss:
			self.outbook.writestr('dropcap.css', incss.read())
		
		self.outbook.write(self.fontfile, 'fonts/dropcap-font.ttf')

		content_file = [i for i in self.filelist if 'content.opf' in i][0]
		content = etree.fromstring(self.inbook.read('content.opf'))
		manif = content.xpath("//*[local-name()= 'manifest']")[0]

		itemfont = etree.SubElement(manif, "item")
		attr = itemfont.attrib
		itemfont.attrib.update({
			"id" : "dropcap-font",
			"href" : "fonts/dropcap-font.ttf",
			"media-type" : "application/x-font-truetype"
		})

		itemcss = etree.SubElement(manif, "item")
		itemcss.attrib.update({
			"id" : "dropcap-css",
			"href" : "dropcap.css",
			"media-type" : "text/css"
		})

		self.outbook.writestr('content.opf', etree.tostring(content))

	def edit_htmls(self):
		htmfiles = [i for i in self.filelist if 'htm' in i]

		for htmfile in htmfiles:
			tree = html.fromstring(self.inbook.read(htmfile))
			self.add_span(tree)

			head = tree.xpath("//head")[0]
			link = etree.SubElement(head, "link")
			link.attrib.update({
				"rel" : "stylesheet",
				"href" : "dropcap.css",
				"type" : "text/css"
			})

			self.outbook.writestr(htmfile, etree.tostring(tree))

	def complete(self):
		remfiles = [i for i in self.filelist if i not in self.outbook.namelist()]

		for file in remfiles:
			self.outbook.writestr(file, self.inbook.read(file))


drop = CapDrop('Lolita - Vladimir Nabokov.epub', 'resources/dropcap.ttf')