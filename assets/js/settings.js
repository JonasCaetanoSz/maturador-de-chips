   // Ação de fechar pagina

    document.querySelector(".close-btn").addEventListener("click", () => {
      window.controller.close_preferences_signal();
    })

  var currentFilePath = "";

      // Obter configurações do usuario
    window.controller.get_user_configs().then(configs => {

      const preferences = JSON.parse(configs);
      currentFilePath = preferences.selectedFilePath || "";

      //  Checkboxes 
      document.getElementById("shutdown").checked = preferences.ShutdownAfterCompletion;
      document.getElementById("sound").checked = preferences.PlaySound;
      document.getElementById("continue").checked = preferences.ContinueIfDisconnected;

      //  Intervalos 
      document.getElementById("minInterval").value = preferences.MinInterval;
      document.getElementById("maxInterval").value = preferences.MaxInterval;

      //  Limite de mensagens 
      document.getElementById("limitMessages").value = preferences.LimitMessages;

      //  Fonte de mensagens 
      const select = document.getElementById("msgSelect");
      select.value = preferences.MessageType;

      // Atualiza o campo extra conforme a seleção
      updateExtraOption();

      // Se for OpenAI
      if (preferences.MessageType  == "openai") {
        const apiTokenInput = document.getElementById("apiToken");
        if (apiTokenInput) apiTokenInput.value = preferences.ApiToken;
      }

      // Se for arquivo
      if (preferences.MessageType ===  "file") {
        const fileNameSpan = document.getElementById("fileName");
        if (fileNameSpan && preferences.selectedFilePath )
          fileNameSpan.textContent = "Arquivo atual: " + preferences.selectedFilePath.split("\\").pop();
      }
    }).catch(err => {
      console.error("Erro ao carregar configurações:", err);
    });
    
  
  // Atualizar configurações

  document.querySelector("#saveBtn").addEventListener("click", () => {
    const fileNameSpan = document.getElementById("fileName");

    // Se o usuário mudou o arquivo no front, atualiza currentFilePath
    if (fileNameSpan && fileNameSpan.textContent.includes(":")) {
        const full = fileNameSpan.textContent.split(":").pop().trim();
        // ← Aqui deve ser o caminho completo, NÃO apenas o nome!
        currentFilePath = full;
    }
    
    const shutdown = document.querySelector("#shutdown").checked;
    const sound = document.querySelector("#sound").checked;
    const continue_ = document.querySelector("#continue").checked;
    const minInterval = parseInt(document.querySelector("#minInterval").value);
    const maxInterval = parseInt(document.querySelector("#maxInterval").value);
    const limitMessages = parseInt(document.querySelector("#limitMessages").value);
    const msgSelect = document.querySelector("#msgSelect").value;
    const tokenInput = document.querySelector("#apiToken");
    const apiToken = tokenInput ? tokenInput.value.trim() : currentToken;

  // salva na variável global
  currentToken = apiToken;

    // Validação dos valores básicos

    if (
      !minInterval ||
      !maxInterval ||
      minInterval >= maxInterval ||
      !limitMessages ||
      limitMessages <= 0
    ) {
      window.controller.show_alert(
        "Maturador de chips",
        "Erro ao cadastrar novas configurações, verifique os dados informados e tente novamente."
      );
      return; // impede execução do restante
    }

    // Determina se o método selecionado exige token

    const needToken = ["openai"].includes(msgSelect);
    if (needToken && apiToken === "") {
      window.controller.show_alert(
        "Maturador de chips",
        "O método selecionado requer um token de API. Por favor, preencha o campo correspondente."
      );
      return;
    }

    // Cria objeto de configurações

    const preferences = {
      ShutdownAfterCompletion: shutdown,
      PlaySound: sound,
      ContinueIfDisconnected: continue_,
      MinInterval: minInterval,
      MaxInterval: maxInterval,
      LimitMessages: limitMessages,
      MessageType: msgSelect,
      ApiToken: apiToken,
      selectedFilePath: currentFilePath
    };

    // Envia para backend
    
    window.controller.update_user_configs(JSON.stringify(preferences))
      .then(() => {
        window.controller.show_alert("Maturador de chips", "Configurações salvas com sucesso!");
      })
      .catch(err => {
        console.error("Erro ao salvar configurações:", err);
        window.controller.show_alert("Maturador de chips", "Erro ao salvar configurações. Verifique o arquivo de log para mais detalhes.");
      });
});
