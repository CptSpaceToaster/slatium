################################################################################
# Aecko Project Makefile
#   Author: CptSpaceToaster
#   Email:  CptSpaceToaster@gmail.com
################################################################################
# Quick Start Guide:
#   TODO:

######### Fallen and can't get back up? #########
.PHONY: help
help:
	@echo "Quick reference for supported build targets."
	@echo "----------------------------------------------------"
	@echo "  help                          Display this message."
	@echo "----------------------------------------------------"
	@echo "  check-tools                   Check if this user has required build tools in its PATH."
	@echo "  hooks                         Install some useful git-hooks to help ensure safe commits."
	@echo "----------------------------------------------------"
	@echo "  test                          Run some tests!"
	@echo "----------------------------------------------------"
	@echo "  clean-all                     Clean everything!"
	@printf "  %-30s" "clean-$(VENV)"
	@echo "Clean the virtual environment, and start anew."
	@echo "  clean-hooks                   Clean and uninstall the git-hooks"
	@echo "  clean-pycache                 Clean up python's compiled bytecode objects in the package"

################################################################################
include config.mk

.PHONY: check-tools
check-tools: $(TOOL_DEPS)
check-%:
	@printf "%-15s" "$*"
	@command -v "$*" &> /dev/null; \
	if [[ $$? -eq 0 ]] ; then \
		echo -e $(GRN)"OK"$(NC); \
		exit 0; \
	else \
		echo -e $(RED)"Missing"$(NC); \
		exit 1; \
	fi

######### Virtual Environment #########
$(VENV) $(PYTHON):
	$(MAKE) check-tools
	test -d $(VENV) || python3.4 -m venv --without-pip $(VENV)

######### Pip #########
$(PIP): $(PYTHON)
	wget $(PIP_URL) -O - | $(PYTHON)

# This creates a dotfile for the requirements, indicating that they were installed
.$(REQUIREMENTS): $(PIP) $(REQUIREMENTS)
	test -s $(REQUIREMENTS) && $(PIP) install -Ur $(REQUIREMENTS) || :
	touch .$(REQUIREMENTS)

######### Git Hooks #########
.PHONY: hooks
hooks: $(GIT_HOOKS)

.git/hooks/%: hooks/%
	ln -s ../../$< $@

######### Tests #########
.PHONY: test
test: $(PYTHON) .$(REQUIREMENTS)
	$(PYTHON) -m unittest discover -s $(PACKAGE)
	$(PYTHON) setup.py check --strict --restructuredtext

######### Release #########
.PHONY: list-sources
list-sources:
	@echo $(SOURCES)
	@echo $(REPO_HOOKS)
	@echo $(GIT_HOOKS)

.PHONY: build
build: .build
.build: $(PYTHON) .$(REQUIREMENTS) $(SOURCES) setup.py
	$(PYTHON) setup.py build
	touch .build

.PHONY: install
install: .install
.install: .build
	$(PYTHON) setup.py install
	touch .install
	@echo -e "Installed locally in "$(GRN)$(VENV)"/bin/"$(PACKAGE)$(NC)
	@command -v "xclip" &> /dev/null; \
	if [[ $$? -eq 0 ]] ; then \
		echo "$(VENV)"/bin/"$(PACKAGE)" | xclip -selection c; \
	fi

.PHONY: register
register: .register
.register: $(PYTHON) .$(REQUIREMENTS) $(SOURCES) setup.py
	$(PYTHON) setup.py register --strict
	touch .register

.PHONY: upload
upload: .upload
.upload: .build .register $(PYTHON) .$(REQUIREMENTS) $(SOURCES) setup.py
	# TODO: bdist_wininst
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_wheel upload
	touch .upload

######### Cleaning supplies #########
.PHONY: clean
clean:
ifneq ("$(wildcard .build)","")
	$(PYTHON) setup.py clean
endif
	rm -rf .build
	rm -rf .install
	rm -rf .upload

.PHONY: clean-all
clean-all: clean clean-$(VENV) clean-hooks clean-pycache

.PHONY: clean-$(VENV)
clean-$(VENV):
	rm -rf $(VENV)
	rm -rf .$(REQUIREMENTS)

.PHONY: clean-hooks
clean-hooks:
	rm -rf $(GIT_HOOKS)

.PHONY: clean-pycache
clean-pycache:
	find -path "*/__pycache__/*" -not -path "*/venv/*" -delete
	find -name "__pycache__" -not -path "*/venv/*" -type d -delete
