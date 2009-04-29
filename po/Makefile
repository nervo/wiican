#!/usr/bin/make -f

PROJECT = wiican

GETTEXT = /usr/bin/xgettext
MSGMERGE = /usr/bin/msgmerge

PO = $(shell find . -name *.po -print | sed -e 's!./!!g')

update-po:
	$(GETTEXT) -f POTFILES -d $(PROJECT) -o $(PROJECT).pot
	for lang in $(PO); do $(MSGMERGE) -U $$lang $(PROJECT).pot; done 
