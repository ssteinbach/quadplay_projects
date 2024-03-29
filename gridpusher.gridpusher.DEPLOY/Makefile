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

include Makefile.defs

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
	@python3 download_level.py

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
	@echo ""

# @{ preflight checks

_check_git_status_is_clean:
ifneq ($(GITSTATUS), 0)
	$(error "Git repository is dirty, cannot deploy. Run 'git status' for more\
			info.")
endif

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

# this target deploys to a github repo that you can then point at with a url like:
# https://morgan3d.github.io/quadplay/console/quadplay.html?game=https://<USER_NAME>.github.io/<DEPLOY_REPO_NAME>/<GAME_NAME>.game.json
# the target needs to be something like: DEPLOY_REMOTE = git@github.com:<USER_NAME>/<DEPLOY_REPO_NAME>.git
deploy: \
	_check_git_status_is_clean \
	info_dump \
	_check_game_json_name \
	
	@echo "$(COLOR_GREEN)"
	@echo "Moving deploy branch"
	@echo "$(COLOR_RESET)"
	$(GIT) checkout -B $(DEPLOY_BRANCH)
	$(GIT) reset --hard $(DEV_BRANCH)
	$(GIT) init
	$(GIT) add .
	$(GIT) commit -m "Snapshot for deployment"
	$(GIT) remote add deploy $(DEPLOY_REMOTE)
	$(GIT) push deploy main --force
	@rm -rf .git
	$(GIT) checkout $(DEV_BRANCH)
	
	@echo "$(COLOR_GREEN)"
	@echo "Deploy branch is now moved." 
	@echo "To test visit: https://morgan3d.github.io/quadplay/console/quadplay.html?game=https://"$(GITHUB_USERNAME)".github.io/$(DEPLOY_REPO_NAME)/$(GAME_NAME).game.json"
	@echo "$(COLOR_RESET)"

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

# @{ new deployment system
#
# path to the temp directory where the $(DEPLOY_REMOTE) gets cloned
DEPLOY_STAGING_ROOT = /var/tmp/project_deployment
DEPLOY_NAME = $(GAME_NAME).$(DEV_BRANCH)
DEPLOY_STAGING_DIR = $(DEPLOY_STAGING_ROOT)/$(DEPLOY_NAME)
DEPLOY_STAGING_ROOT_GIT = $(DEPLOY_STAGING_ROOT)/.git

DEPLOY_GIT = $(GIT) \
		  --git-dir $(DEPLOY_STAGING_ROOT_GIT) \
		  --work-tree $(DEPLOY_STAGING_ROOT)
GIT_PULL_RETURN = $(shell $(DEPLOY_GIT) pull 1>&2 2> /dev/null; echo $$?)

# Goal: have a directory / project / target in a deployment repo that gets 
#       updated each time you run `make deploy`
#       * use the git branch to create the name of the branch to push into

# pieces:
# * SOURCE_REPO: the repo that you're deploying from.
# * SOURCE_PROJECT: name of the directory in the deployment system result
# * DEPLOY_STAGING_DIR: directory under $(DEPLOY_STAGING_ROOT) where this
#  	 				    project gets staged.  
_cloned_deployment_staging_dir:
ifneq ($(GIT_PULL_RETURN), 0)
	git clone $(DEPLOY_REMOTE) $(DEPLOY_STAGING_ROOT)
endif

_copy_local_to_deployment_staging_dir:
	mkdir -p $(DEPLOY_STAGING_DIR)
	cp -R . $(DEPLOY_STAGING_DIR)
	$(DEPLOY_GIT) add $(DEPLOY_STAGING_DIR)
	# @TODO: fetch the host commit hash and stuff it in the commit message here
	$(DEPLOY_GIT) commit -m "Updating $(DEPLOY_NAME)"

_push_local_to_remote:
	#$(DEPLOY_GIT) push origin main
	@echo "Would push"

new_deploy: \
	_cloned_deployment_staging_dir \
	_copy_local_to_deployment_staging_dir \
	_push_local_to_remote \

	@echo "$(COLOR_GREEN)"
	@echo "To test visit: "
	@echo "https://morgan3d.github.io/quadplay/console/quadplay.html?game="\
		"https://"$(GITHUB_USERNAME)".github.io/$(DEPLOY_REPO_NAME)/$(DEPLOY_NAME)/$(GAME_NAME).game.json"
	@echo "$(COLOR_RESET)"echo "Deployed: " $(GAME_NAME) " to " "foobar"
# @}

# print all targets
.PHONY: help
help:
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
