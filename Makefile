# Quadplay workflow /utility makefile
#
# Update sprite sheets, package release builds, push test builds hosted on
# github.io for sharing with folks, more.
#
# expected to be in Makefile.defs:
#
# ITCH_RELEASE_USER - itch.io username of the person uploading to itch
# GITHUB_USERNAME   - github username of the person hosting the deployment repo
# DEPLOY_REPO_NAME  - github repo name of the deployment repository

mkfile_path := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

include $(mkfile_path)/Makefile.defs

GAME_JSON ?= $(shell ls -1 *.game.json)
GAME_NAME ?= $(shell echo $(GAME_JSON) | cut -f 1 -d "." )

GIT ?= git
GITSTATUS = $(shell git diff-index --quiet HEAD . 1>&2 2> /dev/null; echo $$?)
DEV_BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
DEPLOY_BRANCH ?= $(GAME_NAME).DEPLOY

ALLOW_ITCH_RELEASE ?= false
ITCH_GAME_NAME ?= $(GAME_NAME)
ITCH_RELEASE_FILE ?= $(ITCH_GAME_NAME).$(GAME_VERSION).zip

DEPLOY_REMOTE ?= git@github.com:$(GITHUB_USERNAME)/$(DEPLOY_REPO_NAME).git

# assumes running inside the `quadplay` distribution
QUADPLAY_TOOLS_DIR ?= $(shell git rev-parse --show-toplevel)/tools
LINTER ?= $(QUADPLAY_TOOLS_DIR)/project_linter.py

GAME_VERSION ?= $(shell \
				env PYTHONPATH=$(PYTHONPATH):$(QUADPLAY_TOOLS_DIR) \
				python -c "import workjson as json;\
				print(json.load('$(GAME_JSON)')['version'])"\
				)

EXPORT_DIR ?= /var/tmp/$(GAME_NAME)

