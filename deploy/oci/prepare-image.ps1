param(
    [Parameter(Mandatory = $true)] [string] $RegistryHost,
    [Parameter(Mandatory = $true)] [string] $OcirUsername,
    [Parameter(Mandatory = $true)] [string] $Namespace,
    [Parameter(Mandatory = $true)] [string] $Repository,
    [string] $Tag = "latest"
)

$ErrorActionPreference = "Stop"
$image = "${RegistryHost}/${Namespace}/${Repository}:${Tag}"

Write-Host "Iniciando sesión en ${RegistryHost}. Usa un Auth Token de OCI como contraseña."
docker login $RegistryHost --username $OcirUsername
docker build --tag $image .
docker push $image

Write-Host "Imagen publicada: $image"
Write-Host "Usa esta referencia al crear la instancia de contenedor en OCI."
