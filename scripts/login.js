// enviar o numero de telefone dessa instancia para "web.whatssap.com"
// para ser interceptada e esse dado ser processado pela API do programa. 

function SendPhoneNumber(phone) {
  const instanceName = "@INSTANCE"
  const url = `/maturador/api/account-added/{"instance":"${instanceName}", "phone":"${phone}"}`
  xhr = new XMLHttpRequest()
  xhr.open("GET", url, true)
  xhr.send()
}

// verifica a cada 0 milisegundos se um conta foi adiconada, se sim, e clica no painel de novas conversas
// e busca na lista de contatos o numero da conta atual, em seguida fecha a lista de contatos

function verificarConexaoWhatsApp() {
  let newChat = document.querySelector('[aria-label="Nova conversa"]');
  if (newChat) {
    newChat.click();

    setTimeout(() => {
      let closeNewChat = document.querySelector('[data-testid="btn-closer-drawer"]');
      if (closeNewChat) {
        setTimeout(() => {
          let MyPhone = document.querySelector('[data-testid="message-yourself-row"]').textContent.split(")")[0].split("(")[0];
          SendPhoneNumber(MyPhone)
          closeNewChat.click();
        }, 0);
      }
    }, 0);

  } else {
    setTimeout(() => {
      verificarConexaoWhatsApp();
    }, 0);
  }
}

verificarConexaoWhatsApp();