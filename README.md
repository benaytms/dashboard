# Dashboard UFPR

Dashboard interativo para o Hackathon de dados da UFPR

Este dashboard permite visualizar e analisar dados das pesquisas
realizadas pela UFPR:  
- Cursos
- Disciplinas presenciais  
- Disciplinas EAD
- Pesquisa institucional

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/xpu7zcKH)

## Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)
- git

### Instalação e Execução

```bash
1. git clone https://github.com/benaytms/dashboard.git
2. cd dashboard/
3. pip install -r requirements.txt
4. python3 src/app.py
5. Abrir no navegador: http://localhost:8050
```

### Troubleshooting
Para instalar dependências e pacotes, é necessário usar o pip
e muitas vezes para usar o pip é preciso estar em um ambiente
virtual separado. Nesses casos a solução é a seguinte:

```bash
python3 -m venv venv
source venv/bin/activate
<instalar dependências>
```

Após isso, para voltar ao ambiente padrão basta usar o comando "deactivate".
