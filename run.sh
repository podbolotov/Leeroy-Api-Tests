#!/usr/bin/env bash

echo "[ 🤖 Iteration is started. ]"

# PROJECT ROOT FINDING START
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

if [[ -f $PROJECT_ROOT/run.sh && -f $PROJECT_ROOT/requirements.txt ]]; then
    echo "[ 🤖 Project root is \"$PROJECT_ROOT\". ]"
else 
    echo "[ 🛑 Project root \"$PROJECT_ROOT\" is incorrect! Iteration is stopped! ]"
    exit 1
fi
#PROJECT ROOT FINDING END

# SERVICE (NON-CONFIGURABLE) PARAMS START
CURRENT_TIME=$(date +%Y-%m-%d_%H-%M-%S)
TIME_FOR_MESSAGE=$(date +%H:%M:%S)
DATE_FOR_MESSAGE=$(date +%d.%m.%Y)
PYTEST_EXIT_CODE=1
# SERVICE (NON-CONFIGURABLE) PARAMS END

# Open project directory and activate virtual environment
echo "[ 🤖 Opening project root $PROJECT_ROOT... ]"
cd "$PROJECT_ROOT" || exit
echo "[ 🤖 Python virtual environment activating... ]"
source venv/bin/activate

# Preparation: Clearing results directory
echo "[ 🤖 Deleting old iterations from $PROJECT_ROOT/allure-results/... ]"
rm -rf "$PROJECT_ROOT"/allure-results/*

RUN_SCOPE_WITH_PYTEST_ARGS="tests"
# Parsing RUN_SCOPE variable
if [ -z "${RUN_SCOPE}" ]; then
    echo "[ 🤖 RUN_SCOPE is not defined. Using default scope: \"$RUN_SCOPE_WITH_PYTEST_ARGS\" without additional args...  ]"
else
    RUN_SCOPE_WITH_PYTEST_ARGS="$RUN_SCOPE"
    echo "[ 🤖 Defined RUN_SCOPE and additional args is: \"$RUN_SCOPE_WITH_PYTEST_ARGS\"... ]"
fi

pytest "$RUN_SCOPE_WITH_PYTEST_ARGS" --alluredir="$PROJECT_ROOT"/allure-results -s

PYTEST_EXIT_CODE=$?
echo "[ 🤖 Pytest exitcode is $PYTEST_EXIT_CODE. ]"

if [[ -d "$PROJECT_ROOT"/allure-report/ && \
-d "$PROJECT_ROOT"/allure-report/$(ls -Art allure-report/ | tail -n 1)/multi-file/history ]]; then
    echo "[ 🤖 Copying history from previous multi-file report... ]"
    mv "$PROJECT_ROOT"/allure-report/$(ls -Art allure-report/ | tail -n 1)/multi-file/history \
    "$PROJECT_ROOT"/allure-results/
else
    echo "[ 🤖 Previous multi-file report is not found. History won't be included in current report. ]"
fi

echo "[ 🤖 Generating multi-file report with Allure... ]"
allure generate "$PROJECT_ROOT"/allure-results --clean --output \
"$PROJECT_ROOT"/allure-report/"$CURRENT_TIME"/multi-file --name "Leeroy Api Tests"
echo "[ 🤖 Generating single-file report with Allure... ]"
allure generate "$PROJECT_ROOT"/allure-results --clean --output \
"$PROJECT_ROOT"/allure-report/"$CURRENT_TIME"/single-file --single-file --name "Leeroy Api Tests"

RUN_STATUS=0
[ $PYTEST_EXIT_CODE -eq 0 ] && RUN_STATUS='🟩 Статус: все тесты пройдены.' || RUN_STATUS="🟥 Статус: обнаружены упавшие тесты."
echo "   ---- "
echo "   ⚙️  Итерация тестирования от $TIME_FOR_MESSAGE ($DATE_FOR_MESSAGE) завершена."
echo "   $RUN_STATUS"
echo "   🔗 Cсылка на отчёт, если он опубликован: $REPORT_LINK"
echo "   🔗 Отчёт: ./allure-report/$CURRENT_TIME/index.html"
echo "   ---- "

# Deactivate virtual environment
echo "[ 🤖 Python virtual environment deactivating... ]"
deactivate

# Open report with open or xdg-open
SYSTEM_HAS_OPEN=$(which open | grep 'open')
SYSTEM_HAS_XDG_OPEN=$(which xdg-open | grep 'xdg-open')
if [ -n "$SYSTEM_HAS_OPEN" ]
then
    echo "[ 🤖 Report opening via open... ]"
    open ./allure-report/"$CURRENT_TIME"/single-file/index.html > /dev/null
elif [ -n "$SYSTEM_HAS_XDG_OPEN" ]
then
    echo "[ 🤖 Report opening via xdg-open... ]"
    xdg-open ./allure-report/"$CURRENT_TIME"/single-file/index.html > /dev/null
else
   echo "[ 🤖 open or xdg-open not found, the report will not be opened. ]"
fi

echo "[ 🤖 Iteration is ended. ]"
