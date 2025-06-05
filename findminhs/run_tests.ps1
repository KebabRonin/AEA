# Create results directory if it doesn't exist
$resultsDir = "results_optimized_build"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir
}

# Path to the testset directory
$testsetDir = "..\hs_verifier\Hitting Set Verifier\src\test\resources\testset"

# Get all .hgr files
$hgrFiles = Get-ChildItem -Path $testsetDir -Filter "*.hgr"

foreach ($file in $hgrFiles) {
    Write-Host "Processing $($file.Name)..."

    # Create output filenames
    $solutionFile = Join-Path $resultsDir "$($file.BaseName)_solution.json"
    $reportFile = Join-Path $resultsDir "$($file.BaseName)_report.json"

    # Run the solver
    cargo run solve "$($file.FullName)" settings.json --hgr --solution $solutionFile --report $reportFile

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully processed $($file.Name)"
    } else {
        Write-Host "Failed to process $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "All files processed. Results saved in $resultsDir"