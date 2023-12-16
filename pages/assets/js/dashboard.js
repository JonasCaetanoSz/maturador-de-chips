const fileInputLabel = document.getElementById('fileInputLabel');

// processa o pedido para atualizar as configurações

function update_user_config() {
    const ContinueOnBlock = document.querySelector("#ContinueOnBlock").checked ;
    const ShutdownAfterCompletion = document.querySelector("#ShutdownAfterCompletion").checked ;
    const MinimumMessageInterval = document.querySelector("#MinimumMessageInterval").value;
    const MaximumMessageInterval = document.querySelector("#MaximumMessageInterval").value;
    const ChangeAccountEveryMessages = document.querySelector("#ChangeAccountEveryMessages").value;
    const stopAfterMessages = document.querySelector("#stopAfterMessages").value;
    const notValidValues = ['', '0' , 0];

    // antes de enviar validar as informações

    if (
      notValidValues.includes(MinimumMessageInterval) 
      || notValidValues.includes(MaximumMessageInterval)
      || notValidValues.includes(ChangeAccountEveryMessages)
      || notValidValues.includes(stopAfterMessages)
      || Number(MinimumMessageInterval) < 0
      || Number(MaximumMessageInterval) < 0
      || Number(ChangeAccountEveryMessages) < 0
      || Number(stopAfterMessages) < 0
      || Number(MaximumMessageInterval) <= Number(MinimumMessageInterval)
      ) {
      
      $.notify("verifique os dados informados", "error");
    }

     // tudo certo,  enviar as novas configurações

    else{

        const dadosAtualizados = {
          "ContinueOnBlock": ContinueOnBlock,
          "MinimumMessageInterval": MinimumMessageInterval,
          "MaximumMessageInterval": MaximumMessageInterval,
          "ChangeAccountEveryMessages": ChangeAccountEveryMessages,
          "StopAfterMessages": stopAfterMessages,
          "ShutdownAfterCompletion": ShutdownAfterCompletion
        };

        controller.update_user_configs(JSON.stringify(dadosAtualizados)).then(response =>   {
            response = JSON.parse(response)
            $.notify(response.message, { className: response.ok ? "success" : "error"});
      } )
      }
  }
  
  document.querySelector("#ContinueOnBlock").addEventListener("change", update_user_config);
  document.querySelector("#ShutdownAfterCompletion").addEventListener("change", update_user_config);
  document.querySelector("#MinimumMessageInterval").addEventListener("change", update_user_config);
  document.querySelector("#MaximumMessageInterval").addEventListener("change", update_user_config);
  document.querySelector("#ChangeAccountEveryMessages").addEventListener("change", update_user_config);
  document.querySelector("#stopAfterMessages").addEventListener("change", update_user_config);  


  // abrir repositório do projeto

  document.getElementById("GithubOpen").addEventListener("click", () => {
    controller.open_project_repository();
  })

  // abrir a licença de código do projeto

  document.getElementById("LicenseOpen").addEventListener("click",() => {
    controller.open_project_license();
    })

  // mostrar versão do projeto

    document.getElementById("VersionView").addEventListener("click", () => {
      controller.view_project_version();
      })
  
  // mostrar a pagina de issues do github

    document.getElementById("issues").addEventListener("click",  () =>{
      controller.open_project_issues();
      })
  
    // mostrar a pagina de numero virtual

    document.getElementById("virtual-number").addEventListener("click",  () =>{
      controller.telegram_virtual_number_bot_open();
    })

      // mostrar a pagina de disparador

      document.getElementById("disparador").addEventListener("click",  () =>{
        controller.disparador();
        })
    
  // mostrar todas as contas conectadas

      document.querySelector(".all-accounts").addEventListener("click",  () =>{
        controller.view_accounts();
        })

// enviar pedido para iniciar a maturação

document.querySelector(".start-maturador").addEventListener("click",  () =>{
  controller.start_maturation();
  })

  // selecionar o arquivo de mensagens

  document.querySelector("#files").addEventListener("click", () => {
    controller.select_file().then(response =>   
        {
      response = JSON.parse(response)
      $.notify(response.message, { className: response.ok ? "success" : "error"});
      document.querySelector("#fileInputLabel").textContent = response["filename"]
    } )
   

  })


  // carregando as configurações do usuário

  controller.get_user_configs().then(configs => {
  configs = JSON.parse(configs);
  document.querySelector("#ContinueOnBlock").checked = configs["ContinueOnBlock"]
  document.querySelector("#ShutdownAfterCompletion").checked = configs["ShutdownAfterCompletion"]
  document.querySelector("#ChangeAccountEveryMessages").value = configs["ChangeAccountEveryMessages"]
  document.querySelector("#stopAfterMessages").value = configs["StopAfterMessages"]
  document.querySelector("#MinimumMessageInterval").value = configs["MinimumMessageInterval"]
  document.querySelector("#MaximumMessageInterval").value = configs["MaximumMessageInterval"]
  fileInputLabel.textContent = configs["filename"]

  const accounts_container = document.querySelector(".home-container02")
  Object.keys(configs["accounts"]).forEach(key => {

    accounts_container.innerHTML += ` <div class="home-container03">
      <div class="home-container04">
        <span class="home-text03"> ${ configs["accounts"][key] } </span>
        <svg viewBox="0 0 877.7142857142857 1024" class="home-icon2">
          <path
            d="M562.857 556.571c9.714 0 102.857 48.571 106.857 55.429 1.143 2.857 1.143 6.286 1.143 8.571 0 14.286-4.571 30.286-9.714 43.429-13.143 32-66.286 52.571-98.857 52.571-27.429 0-84-24-108.571-35.429-81.714-37.143-132.571-100.571-181.714-173.143-21.714-32-41.143-71.429-40.571-110.857v-4.571c1.143-37.714 14.857-64.571 42.286-90.286 8.571-8 17.714-12.571 29.714-12.571 6.857 0 13.714 1.714 21.143 1.714 15.429 0 18.286 4.571 24 19.429 4 9.714 33.143 87.429 33.143 93.143 0 21.714-39.429 46.286-39.429 59.429 0 2.857 1.143 5.714 2.857 8.571 12.571 26.857 36.571 57.714 58.286 78.286 26.286 25.143 54.286 41.714 86.286 57.714 4 2.286 8 4 12.571 4 17.143 0 45.714-55.429 60.571-55.429zM446.857 859.429c197.714 0 358.857-161.143 358.857-358.857s-161.143-358.857-358.857-358.857-358.857 161.143-358.857 358.857c0 75.429 24 149.143 68.571 210.286l-45.143 133.143 138.286-44c58.286 38.286 127.429 59.429 197.143 59.429zM446.857 69.714c237.714 0 430.857 193.143 430.857 430.857s-193.143 430.857-430.857 430.857c-72.571 0-144.571-18.286-208.571-53.714l-238.286 76.571 77.714-231.429c-40.571-66.857-61.714-144-61.714-222.286 0-237.714 193.143-430.857 430.857-430.857z"
          ></path>
        </svg>
      </div>
      <div class="home-container05">
        <span class="home-text04">${ key.replace("@", "") }</span>
      </div>
    </div>`
  })
  

})