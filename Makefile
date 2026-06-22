# See LICENSE file for copyright and license details.

include config.mk

SRC = autoreload.c commands.c image.c main.c options.c thumbs.c util.c window.c wallpaper.c
OBJ = $(SRC:.c=.o)
ICONS = icon/16x16.png icon/32x32.png icon/48x48.png icon/64x64.png icon/128x128.png

all: options sxiv icon desktop

options:
	@echo sxiv build options:
	@echo "CFLAGS  = $(SXIVCFLAGS)"
	@echo "LDFLAGS = $(SXIVLDFLAGS)"
	@echo "CC      = $(CC)"

config.h:
	cp config.def.h $@


.c.o:
	$(CC) $(SXIVCFLAGS) -c -o $@ $<

window.o: icon/data.h

$(OBJ): commands.lst sxiv.h config.h config.mk

sxiv: $(OBJ)
	$(CC) -o $@ $(OBJ) $(SXIVLDFLAGS)

clean:
	rm -f sxiv $(OBJ) sxiv-$(VERSION).tar.gz *.o *.orig *.rej

dist: clean
	mkdir -p sxiv-${VERSION}
	cp -R LICENSE Makefile README config.def.h config.mk\
		sxiv.1 sxiv.h util8.h util.h ${SRC} sxiv.png sxiv-${VERSION}
	tar -cf sxiv-${VERSION}.tar sxiv-${VERSION}
	gzip sxiv-${VERSION}.tar
	rm -rf sxiv-${VERSION}

desktop:
	@echo "INSTALL sxiv.desktop"
	mkdir -p $(DESTDIR)$(PREFIX)/share/applications
	cp sxiv.desktop $(DESTDIR)$(PREFIX)/share/applications

icon:
	@echo "INSTALL icon"
	for f in $(ICONS); do \
		dir="$(DESTDIR)$(PREFIX)/share/icons/hicolor/$${f%.png}/apps"; \
		mkdir -p "$$dir"; \
		cp "icon/$$f" "$$dir/sxiv.png"; \
		chmod 644 "$$dir/sxiv.png"; \
	done

icon_cleanup:
	for f in $(ICONS); do \
		dir="$(DESTDIR)$(PREFIX)/share/icons/hicolor/$${f%.png}/apps"; \
		rm -f "$$dir/sxiv.png"; \
	done

install: all
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp -f sxiv $(DESTDIR)$(PREFIX)/bin/
	chmod 755 $(DESTDIR)$(PREFIX)/bin/sxiv
	mkdir -p $(DESTDIR)$(MANPREFIX)/man1
	sed "s!PREFIX!$(PREFIX)!g; s!VERSION!$(VERSION)!g" sxiv.1 >$(DESTDIR)$(MANPREFIX)/man1/sxiv.1
	chmod 644 $(DESTDIR)$(MANPREFIX)/man1/sxiv.1
	mkdir -p $(DESTDIR)$(PREFIX)/share/sxiv/exec
	cp exec/* $(DESTDIR)$(PREFIX)/share/sxiv/exec/
	chmod 755 $(DESTDIR)$(PREFIX)/share/sxiv/exec/*

uninstall: icon_cleanup
	rm -f $(DESTDIR)$(PREFIX)/bin/sxiv\
		rm -f $(DESTDIR)$(MANPREFIX)/man1/sxiv.1\
		rm -rf $(DESTDIR)$(PREFIX)/share/sxiv
	rm -f $(DESTDIR)$(PREFIX)/share/applications/sxiv.desktop

.PHONY: all clean install uninstall icon
