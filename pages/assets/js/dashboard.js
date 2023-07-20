const arquivoInput = document.getElementById('arquivoInput');
const arquivoInputLabel = document.getElementById('arquivoInputLabel');

arquivoInput.addEventListener("change", async function () {
  const file = arquivoInput.files[0];

  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('/api/selected-messages-file', {
      method: 'POST',
      body: formData
    });

    if (response.ok) {
      const data = await response.json();

      if (data.ok) {
        arquivoInputLabel.textContent = arquivoInput.files[0].name;
        $.notify("alterações foram salvas com êxito", "success");
  
      } else {
        $.notify(data.message, "error");
      }
    } else {

      $.notify("erro ao processar arquivo", "error");
    }
  } catch (error) {

    $.notify("erro ao processar arquivo", "error");
  }

  arquivoInput.value = "";
});

// processa o pedido para atualizar as configurações

function update_config_send() {
    const stopWithBlock = document.querySelector("#banimentoCheckbox").checked ? "True" : "False";
    const minMessageInterval = document.querySelector("#intervaloMinInput").value;
    const maxMessageInterval = document.querySelector("#intervaloMaxInput").value;
    const changeAccountAfterMessages = document.querySelector("#trocarContaInput").value;
    const stopAfterMessages = document.querySelector("#pararAposInput").value;
    const notValidValues = ['', '0' , 0];

    // antes de enviar valida as informações

    if (
      notValidValues.includes(minMessageInterval) 
      || notValidValues.includes(maxMessageInterval)
      || notValidValues.includes(changeAccountAfterMessages)
      || notValidValues.includes(stopAfterMessages)
      || Number(minMessageInterval) < 0
      || Number(maxMessageInterval) < 0
      || Number(changeAccountAfterMessages) < 0
      || Number(stopAfterMessages) < 0
      || Number(maxMessageInterval) <= Number(minMessageInterval)
      ) {
      
      $.notify("verifique os dados informados", "error");
    }

     // tudo certo,  enviar as novas configurações

    else{


        const dadosAtualizados = {
          continue_with_block: stopWithBlock,
          min_message_interval: minMessageInterval,
          max_message_interval: maxMessageInterval,
          change_account_after_messages: changeAccountAfterMessages,
          stop_after_messages: stopAfterMessages
        };
      
        const url = "/api/update-configs";
      
        fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(dadosAtualizados)
        })
        .then(response => {
          if (response.ok) {

            $.notify("alterações foram salvas com êxito", "success");

          } else {
            $.notify("as alterações não foram salvas", "error");
          }
        })
        .catch(error => {
          $.notify("as alterações não foram salvas", "error");
        });
      }
  }
  
  document.querySelector("#banimentoCheckbox").addEventListener("change", update_config_send);
  document.querySelector("#intervaloMinInput").addEventListener("change", update_config_send);
  document.querySelector("#intervaloMaxInput").addEventListener("change", update_config_send);
  document.querySelector("#trocarContaInput").addEventListener("change", update_config_send);
  document.querySelector("#pararAposInput").addEventListener("change", update_config_send);  


  // abrir repositório do projeto

  document.getElementById("GithubOpen").addEventListener("click", function request_github_open(){

    let xhr = new XMLHttpRequest()
    xhr.open("GET", "/api/github-open", true)
    xhr.send()
  })

  // abrir a licença de código do projeto

  document.getElementById("LicenseOpen").addEventListener("click", function request_license_open(){

      let xhr = new XMLHttpRequest()
      xhr.open("GET", "/api/license-open", true)
      xhr.send()
    })

  // mostrar versão do projeto

    document.getElementById("VersionView").addEventListener("click", function request_version_view(){

      let xhr = new XMLHttpRequest()
      xhr.open("GET", "/api/version-view", true)
      xhr.send()
      })
  
  // mostrar a pagina do nubank de pix

    document.getElementById("PixOpen").addEventListener("click", function (){

      let xhr = new XMLHttpRequest()
      xhr.open("GET", "/api/apoia-pix-open", true)
      xhr.send()
      })

  // mostrar todas as contas conectadas

document.querySelectorAll(".btn-whatsapp").forEach(

  button => {
    if (button.textContent == "Ver contas conectadas"){

      button.addEventListener("click", function view_accounts(){

        let xhr = new XMLHttpRequest()
        xhr.open("GET", "/api/accounts-view", true)
        xhr.send()
        })
    }
  }
)

// enviar pedido para iniciar a maturação

document.querySelectorAll(".btn-whatsapp").forEach(

  button => {
    if (button.textContent == "Iniciar maturador"){

      button.addEventListener("click", function view_accounts(){

        let xhr = new XMLHttpRequest()
        xhr.open("GET", "/api/start-maturation", true)
        xhr.send()
        })
    }
  }
)