COLOR_GREEN=\033[0;32m
COLOR_RED=\033[0;31m
COLOR_BLUE=\033[0;34m
COLOR_RESET=\033[0m

all: update_sprites download_levels

update_sprites:
	@echo "$(COLOR_GREEN)Updating all sprites... $(COLOR_RESET)"
	@$(QUADPLAY_TOOLS_DIR)/sprite_json_generator.py -u

download_levels:
ifneq (,$(wildcard download_level.py))
	@python3 download_level.py
endif

info_dump:
	@echo "$(COLOR_GREEN)"
	@echo "Settings: "
	@echo "$(COLOR_RESET)"
	@echo "GAME_NAME = $(GAME_NAME)"
	@echo "GAME_VERSION = $(GAME_VERSION)"
	@echo "ITCH_RELEASE_USER = $(ITCH_RELEASE_USER)"
	@echo "GITHUB_USERNAME = $(GITHUB_USERNAME)"
	@echo "DEPLOY_REPO_NAME = $(DEPLOY_REPO_NAME)"
	@echo "EXPORT_DIR = $(EXPORT_DIR)"
	@echo "QUADPLAY_TOOLS_DIR = $(QUADPLAY_TOOLS_DIR)"
	@echo ""

# @{ preflight checks

_check_git_status_is_clean:
# ifneq ($(GITSTATUS), 0)
# 	$(error "Git repository is dirty, cannot deploy. Run 'git status' for more\
# 			info.")
# endif

_check_game_json_name:
ifneq ($(GAME_JSON), $(GAME_NAME).game.json)
	$(error "ERROR: Detected .game.json named: '$(GAME_JSON)', expected based\
			on GAME_NAME: '$(GAME_NAME).game.json'.")
endif

_check_itch_allowed:
ifneq ($(ALLOW_ITCH_RELEASE), true)
	$(error "Releasing to itch is not yet allowed for this game.")
endif

# @}

# make a zipfile for itch
itch: \
	_check_itch_allowed \
	_check_git_status_is_clean \
	info_dump \
	
	@echo "$(COLOR_GREEN)"
	@echo "running from: " $(PWD)
	@echo "Remove previous release if it exists."
	@echo "$(COLOR_RESET)"
	-@rm -rf $(ITCH_RELEASE_FILE)
	python3 $(QUADPLAY_TOOLS_DIR)/export.py -z $(ITCH_RELEASE_FILE) .
	@echo "done, made $(PWD)/$(ITCH_RELEASE_FILE)"
	@echo "updating butler..."
	bash getbutler.sh
	butler/butler push $(ITCH_RELEASE_FILE) $(ITCH_RELEASE_USER)/$(ITCH_GAME_NAME):html

# for putting in your ~/public_html/ folder
# might be good to cache older exports with mv instead of overwriting them
export_html: \
	_check_git_status_is_clean \
	info_dump \
	_check_game_json_name \

	python3 $(QUADPLAY_TOOLS_DIR)/export.py $(PWD) -o $(EXPORT_DIR) -f
	@echo "$(COLOR_GREEN)Exported $(GAME_NAME) to $(EXPORT_DIR).  To change destination, set EXPORT_DIR in Makefile.defs.$(COLOR_RESET)"

# run the project linter
lint:
	@echo  "$(COLOR_GREEN)Running project linter$(COLOR_RESET)" 
	@$(LINTER)

# @TODO: 
#
# Deployment System
# #################
#
# To configure a github repo to be a deployment repo, create a new repository
# on github.  Then in the settings, go to the "pages" section, and set the
# source to "deploy from a branch" and select the "main" branch.
#
# * add a top level page to deployment repo that has links to deployed games
#
# path to the temp directory where the $(DEPLOY_REMOTE) gets cloned
DEPLOY_STAGING_ROOT = /var/tmp/project_deployment
DEPLOY_NAME = $(GAME_NAME).$(DEV_BRANCH)
DEPLOY_STAGING_DIR = $(DEPLOY_STAGING_ROOT)/$(DEPLOY_NAME)
DEPLOY_STAGING_ROOT_GIT = $(DEPLOY_STAGING_ROOT)/.git

DEPLOY_GIT = $(GIT) \
		  --git-dir $(DEPLOY_STAGING_ROOT_GIT) \
		  --work-tree $(DEPLOY_STAGING_ROOT)
GIT_PULL_RETURN = $(shell $(DEPLOY_GIT) pull --quiet 1>&2 2> /dev/null; echo $$?)
GIT_SOURCE_HASH := $(shell $(GIT) rev-parse HEAD)
GIT_COMMIT_MESSAGE := \
				  "Deploy $(DEPLOY_NAME) from source hash $(GIT_SOURCE_HASH)"
GIT_BRANCH_DESCRIPTION := $(shell $(GIT) config branch.$(DEV_BRANCH).description)

# files to stage
SRC_FILES := $(shell $(LINTER) -m manifest)
SRC_FILES += $(wildcard label* README.md preview.png)
DST_FILES = $(addprefix $(DEPLOY_STAGING_DIR)/, $(SRC_FILES))
DST_FILES_PRESENT = $(shell $(DEPLOY_GIT) ls-files $(DEPLOY_NAME) --full-name | tr " " "\n" | sed "s,^,$(DEPLOY_STAGING_ROOT)/,")


_cloned_deployment_staging_dir:
ifneq ($(GIT_PULL_RETURN), 0)
	@$(GIT) clone --depth=1 $(DEPLOY_REMOTE) $(DEPLOY_STAGING_ROOT)
endif

# copies and adds files to the deployment git repo
$(DEPLOY_STAGING_DIR)/% : %
	@mkdir -p `dirname $@`
	@cp -pv $< $@
	$(DEPLOY_GIT) add $@

_description_file:
	@echo $(GIT_BRANCH_DESCRIPTION) > $(DEPLOY_STAGING_DIR)/description.md
	@$(DEPLOY_GIT) add $(DEPLOY_STAGING_DIR)/description.md

_update_deployment_landing_readme:
	@python $(DEPLOY_STAGING_ROOT)/update_readme.py
	@$(DEPLOY_GIT) add $(DEPLOY_STAGING_ROOT)/README.md

_push_and_commit:
	@echo $(DST_FILES_PRESENT) | tr " " "\n" > $(DEPLOY_STAGING_DIR)/present_files.txt
	@echo $(DST_FILES) | tr " " "\n" > $(DEPLOY_STAGING_DIR)/new_files.txt
	@grep -F -x -v -f $(DEPLOY_STAGING_DIR)/new_files.txt $(DEPLOY_STAGING_DIR)/present_files.txt > $(DEPLOY_STAGING_DIR)/diff.txt || echo ""
	@test -s $(DEPLOY_STAGING_DIR)/diff.txt && $(DEPLOY_GIT) rm --pathspec-from-file=$(DEPLOY_STAGING_DIR)/diff.txt || echo ""
	@rm $(DEPLOY_STAGING_DIR)/present_files.txt
	@rm $(DEPLOY_STAGING_DIR)/new_files.txt
	@rm $(DEPLOY_STAGING_DIR)/diff.txt

	@$(DEPLOY_GIT) commit -m $(GIT_COMMIT_MESSAGE) || echo \
		"$(COLOR_GREEN)""...everything already deployed!""$(COLOR_RESET)"
	$(DEPLOY_GIT) push origin main

deploy: \
	info_dump \
	_check_git_status_is_clean \
	_check_game_json_name \
	_cloned_deployment_staging_dir \
	$(DST_FILES) \
	_description_file \
	_update_deployment_landing_readme \
	_push_and_commit \

	@echo "$(COLOR_GREEN)"
	@echo "To test visit: "
	@echo "https://morgan3d.github.io/quadplay/console/quadplay.html?game=https://"$(GITHUB_USERNAME)".github.io/$(DEPLOY_REPO_NAME)/$(DEPLOY_NAME)/$(GAME_NAME).game.json"
	@echo "$(COLOR_RESET)"
	@echo "Deployed: " $(GAME_NAME)

deploy_v3:
	@echo "using export-based deployment"
	python3 $(QUADPLAY_TOOLS_DIR)/export.py -o $(DEPLOY_STAGING_DIR)_html

# print all targets
.PHONY: help
help:
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
