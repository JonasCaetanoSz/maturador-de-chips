    // Ação de fechar pagina

    document.querySelector(".close-btn").addEventListener("click", () => {
      controller.close_preferences_signal();
    })

  controller.get_user_configs().then(configs => {
    const preferences = JSON.parse(configs);

    // === Checkboxes ===
    document.getElementById("shutdown").checked = preferences.ShutdownAfterCompletion;
    document.getElementById("sound").checked = preferences.SoundNotifications;
    document.getElementById("continue").checked = preferences.ContinueIfDisconnected;

    // === Intervalos ===
    document.getElementById("minInterval").value = preferences.IntervalMin;
    document.getElementById("maxInterval").value = preferences.IntervalMax;

    // === Limite de mensagens ===
    document.getElementById("limitMessages").value = preferences.MessageLimit;

    // === Fonte de mensagens ===
    const select = document.getElementById("msgSelect");
    select.value = preferences.MessageSource;

    // Atualiza o campo extra conforme a seleção
    updateExtraOption();

    // Se for OpenAI
    if (preferences.MessageSource === "openai") {
      const apiTokenInput = document.getElementById("apiToken");
      if (apiTokenInput) apiTokenInput.value = preferences.ApiToken;
    }

    // Se for arquivo
    if (preferences.MessageSource === "file") {
      const fileNameSpan = document.getElementById("fileName");
      if (fileNameSpan && preferences.FilePath)
        fileNameSpan.textContent = "Arquivo atual: " + preferences.FilePath.split("\\").pop();
    }
  }).catch(err => {
    console.error("Erro ao carregar configurações:", err);
  });