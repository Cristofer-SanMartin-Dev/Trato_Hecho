# ============================================================
#  Actualiza las credenciales temporales de AWS Academy
#  Corre esto cada vez que abras un Learner Lab nuevo, ANTES
#  de usar ec2-start.ps1 / ec2-stop.ps1 / terraform.
# ============================================================

Write-Host "Pega los 3 valores del panel 'AWS Details' de tu Learner Lab." -ForegroundColor Cyan
Write-Host ""

$accessKey    = Read-Host "aws_access_key_id"
$secretKey    = Read-Host "aws_secret_access_key"
$sessionToken = Read-Host "aws_session_token"

aws configure set aws_access_key_id "$accessKey" --profile academy
aws configure set aws_secret_access_key "$secretKey" --profile academy
aws configure set aws_session_token "$sessionToken" --profile academy
aws configure set region us-east-1 --profile academy

Write-Host ""
Write-Host "Verificando identidad..." -ForegroundColor Cyan
aws sts get-caller-identity --profile academy

Write-Host ""
Write-Host "Listo. Ahora puedes correr ec2-start.ps1" -ForegroundColor Green
