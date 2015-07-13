from lxml import etree, html
import re

def add_span(tree):
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


	print intro.get("class")
	print intro.text
	cont = intro.text[0]
	tail = intro.text[1:]
	intro.text = ""

	dc_span = etree.Element("span")
	intro.insert(0, dc_span)
	dc_span.set("class", "dropcap")
	dc_span.text = cont
	dc_span.tail = tail

	with open('opt.html', 'w') as op:
		op.write(etree.tostring(tree))


with open("Do_Androids_-Electric_Sheep_split_005.html", 'r') as htm:
	tree = html.fromstring(htm.read())

add_span(tree)