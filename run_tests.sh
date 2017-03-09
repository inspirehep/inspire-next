#!/bin/bash

printf "\n--------------------- Unit Tests ----------------------\n"
py.test inspirehep tests/unit
unit_tests_exit_code=$?

printf "\n\n--------------- Creating Documentation ----------------\n"
make -C docs html
create_docs_exit_code=$?

if [[ "$unit_tests_exit_code" != "0" ]] || [[ "$create_docs_exit_code" != "0" ]]
then
	exit 1
fi
