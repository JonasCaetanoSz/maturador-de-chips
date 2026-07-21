// Ação de fechar pagina
document.querySelector(".close-btn").addEventListener("click", () => {
    window.controller.close_preferences_signal();
});

// Mantemos as variáveis de token para o caso de o usuário ocultar o campo
var currentTokenPrivate = "";
var currentTokenGroup = "";
var savedGroupTargets = {}; // Nova variável global para guardar o mapeamento vindo do JSON

// Obter configurações do usuario
window.controller.get_user_configs().then(configs => {
    const preferences = JSON.parse(configs);
    
    // ================= ABA PRIVADA =================
    // As variáveis savedFilePathPrivate e savedFilePathGroup já existem no HTML
    savedFilePathPrivate = preferences.selectedFilePath || "";
    currentTokenPrivate = preferences.ApiToken || "";

    document.getElementById("shutdown").checked = preferences.ShutdownAfterCompletion || false;
    document.getElementById("sound").checked = preferences.PlaySound || false;
    document.getElementById("continue").checked = preferences.ContinueIfDisconnected || false;

    document.getElementById("minInterval").value = preferences.MinInterval || 1;
    document.getElementById("maxInterval").value = preferences.MaxInterval || 10;
    document.getElementById("limitMessages").value = preferences.LimitMessages || 50;
    document.getElementById("switchAccountAfter").value = preferences.switchAccountAfter || 100;

    const selectPriv = document.getElementById("msgSelect");
    if(selectPriv) selectPriv.value = preferences.MessageType || "file";

    if (preferences.MessageType === "openai") {
        const apiTokenInput = document.getElementById("apiTokenPrivate");
        if (apiTokenInput) apiTokenInput.value = currentTokenPrivate;
    }

    // ================= ABA GRUPOS =================
    savedFilePathGroup = preferences.SelectedFilePathGrp || "";
    currentTokenGroup = preferences.ApiTokenGrp || "";
    
    // Carrega o mapeamento salvo de grupos (ex: {"Sessao1": "12345@g.us"})
    savedGroupTargets = preferences.GroupMaturationTargets || {};
    
    document.getElementById("minIntervalGrp").value = preferences.MinIntervalGrp || 10;
    document.getElementById("maxIntervalGrp").value = preferences.MaxIntervalGrp || 30;
    document.getElementById("limitMessagesGrp").value = preferences.LimitMessagesGrp || 20;
    
    const sendStickers = document.getElementById("sendStickersGrp");
    if(sendStickers) sendStickers.checked = preferences.SendStickersGrp !== false; // Padrão é true

    const selectGrp = document.getElementById("msgSelectGrp");
    if(selectGrp) selectGrp.value = preferences.MessageTypeGrp || "file";

    if (preferences.MessageTypeGrp === "openai") {
        const apiTokenInputGrp = document.getElementById("apiTokenGroup");
        if (apiTokenInputGrp) apiTokenInputGrp.value = currentTokenGroup;
    }

    // Atualiza a exibição dos campos de arquivo e token via função que criamos no HTML
    if(typeof updateExtraOption === 'function') {
        updateExtraOption('private');
        updateExtraOption('group');
    }

}).catch(err => {
    console.error("Erro ao carregar configurações:", err);
});

// FUNÇÃO GLOBAL: Chamada pelo Python para construir o visual de cada chip na tela
window.receiveChipGroups = function(chipName, groupsList) {
    const container = document.getElementById("chipsGroupsContainer");
    
    // Se o texto padrão de "Carregando..." ainda estiver lá, limpa o container
    if (container.querySelector('div[style*="italic"]')) {
        container.innerHTML = "";
    }

    // Verifica se a linha desse chip já existe para reaproveitar ou criar uma nova
    let row = document.getElementById(`row-chip-${chipName}`);
    if (!row) {
        row = document.createElement("div");
        row.id = `row-chip-${chipName}`;
        row.style.cssText = "display: flex; align-items: center; justify-content: space-between; gap: 15px; background: #faf7f2; padding: 10px 15px; border-radius: 8px; border: 1px solid #eaddd3;";
        container.appendChild(row);
    }

    // Se o chip não tiver grupos ativos
    if (groupsList.length === 0) {
        row.innerHTML = `<strong>📱 ${chipName}:</strong> <span style="color: #c0392b; font-size: 0.9rem;">Nenhum grupo encontrado nesta conta.</span>`;
        return;
    }

    // Monta o Select Dropdown
    let selectHtml = `<select class="input-box chip-group-selector" data-chip="${chipName}" style="max-width: 300px; padding: 6px 10px;">`;
    selectHtml += `<option value="">-- Ignorar este chip --</option>`;
    
    groupsList.forEach(grp => {
        // Deixa pré-selecionado se o ID bater com o que foi salvo anteriormente
        const selected = (savedGroupTargets[chipName] === grp.id) ? "selected" : "";
        selectHtml += `<option value="${grp.id}" ${selected}>👥 ${grp.name}</option>`;
    });
    selectHtml += `</select>`;

    row.innerHTML = `
        <span style="font-weight: 600; color: #5e3d2e;">📱 ${chipName}</span>
        ${selectHtml}
    `;
};
  
