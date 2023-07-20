// enviar o numero de telefone dessa instancia para "web.whatssap.com"
// para ser interceptada e esse dado ser processado pela API do programa. 

function SendPhoneNumber(phone) {
  const instanceName = "@INSTANCE"
  const url = `/maturador/api/account-added/{"instance":"${instanceName}", "phone":"${phone}"}`
  xhr = new XMLHttpRequest()
  xhr.open("GET", url, true)
  xhr.send()
}

// verifica a cada 0 milisegundos se um conta foi adiconada, se sim, encontra o nmero de telefone da conta atual no aramazenamento local

function verificarConexaoWhatsApp() {
  let ElementReference = document.getElementById("pane-side");
  if (ElementReference) {

    let accountPhone = localStorage.getItem("last-wid-md");
    let accountPhoneProcessed = accountPhone.split(":")[0].replace('"', "");
    SendPhoneNumber(accountPhoneProcessed);

  } else {

    setTimeout(() => {
      verificarConexaoWhatsApp();
    }, 0);
    
  }
}

verificarConexaoWhatsApp();