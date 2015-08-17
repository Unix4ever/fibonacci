REACTOR := select
PORT := 8080
BIND_ADDRESS := 0.0.0.0

CMD_BASE := source env/bin/activate && twistd -r $(REACTOR)
CMD_APP := fibonacci --port=$(PORT) --bind-address=$(BIND_ADDRESS)

ifeq ($(OS),Windows_NT)
	REACTOR := win32
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
				REACTOR := epoll
    endif
    ifeq ($(UNAME_S),Darwin)
				REACTOR := kqueue
    endif
endif

all: pep8 test run

env:
	bash ./scripts/setup.sh

main-deps: env
	env/bin/pip install -r requirements.txt

test-deps: main-deps
	env/bin/pip install -r requirements-dev.txt

stop:
	if [ -f twistd.pid ] ; \
		then \
		echo "\033[0;33mStopped previously running daemon\033[0m" ; \
		kill `cat twistd.pid` ; \
	fi;

daemon: main-deps stop FORCE
	@bash -c "$(CMD_BASE) $(CMD_APP)"
	echo "Started daemon pid:" && cat twistd.pid && echo ""

run: main-deps FORCE
	@bash -c "$(CMD_BASE) -n $(CMD_APP)"

test: test-deps FORCE
	@echo "\033[0;33mRunning trial tests\033[0m"
	@bash -c "env/bin/trial tests"

pep8: test-deps FORCE
	@echo "\033[0;33mRunning PEP8\033[0m"
	@bash -c "env/bin/pep8 twisted fibonacci tests --ignore E501,E126"
	@echo "\033[0;32mPASSED\033[0m"

ci: pep8 test

clean:
	rm -rf env && find ./ -name "*.pyc" | xargs rm

FORCE:
