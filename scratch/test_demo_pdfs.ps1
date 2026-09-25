$ErrorActionPreference = "Stop"

$base_url = "http://localhost:8000/api"
$token = "test-demo-token"
$email = "test_demo_user@example.com"
$password = "testpass123"

# Register & Login
Write-Host "Registering..."
$regBody = @{ email = $email; password = $password } | ConvertTo-Json
curl.exe -s -X POST "$base_url/auth/register" -H "Content-Type: application/json" -d $regBody

Write-Host "Logging in..."
$loginBody = "username=$email&password=$password"
$loginResp = Invoke-RestMethod -Uri "$base_url/auth/token" -Method Post -Body $loginBody -ContentType "application/x-www-form-urlencoded"
$token = $loginResp.access_token
$headers = @{ "Authorization" = "Bearer $token" }

function Test-Workflow {
    param([string]$PdfPath, [string]$SopPath, [string]$Instruction)

    Write-Host "Uploading SOP: $SopPath"
    $sopResp = curl.exe -s -X POST "$base_url/documents/upload" `
      -H "Authorization: Bearer $token" `
      -F "file=@$SopPath" `
      -F "role=sop"
    $sopId = ($sopResp | ConvertFrom-Json).id

    Write-Host "Uploading Inspection: $PdfPath"
    $docResp = curl.exe -s -X POST "$base_url/documents/upload" `
      -H "Authorization: Bearer $token" `
      -F "file=@$PdfPath" `
      -F "role=inspection"
    $docId = ($docResp | ConvertFrom-Json).id

    Write-Host "Executing Workflow for Document $docId"
    $wfBody = @{
        instruction = $Instruction
        document_ids = @($docId)
    } | ConvertTo-Json

    $wfResp = Invoke-RestMethod -Uri "$base_url/workflows/approval" -Method Post -Headers $headers -Body $wfBody -ContentType "application/json" -TimeoutSec 120
    
    return $wfResp
}

$instruction = "Analyze this inspection report and determine whether approval should be granted based on the available SOP evidence."

$approveResult = Test-Workflow "C:\Users\Shubham\OneDrive\Desktop\ai-workbench\demo_fixtures\demo_inspection_approve.pdf" "C:\Users\Shubham\OneDrive\Desktop\ai-workbench\demo_fixtures\demo_sop_approve.pdf" $instruction
Write-Host "`n--- APPROVE CASE ---"
Write-Host "Decision: $($approveResult.decision)"
Write-Host "Summary: $($approveResult.summary)"

$reviewResult = Test-Workflow "C:\Users\Shubham\OneDrive\Desktop\ai-workbench\demo_fixtures\demo_inspection_review.pdf" "C:\Users\Shubham\OneDrive\Desktop\ai-workbench\demo_fixtures\demo_sop_review.pdf" $instruction
Write-Host "`n--- REVIEW CASE ---"
Write-Host "Decision: $($reviewResult.decision)"
Write-Host "Summary: $($reviewResult.summary)"

$rejectResult = Test-Workflow "C:\Users\Shubham\OneDrive\Desktop\ai-workbench\demo_fixtures\demo_inspection_reject.pdf" "C:\Users\Shubham\OneDrive\Desktop\ai-workbench\demo_fixtures\demo_sop_reject.pdf" $instruction
Write-Host "`n--- REJECT CASE ---"
Write-Host "Decision: $($rejectResult.decision)"
Write-Host "Summary: $($rejectResult.summary)"
