// enviar o numero de telefone dessa instancia para "web.whatssap.com"
// para ser interceptada e esse dado ser processado pela API do programa. 

const session_name = "@SESSIONNAME"

function SendPhoneNumber(phone) {
  const instance_index = "@INSTANCE"
  const url = `/maturador/api/account-added/{"instance":"${instance_index}", "sessionName": "${session_name}" , "phone":"${phone}"}`
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