TESTS = $(wildcard test_*.py)

.PHONY: test

test: backup_client.py
	@- $(foreach TEST,$(TESTS), \
		echo === Running test: $(TEST); \
		python $(TEST); \
		)

backup_client.py: ../backup-client
	cp $< $@