// Atualizar configurações
document.querySelector("#saveBtn").addEventListener("click", () => {
    
    // --- COLETA DADOS PRIVADOS ---
    const shutdown = document.querySelector("#shutdown").checked;
    const sound = document.querySelector("#sound").checked;
    const continue_ = document.querySelector("#continue").checked;
    const minInterval = parseInt(document.querySelector("#minInterval").value);
    const maxInterval = parseInt(document.querySelector("#maxInterval").value);
    const limitMessages = parseInt(document.querySelector("#limitMessages").value);
    const switchAccountAfter = parseInt(document.getElementById("switchAccountAfter").value);
    const msgSelect = document.querySelector("#msgSelect").value;
    const tokenInput = document.querySelector("#apiTokenPrivate");
    const apiTokenPrivate = tokenInput ? tokenInput.value.trim() : currentTokenPrivate;

    // --- COLETA DADOS GRUPOS ---
    const minIntervalGrp = parseInt(document.querySelector("#minIntervalGrp").value);
    const maxIntervalGrp = parseInt(document.querySelector("#maxIntervalGrp").value);
    const limitMessagesGrp = parseInt(document.querySelector("#limitMessagesGrp").value);
    const sendStickersGrp = document.querySelector("#sendStickersGrp").checked;
    const msgSelectGrp = document.querySelector("#msgSelectGrp").value;
    const tokenInputGrp = document.querySelector("#apiTokenGroup");
    const apiTokenGroup = tokenInputGrp ? tokenInputGrp.value.trim() : currentTokenGroup;

    // --- NOVA COLETA: Captura a seleção de cada dropdown dinâmico ---
    let updatedGroupTargets = {};
    document.querySelectorAll(".chip-group-selector").forEach(select => {
        const chip = select.getAttribute("data-chip");
        const groupId = select.value;
        if (groupId) {
            updatedGroupTargets[chip] = groupId;
        }
    });

    // Atualiza globais
    currentTokenPrivate = apiTokenPrivate;
    currentTokenGroup = apiTokenGroup;

    // --- VALIDAÇÕES DE SEGURANÇA (Original mantida e expandida) ---
    if (
        !minInterval || !maxInterval || !switchAccountAfter || minInterval >= maxInterval || !limitMessages || limitMessages <= 0 || switchAccountAfter <= 0 ||
        !minIntervalGrp || !maxIntervalGrp || minIntervalGrp >= maxIntervalGrp || !limitMessagesGrp || limitMessagesGrp <= 0
    ) {
        window.controller.show_alert(
            "Maturador de chips",
            "Erro ao cadastrar novas configurações, verifique se os intervalos e limites estão corretos (o tempo mínimo não pode ser maior ou igual ao máximo)."
        );
        return; 
    }

    if (msgSelect === "openai" && apiTokenPrivate === "") {
        window.controller.show_alert("Maturador de chips", "O método Privado requer um token de API da OpenAI. Por favor, preencha o campo.");
        return;
    }

    if (msgSelectGrp === "openai" && apiTokenGroup === "") {
        window.controller.show_alert("Maturador de chips", "O método de Grupos requer um token de API da OpenAI. Por favor, preencha o campo.");
        return;
    }

    // Cria objeto de configurações completo
    const preferences = {
        // Gerais e Privado
        ShutdownAfterCompletion: shutdown,
        PlaySound: sound,
        ContinueIfDisconnected: continue_,
        MinInterval: minInterval,
        MaxInterval: maxInterval,
        LimitMessages: limitMessages,
        switchAccountAfter: switchAccountAfter,
        MessageType: msgSelect,
        ApiToken: apiTokenPrivate,
        selectedFilePath: savedFilePathPrivate, // Puxa direto da variável que o selectFile() do HTML alimentou

        // Grupos dinâmicos mapeados por Chip
        GroupMaturationTargets: updatedGroupTargets,
        MinIntervalGrp: minIntervalGrp,
        MaxIntervalGrp: maxIntervalGrp,
        LimitMessagesGrp: limitMessagesGrp,
        SendStickersGrp: sendStickersGrp,
        MessageTypeGrp: msgSelectGrp,
        ApiTokenGrp: apiTokenGroup,
        SelectedFilePathGrp: savedFilePathGroup // Puxa direto da variável que o selectFile() do HTML alimentou
    };

    // Envia para backend mantendo a estrutura de Promises
    window.controller.update_user_configs(JSON.stringify(preferences))
    .then(() => {
        // Atualiza a memória local após salvar com sucesso
        savedGroupTargets = updatedGroupTargets;
        window.controller.show_alert("Maturador de chips", "Configurações salvas com sucesso!");
    })
    .catch(err => {
        console.error("Erro ao salvar configurações:", err);
        window.controller.show_alert("Maturador de chips", "Erro ao salvar configurações. Verifique o arquivo de log para mais detalhes.");
    });
});