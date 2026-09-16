# Backend do TozMusic

Este servidor baixa o áudio usando `yt-dlp` e entrega o arquivo ao aplicativo Flutter.

## Iniciar no computador

No PowerShell, dentro da pasta `server`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

O computador precisa ter o `ffmpeg` instalado apenas se o `yt-dlp` escolher um formato que precise de conversão.

## Hospedar sem deixar o computador ligado

A pasta já inclui `Dockerfile` e `render.yaml` para publicar o backend em um serviço de nuvem como o Render. Crie um repositório no GitHub com a pasta `server`, crie um Web Service no Render apontando para esse repositório e escolha o plano disponível. O Render fornecerá uma URL pública parecida com:

```text
https://tozmusic-downloader.onrender.com
```

Depois gere o APK usando essa URL:

```powershell
flutter build apk --release --dart-define=TOZMUSIC_BACKEND_URL=https://tozmusic-downloader.onrender.com
```

Serviços gratuitos podem ficar adormecidos e demorar no primeiro download. Para uso contínuo, será necessário um plano que mantenha o serviço ativo.

## Gerar o APK

Descubra o IPv4 do computador com `ipconfig`. Se o IP for `192.168.1.20`, gere assim:

```powershell
flutter build apk --release --dart-define=TOZMUSIC_BACKEND_URL=http://192.168.1.20:8000
```

O celular e o computador precisam estar na mesma rede Wi-Fi. No emulador Android, o endereço padrão `http://10.0.2.2:8000` já aponta para o computador.

Teste o servidor antes de instalar o APK abrindo no navegador do celular:

```text
http://192.168.1.20:8000/health
```

A resposta esperada é `{"status":"ok"}`.
