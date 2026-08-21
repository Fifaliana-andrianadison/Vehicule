param(
    [Parameter(Position=0)]
    [string]$Command = "run"
)

$PythonPath = "C:\Users\User1\AppData\Local\Programs\Python\Python312\python.exe"
$ProjectPath = "D:\vehicule"

function Write-Title {
    param([string]$Text)
    Write-Host "="*60 -ForegroundColor Blue
    Write-Host "  $Text" -ForegroundColor White -BackgroundColor Blue
    Write-Host "="*60 -ForegroundColor Blue
}

switch ($Command.ToLower()) {
    "run" {
        Write-Title "Démarrage du serveur de développement"
        & $PythonPath manage.py runserver
    }
    "migrate" {
        Write-Title "Application des migrations"
        & $PythonPath manage.py migrate
    }
    "migrations" {
        Write-Title "Création des migrations"
        & $PythonPath manage.py makemigrations
    }
    "superuser" {
        Write-Title "Création d'un superutilisateur"
        $username = Read-Host "Nom d'utilisateur"
        $email = Read-Host "Email"
        & $PythonPath manage.py createsuperuser --username=$username --email=$email
    }
    "reminders" {
        Write-Title "Envoi manuel des rappels"
        & $PythonPath manage.py send_reminders
    }
    "shell" {
        Write-Title "Shell Django"
        & $PythonPath manage.py shell
    }
    "collectstatic" {
        Write-Title "Collecte des fichiers statiques"
        & $PythonPath manage.py collectstatic --noinput
    }
    "test" {
        Write-Title "Tests"
        & $PythonPath manage.py test
    }
    default {
        Write-Host ""
        Write-Host "Usage: .\manage.ps1 [command]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commandes disponibles :" -ForegroundColor Cyan
        Write-Host "  run           Démarrer le serveur (défaut)" -ForegroundColor White
        Write-Host "  migrate       Appliquer les migrations" -ForegroundColor White
        Write-Host "  migrations    Créer les migrations" -ForegroundColor White
        Write-Host "  superuser     Créer un superutilisateur" -ForegroundColor White
        Write-Host "  reminders     Envoyer les rappels manuellement" -ForegroundColor White
        Write-Host "  shell         Console interactive Django" -ForegroundColor White
        Write-Host "  collectstatic Collecter les fichiers statiques" -ForegroundColor White
        Write-Host "  test          Lancer les tests" -ForegroundColor White
        Write-Host ""
        Write-Host "Exemples :" -ForegroundColor Cyan
        Write-Host "  .\manage.ps1 run" -ForegroundColor Gray
        Write-Host "  .\manage.ps1 reminders" -ForegroundColor Gray
    }
}
