Param
(
    [string]$RunScope = ".\tests\"
)

Write-Host "[ Iteration is started. ]" -BackgroundColor Darkgray

# PROJECT ROOT FINDING START
$PROJECT_ROOT=$($MyInvocation.MyCommand.Path | split-path -parent)
$TEST_PATH_FILE_1=$(Test-Path -PathType Leaf -Path $PROJECT_ROOT'\run.ps1')
$TEST_PATH_FILE_2=$(Test-Path -PathType Leaf -Path $PROJECT_ROOT'\requirements.txt')
if (
    $TEST_PATH_FILE_1 -and $TEST_PATH_FILE_2
) {
    Write-Host "[ Project root is $PROJECT_ROOT. ]"
} else {
    Write-Host "[ ERROR: Project root $PROJECT_ROOT is incorrect! Iteration is stopped! ]"
    exit 1
}
# PROJECT ROOT FINDING END

# SERVICE (NON-CONFIGURABLE) PARAMS START
$CURRENT_TIME=$(Get-Date -Format "yyyy-MM-dd_HH-mm-ss")
$TIME_FOR_MESSAGE=$(Get-Date -Format "HH:mm:ss")
$DATE_FOR_MESSAGE=$(Get-Date -Format "dd.MM.yyyy")
$PYTEST_EXIT_CODE=1
# SERVICE (NON-CONFIGURABLE) PARAMS END

# Open project directory and activate virtual environment
Write-Host "[ Opening project root $PROJECT_ROOT... ]"
cd $PROJECT_ROOT
Write-Host "[ Python virtual environment activating... ]"
$TEST_PATH_VENV_ACTIVATION_DEFAULT=$(Test-Path -PathType Leaf -Path $PROJECT_ROOT'\venv\Scripts\activate.ps1')
$TEST_PATH_VENV_ACTIVATION_PYCHARM=$(Test-Path -PathType Leaf -Path $PROJECT_ROOT'\.venv\Scripts\activate.ps1')
if (
    $TEST_PATH_VENV_ACTIVATION_DEFAULT
) {
    Write-Host "[ venv path: .\venv\Scripts\activate.ps1 ... ]"
    .\venv\Scripts\activate.ps1
} elseif (
    $TEST_PATH_VENV_ACTIVATION_PYCHARM
) {
    Write-Host "[ venv path: .\.venv\Scripts\activate.ps1 ... ]"
    .\.venv\Scripts\activate.ps1
} else {
    Write-Host "[ venv activation script is not found! venv activation skipped... ]"
}

# Preparation: Clearing results directory
$TEST_PATH_ALLURE_RESULTS_DIR=$(Test-Path -PathType Container -Path $PROJECT_ROOT'\allure-results')
if (
    $TEST_PATH_ALLURE_RESULTS_DIR
) {
    Write-Host "[ Deleting old iterations from $PROJECT_ROOT\allure-results\... ]"
    Remove-Item $PROJECT_ROOT\allure-results\*.*
} else {
    Write-Host "[ Directory $PROJECT_ROOT\allure-results\ is not exist, clearing is skipped. ]"
}

# Parsing $RunScope param
$RUN_SCOPE_WITH_PYTEST_ARGS=$RunScope
Write-Host "[ Defined RUN_SCOPE and additional args is: "$RUN_SCOPE_WITH_PYTEST_ARGS"... ]"

# Run pytest with passed params
pytest $RUN_SCOPE_WITH_PYTEST_ARGS --alluredir=$PROJECT_ROOT/allure-results -s

# Write pytest exit code
$PYTEST_EXIT_CODE=$LastExitCode
Write-Host "[ Pytest exitcode is $PYTEST_EXIT_CODE. ]"

# Local message generation
Write-Host "[ Report message: ]"
Write-Host "   ---- "
Write-Host "   Iteration from $TIME_FOR_MESSAGE ($DATE_FOR_MESSAGE) is finished."
if ($PYTEST_EXIT_CODE -eq 0) {
    Write-Host "   " -NoNewline
    Write-Host "  " -BackgroundColor Green -NoNewline
    Write-Host " Status: all tests passed."
} elseif ($PYTEST_EXIT_CODE -eq 1) {
    Write-Host "   " -NoNewline
    Write-Host "  " -BackgroundColor Red -NoNewline
    Write-Host " Status: failed tests found."
} else {
    Write-Host "   " -NoNewline
    Write-Host "  " -BackgroundColor Yellow -NoNewline
    Write-Host " Status: pytest internal error."
}
Write-Host "   ---- "

# Allure report generation
Write-Host "[ Generating single-file report with Allure... ]"
allure generate $PROJECT_ROOT/allure-results --clean --output $PROJECT_ROOT/allure-report/$CURRENT_TIME/ --single-file  --name "Leeroy Api Tests"

# Open generated report in default browser
$(Start-Process "$PROJECT_ROOT\allure-report\$CURRENT_TIME\index.html")

Write-Host "[ Iteration is ended. ]" -BackgroundColor Darkgray