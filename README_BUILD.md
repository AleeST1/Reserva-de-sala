# Como Criar o Executável do Sistema de Reservas

## Pré-requisitos

1. **Python 3.7+** instalado
2. **pip** (gerenciador de pacotes Python)
3. **Conexão com o banco de dados MySQL** configurada

## Dependências Necessárias

Execute os seguintes comandos para instalar as dependências:

```bash
pip install pyinstaller
pip install tkcalendar
pip install mysql-connector-python
pip install pillow
```

## Método 1: Usando o Script Automático (Recomendado)

1. Execute o arquivo `build_exe.bat` clicando duas vezes nele
2. Aguarde o processo de build ser concluído
3. O executável será criado em `dist\Reservas de Salas.exe`

## Método 2: Comando Manual

Execute o seguinte comando no terminal:

```bash
pyinstaller --onefile --windowed --icon=resources/icone.reservas.ico --add-data "resources;resources" --name "Reservas de Salas" sala_reservas.py
```

## Método 3: Usando o Arquivo .spec

1. Execute: `pyinstaller "Reservas de Salas.spec"`
2. O executável será criado em `dist\Reservas de Salas.exe`

## Configurações do Executável

### Ícone
- **Arquivo principal**: `resources/icone.reservas.ico`
- **Arquivo alternativo**: `resources/icone.reservas.png`
- O ícone será exibido na barra de tarefas e no cabeçalho da janela

### Recursos Incluídos
- ✅ Pasta `resources` completa (ícones e logo)
- ✅ Todas as dependências Python necessárias
- ✅ Interface gráfica sem console
- ✅ Nome personalizado: "Reservas de Salas.exe"

## Estrutura de Arquivos

```
projeto/
├── sala_reservas.py          # Código principal
├── build_exe.bat            # Script de build automático
├── "Reservas de Salas.spec" # Configuração PyInstaller
├── fix_icone.bat            # Script para corrigir ícone
├── resources/
│   ├── icone.reservas.ico   # Ícone do executável
│   ├── icone.reservas.png   # Ícone alternativo
│   └── logo_rinaldi.png     # Logo da empresa
└── dist/
    └── Reservas de Salas.exe  # Executável final
```

## 🔧 Solução para Problema do Ícone na Área de Trabalho

Se o ícone não aparecer corretamente na área de trabalho:

### Opção 1: Script Automático
1. Execute o arquivo `fix_icone.bat`
2. Aguarde o processo ser concluído
3. O ícone deve aparecer corretamente

### Opção 2: Manual
1. Clique com botão direito no executável
2. Selecione "Propriedades"
3. Clique em "Alterar ícone"
4. Navegue até a pasta `resources`
5. Selecione `icone.reservas.ico`
6. Clique em "OK"

### Opção 3: Limpar Cache do Windows
```cmd
ie4uinit.exe -ClearIconCache
```

## Solução de Problemas

### Erro de Conexão com Banco
- Verifique se o servidor MySQL está rodando
- Confirme as credenciais no arquivo `sala_reservas.py`

### Ícone não aparece na área de trabalho
- Execute o script `fix_icone.bat`
- Verifique se o arquivo `icone.reservas.ico` existe
- O arquivo `.ico` deve ter múltiplos tamanhos (16x16, 32x32, 48x48, 256x256)

### Executável muito grande
- Use `--onefile` para criar um único arquivo
- Use `--windowed` para ocultar o console

## Distribuição

Para distribuir o sistema:

1. Copie o arquivo `dist\Reservas de Salas.exe`
2. Certifique-se de que o servidor MySQL está acessível
3. O executável é independente e não precisa de instalação

## Notas Importantes

- ✅ O ícone será mantido no executável
- ✅ Todos os recursos (imagens, ícones) estão incluídos
- ✅ A aplicação funciona sem console visível
- ✅ Compatível com Windows 10/11
- ✅ Não requer instalação de Python no computador destino
- ⚠️ Pode ser necessário executar `fix_icone.bat` para o ícone aparecer na área de trabalho 