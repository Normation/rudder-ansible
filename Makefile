# Copyright: (c) 2021, Normation
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

PYTHON					:= python3
LINT					:= ansible-lint
GALAXY					:= ansible-galaxy

# Check if 'python3' binary is available in path
ifeq ($(origin PYTHON), undefined)
  PYTHON:=$(shell which python3)
endif
ifeq ($(PYTHON),)
  $(error Could not find 'python3' in path. Please install python3, or if already installed either add it to your path or set PYTHON to point to its directory)
endif

BUILD_DIR				:= "build"
VENV					:= "venv"
PROJECT_NAME			:= "normation-rudder"
PY_SOURCES				:= "normation/rudder/plugins/inventory/"
PROJECT_SOURCES			:= "normation/rudder"
COLLECTION_VERSION		:= $(shell cat normation/rudder/VERSION)
M						:= $(shell printf "\033[34;1m▶\033[0m")

# Add an @ if the value of v is 0, if it is 1 (for debugging),
# it automatically removes the @ and allows to see what is really done.
Q						:= $(if $(filter 1,$V),,@)
V						:= 0

# Defines the default target that `make` will to try to make,
# or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = help

.PHONY: help
help: ## Print help on Makefile
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@grep -hE '^[ a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-17s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

# Inclusion of makefiles to lighten it
include utils/make/Makefile.*

# -------------------------
# Requirements
# -------------------------

# Default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: utils/python/requirements/base-requirements.txt
	python3 -m venv $(VENV)
	$Q ./$(VENV)/bin/pip install \
	--disable-pip-version-check \
	-r $<

venv: $(VENV)/bin/activate

# -------------------------
# Build
# -------------------------

.PHONY: build-collection
build-collection: clean.venv venv | ; $(info $(M) Build Ansible Collection) @
	@echo "Build plugin version $(COLLECTION_VERSION)"
	cd $(PROJECT_SOURCES) && \
	rm -rf build/$(PROJECT_NAME)-$(COLLECTION_VERSION).tar.gz && \
	$(GALAXY) collection build -f  --output-path $(BUILD_DIR)

.PHONY: release
release: build-collection | ; $(info $(M) Build an release) @ ## Build an release

.PHONY: install
install: build-collection ## Install collection
	cd $(PROJECT_SOURCES) && \
	$(GALAXY) collection install $(BUILD_DIR)/$(PROJECT_NAME)-$(COLLECTION_VERSION).tar.gz

.PHONY: uninstall
uninstall: | ; $(info $(M) Uninstall collection) @ ## Uninstall collection
	$Q rm -rf ~/.ansible/collections/ansible_collections/normation

# -------------------------
# Clean
# -------------------------

.PHONY: clean.venv
clean.venv: | ; $(info $(M) Clean old virtual env) @
	$Q rm -rf $(VENV)

.PHONY: clean.project
clean.project:  | ; $(info $(M) Clean this project) @
	$Q find . -type f -name '*.pyc' -delete
	$Q find . -type f -name '*.pyo' -delete
	$Q find . -type d -name "__pycache__" | xargs rm -rf {};

.PHONY: clean.builds
clean.builds: | ; $(info $(M) Clean all generated builds) @
	$Q rm -f $(PROJECT_SOURCES)/$(BUILD_DIR)/*

.PHONY: clean.all
clean.all: clean.project clean.builds clean.venv

.PHONY: clean
clean: clean.all | ; $(info $(M) Clean this project and all generated builds) @ ## Clean this project and all generated builds (subtargets: clean.[all,project,builds,venv])

# -------------------------
# Misc
# -------------------------

.PHONY: lint.all
lint.all: lint.plugins lint.roles

.PHONY: lint
lint: lint.all | ; $(info $(M) Run all linters) @ ## Run all linters (subtargets: lint.[all,plugins,roles])

.PHONY: fmt.all
fmt.all: fmt.plugins fmt.roles

.PHONY: fmt
fmt: fmt.all | ; $(info $(M) Run all formaters) @ ## Run all formaters (subtargets: fmt.[all,plugins,roles])