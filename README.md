# Gobot - O chatbot sobre godot

**Gobot** é um chatbot simples, projetado para ensinar de forma didática e resolver dúvidas sobre a Godot Game Engine, que opera utilizando a API oficial do Telegram e os modelos de geração de linguagem **Google Gemini**.

Para saber mais sobre a API base do Telegram utilizada, acesse [este link](#).

## Como Rodar?

1. **Crie o Bot no Telegram**:  
   - Utilize o [BotFather](https://core.telegram.org/bots#botfather) para criar um novo bot e obter o token de acesso.
  
2. **Configuração do Ambiente**:
   - Copie o token do bot para o arquivo `.env`, seguindo o modelo do arquivo `dot-env-example`.
  
3. **Inicie o Bot**:
   - Execute o arquivo `main.py` para iniciar a comunicação do bot com a API do Telegram.


## TODO:
- [x] Conseguir mandar imagens via bot para a API do Gemini
- [X] Deploy do backend do bot
- [ ] Bot restrito a membros de um canal específico do Telegram
- [ ] Mais interações
