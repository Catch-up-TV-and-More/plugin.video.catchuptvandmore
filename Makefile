export PYTHONPATH := $(CURDIR)/resources/lib:$(CURDIR)/tests
PYTHON := python
KODI_PYTHON_ABIS := 3.0.0 2.25.0

name = $(shell xmllint --xpath 'string(/addon/@id)' addon.xml)
version = $(shell xmllint --xpath 'string(/addon/@version)' addon.xml)
git_branch = $(shell git rev-parse --abbrev-ref HEAD)
git_hash = $(shell git rev-parse --short HEAD)
matrix = $(findstring $(shell xmllint --xpath 'string(/addon/requires/import[@addon="xbmc.python"]/@version)' addon.xml), $(word 1,$(KODI_PYTHON_ABIS)))

ifdef release
	zip_name = $(name)-$(version).zip
else
	zip_name = $(name)-$(version)-$(git_branch)-$(git_hash).zip
endif
zip_dir = $(name)/

languages = $(filter-out en_gb, $(patsubst resources/language/resource.language.%, %, $(wildcard resources/language/*)))

path := /

blue = \e[1;34m
white = \e[1;37m
reset = \e[0;39m

all: check test build
zip: build
test: check test-unit test-service test-run

check: check-pylint check-translations

check-pylint:
	@printf "$(white)=$(blue) Starting sanity pylint test$(reset)\n"
	$(PYTHON) -m pylint resources/lib/ tests/

check-translations:
	@printf "$(white)=$(blue) Starting language test$(reset)\n"
	@-$(foreach lang,$(languages), \
		msgcmp resources/language/resource.language.$(lang)/strings.po resources/language/resource.language.en_gb/strings.po; \
	)

check-addon: clean
	@printf "$(white)=$(blue) Starting sanity addon tests$(reset)\n"
	kodi-addon-checker . --branch=krypton
	kodi-addon-checker . --branch=leia

kill-proxy:
	-pkill -ef '$(PYTHON) -m proxy'

unit: test-unit
run: test-run

test-unit: clean kill-proxy
	@printf "$(white)=$(blue) Starting unit tests$(reset)\n"
	-$(PYTHON) -m proxy --hostname 127.0.0.1 --log-level DEBUG &
	$(PYTHON) -m unittest discover -v
	-pkill -ef '$(PYTHON) -m proxy'

test-service:
	@printf "$(white)=$(blue) Run service$(reset)\n"
	$(PYTHON) resources/lib/service_entry.py

test-run:
	@printf "$(white)=$(blue) Run CLI$(reset)\n"
	$(PYTHON) tests/run.py $(path)

profile:
	@printf "$(white)=$(blue) Profiling $(white)$(path)$(reset)\n"
	$(PYTHON) -m cProfile -o profiling_stats-$(git_branch)-$(git_hash).bin tests/run.py $(path)

build: clean
	@printf "$(white)=$(blue) Building new package$(reset)\n"
	@rm -f ../$(zip_name)
	@git archive --format zip --worktree-attributes -v -o ../$(zip_name) --prefix $(zip_dir) $(or $(shell git stash create), HEAD)
	@printf "$(white)=$(blue) Successfully wrote package as: $(white)../$(zip_name)$(reset)\n"

multizip: clean
	@-$(foreach abi,$(KODI_PYTHON_ABIS), \
		printf "cd /addon/requires/import[@addon='xbmc.python']/@version\nset $(abi)\nsave\nbye\n" | xmllint --shell addon.xml; \
		matrix=$(findstring $(abi), $(word 1,$(KODI_PYTHON_ABIS))); \
		if [ $$matrix ]; then version=$(version)+matrix.1; else version=$(version); fi; \
		printf "cd /addon/@version\nset $$version\nsave\nbye\n" | xmllint --shell addon.xml; \
		make build; \
	)

clean:
	@printf "$(white)=$(blue) Cleaning up$(reset)\n"
	find . -name '*.py[cod]' -type f -delete
	find . -name '__pycache__' -type d -delete
	rm -rf .pytest_cache/
	rm -f *.log tests/userdata/tokens/*.tkn
