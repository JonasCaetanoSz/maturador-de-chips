/**
   * Cria uma intancia de chat com usuario
   
  * @param {Object} model - Instancia de modelo de Chat do whatsapp
  * @param {Object} wid - Whatssapp ID do usuario
  */

class Chat {
 
  constructor(model, wid){
    this._model = model
    this._user_wid = wid
};

  /**
   * Abrir o chat com o usuario e opcionalmente digitar uma mensagem
   * 
   * @param {string} message - Mensagem a ser digitada no campo de mensagem
   * @returns {Promise<boolean>} - Retorna true se o chat foi aberto
  */

  async open(message) {

      await window.require("WAWebCmd").Cmd.openChatBottom({"chat": this._model});
      await this.clearMessageTextArea();

      if (message){

        await this.setMessageTextAreaContent(message);

      };

      const editor = document.querySelector("[aria-placeholder='Digite uma mensagem']");

      if (!editor){

        return false;
      } 

      return true;
};

  /**
   * Fechar chat com usuario 
   * 
   * @returns {Promise<boolean>} - Retorna true se o chat foi fechado
  */

  async close() {

    await window.require("WAWebCmd").Cmd.closeChat(this._model);

    return new Promise(resolve => {
      const selector = "[aria-placeholder='Digite uma mensagem']";

      if (!document.querySelector(selector)) {
        return resolve(true);
      }

      const observer = new MutationObserver(() => {
        const exists = !!document.querySelector(selector);
        if (!exists) {
          observer.disconnect();
          resolve(true);
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });

      setTimeout(() => {
        observer.disconnect();
        resolve(false);
      }, 5000);
    });
};


  /**
   * Limpar campo de Mensagem
   * 
   * @returns {Promise<boolean>} - Retorna true se o campo foi limpado
  */

  async clearMessageTextArea() {

    const inputElement = document.querySelector("[aria-placeholder='Digite uma mensagem']");
    const editor = inputElement["__lexicalEditor"];
    
    if (!editor){
      return false;
    };

    await window.require("WAWebLexicalUtils").setTextContent(editor, "")

    if (inputElement.textContent === "" ){
      return true
    };

    return false;
};

  /**
   * Digitar no campo de mensagens 
   * 
   * @param {string} message - Mensagem a ser digitada no campo de mensagem
   * @returns {Promise<boolean>} - Retorna true se a mensagem for digitada
  */

  async setMessageTextAreaContent(message) {

    const inputElement = document.querySelector("[aria-placeholder='Digite uma mensagem']");
    const editor = inputElement["__lexicalEditor"];
    if (!editor){
      return false;
    };

    await window.require("WAWebLexicalUtils").setTextContent(editor, message)
    
    if (inputElement.textContent.includes(message)){

      return true;

    };

    return false;
};

  /**
   * Fixar chat
   * 
   * @returns {Promise<boolean>} - Retorna true se o chat for fixado
  */

  async pin(){
      await window.require("WAWebCmd").Cmd.pinChat(this._model, true)
      return true;
};

 /**
   * Desafixar chat
   * 
   * @returns {Promise<boolean>} - Retorna true se o chat for desafixado
  */

  async unpin(){
      await window.require("WAWebCmd").Cmd.pinChat(this._model, false)
      return true;
};

 /**
   * Silenciar chat para sempre
   * 
   * @returns {Promise<boolean>} - Retorna true se o chat for silenciado
  */

  async mute(){
      await window.require("WAWebCmd").Cmd.muteChat(this._model, true, 0)
      return true;
};

/**
 * Ativar som de notificações
 * 
 * @returns {Promise<boolean>} - Retorna true se as notificações forem ativadas
*/

  async unmute(){
    return new Promise(async(resolve, reject) => {
      window.require("WAWebCmd").Cmd.muteChat(this._model, false)
    })
};


/**
 * Arquivar chat
 * 
 * @returns {Promise<boolean>} - Retorna true se o chat for arquivado
*/
  
  async archive(){
      await window.require("WAWebCmd").Cmd.archiveChat(this._model, true)
};

/**
 * Desarquivar chat
 * 
 * @returns {Promise<boolean>} - Retorna true se o chat for desarquivado
*/
  
  async unarchive() {
    await window.require("WAWebCmd").Cmd.archiveChat(this._model, false)
};

/**
 * Marcar como lida
 * 
 * @returns {Promise<boolean>} - Retorna true se o chat for marcado como lido
*/

  async markAsRead(){
      await window.require("WAWebCmd").Cmd.markChatUnread(this._model, false)
};

/**
 * Marcar como não lida
 * 
 * @returns {Promise<boolean>} - Retorna true se o chat for marcado como não lido
*/

  async MarkAsUnread(){
      window.require("WAWebCmd").Cmd.markChatUnread(this._model, true)
};

/**
 * Enviar uma mensagem de texto
 * 
 * @param {string} content - Texto da Mensagem a ser enviada
 * @returns {Promise<boolean>} - Retorna true se a mensagem for enviada
*/

  async sendMessage(content){
        
    const MsgKey =  window.require("WAWebMsgKey");
    const lidUser = window.require('WAWebUserPrefsMeUser').getMaybeMeLidUser();
    const meUser = window.require('WAWebUserPrefsMeUser').getMaybeMePnUser();
    const newId = await MsgKey.newId();

    const from = this._model.id.isLid() ? lidUser : meUser;
    const key = new MsgKey({
          from: from,
          to: this._model.id,
          id: newId , 
          participant: undefined,
          selfDir: 'out',
    });

    const ephemeralFields = await window.require("WAWebGetEphemeralFieldsMsgActionsUtils").getEphemeralFields(this._model)
    const message = {
      id: key,
      ack: 0,
      body: content,
      from: meUser,
      to: this._model.id,
      local: true,
      self: 'out',
      t: parseInt(new Date().getTime() / 1000),
      isNewMsg: true,
      type: 'chat',
      disappearingModeInitiator: "chat",
      disappearingModeTrigger: "chat_settings",
      parseVCards: true,
      mentionedJidList: [],
      ignoreQuoteErrors: true,
      waitUntilMsgSent: false,
      ...ephemeralFields
  };

    const msgStatus = window.require('WAWebSendMsgChatAction').addAndSendMsgToChat(this._model, message);
    window.require('WAWebStreamModel').Stream.markAvailable();
    window.require('WAWebUpdateUnreadChatAction').sendSeen(chat);
    window.require('WAWebStreamModel').Stream.markUnavailable()
    const senderStatus = await msgStatus[1];
        
    if (await senderStatus["messageSendResult"] === "OK"){

      return true;
    };

    return false;
    
};};


/**
 * Cria uma intancia de usuario

* @param {Object} wid - Whatssapp ID do usuario
*/

class User{

  constructor(wid){
    this._wid = wid;
    this._chat = null;
};

/**
 * Numero de telefone do usuario
 * 
 * @returns {Promise<String|false>} - Retorna o numero de telefone
*/

  async phone(){
    const phoneNumber = this._wid.user;

    if (phoneNumber){

      return phoneNumber;

    }

    return false;
};

/**
 * Foto de perfil perfil do usuario
 * 
 * @returns {Promise<object|false>} - Retorna biografia do usuario
*/

  async profilePic(){
    const picture = await window.require("WAWebContactProfilePicThumbBridge").requestProfilePicFromServer(this._wid);
    
    if ( picture.eurl ){

      return picture;

    };

    return false;
    
};

/**
 * Biografia do usuario
 * 
 * @returns {Promise<String|false>} - Retorna biografia do usuario
*/

  async biograpy(){
    const bio = await window.require("WAWebContactStatusBridge").getStatus({"wid": this._wid}) 
    
    if (bio.status){

      return bio.status;

    };
  
    return false;
};

/**
 * Bloquear usuario
 * 
 * @returns {Promise<Boolean>} - Retorna true se usuario for bloqueado
*/
  async block(){

    const contact = await window.require("WAWebCollections").Contact.get(this._wid);
    await window.require("WAWebBlockContactAction").blockContact(
    {
      "contact": contact,
      "blockEntryPoint":"profile"
    });

    return true;
};

/**
 * Desbloquear usuario
 * 
 * @returns {Promise<Boolean>} - Retorna true se usuario for desbloqueado
*/
  async unblock(){
      const contact = await window.require("WAWebCollections").Contact.get(this._wid);
      await window.require("WAWebBlockContactAction").unblockContact(contact)
      return true;
  }

/**
 * Instancia de chat do usuario

* @returns {Promise<Chat|false>} - Retorna uma instacia Chat do usuario
*/
  async getChat() {
    const wid = window.require("WAWebWidFactory").createWid(this._wid._serialized);
    const lid = await window.require("WAWebLidMigrationUtils").getPnAndLidToUpdate(wid)
    const model = await window.require("WAWebFindChatAction").findOrCreateLatestChat(wid, { getAsModel: false })
    
    if (model.chat) {
      return new Chat(model.chat, wid);
    };
  
  return false;

}};

 /**
   * Cria uma intancia de Wtools
*/

class WhatsAppTools  {

  constructor (){
    this.onReady(() => {
    this.myWid = window.require("WAWebUserPrefsMeUser").getMaybeMePnUser() || window.require("WAWebUserPrefsMeUser").getMaybeMeLidUser();
    this.myLid = window.require("WAWebUserPrefsMeUser").getMaybeMeLidUser()
    
    })
};

/**
 * Puxar informações da conta conectada

* @returns {Promise<Object|false>} - Retorna dados do perfil
*/

  async myProfileShortDetails() {

    if (this.myWid){
      return {
        "display_name": await window.require("WAWebUserPrefsGeneral").getPushname(),
        "biograpy": ( await window.require("WAWebContactStatusBridge").getStatus({"token":"", "wid": this.myLid}) ).status,
        "phone": await window.require("WAWebUserPrefsMeUser").getMaybeMePnUser().user ,
        "profilePic": await window.require("WAWebContactProfilePicThumbBridge").requestProfilePicFromServer(this.myWid),
        "privacy": await window.require("WAWebUserPrefsGeneral").getUserPrivacySettings(),
    };
  }

  return false;

};

/**
 * Instancia de usuario

* @returns {Promise<User>} - Retorna uma instacia usuario
*/

  async GetUser(id){
    const _id = id.indexOf("@") > -1 ? id : id + this.myWid._serialized.match(/@(.*)/)[0];
    const wid =  window.require("WAWebWidFactory").createWid(_id);

    if (wid){
      return new User(wid);
    };

  return false;

};

/**
 * Pegar Qr code para se conectar

* @returns {Promise<String|false>} - Retorna o texto do Qr code

*/

    async getQr(){
      const registrationInfo = await window.require("WAWebSignalStoreApi").waSignalStore.getRegistrationInfo()
      const noiseKeyPair = await  window.require("WAWebUserPrefsInfoStore").waNoiseInfo.get();
      const staticKeyB64 = await window.require("WABase64").encodeB64(noiseKeyPair.staticKeyPair.pubKey);
      const identityKeyB64 = await  window.require("WABase64").encodeB64(registrationInfo.identityKeyPair.pubKey);
      const advSecretKey = await  window.require("WAWebAdvSignatureApi").getADVSecretKey();
      const platform = window.require("WAWebCompanionRegClientUtils").DEVICE_PLATFORM;
      const ref =  window.require("WAWebConnModel").Conn.ref;
      const qrCode =  ref + ',' + staticKeyB64 + ',' + identityKeyB64 + ',' + advSecretKey + ',' + platform;

      if (ref){
        
        return qrCode;
      };

    return false;
    }
    
/**
 * Definir uma função para escutar o evento de troca do qr code
 * 
 * @param {Function} callback - função que vai escutar o evento
*/

  async setQrCodeChangeEventListenner(callback){

    window.require("WAWebConnModel").Conn.on('change:ref', async (_, ref) => { callback( await this.getQr(ref)) });
    return true;
  };

/**
 * Desconectar do whatsapp web
 * 
*/
  async logout(){
   window.require("WAWebSocketModel").Socket.logout();

};

/**
 * Definir uma função para escutar o evento de whatsapp conectado
 * 
 * @param {Function} callback - função que vai escutar o evento
*/

  async onReady(callback){
    window.require("WAWebSocketModel").Socket.on('change:state', (_AppState , state) => { 

      if (state === "CONNECTED"){
        callback();
      };

      });
};

/**
 * Definir uma função para escutar o evento de whatsapp desconectado
 * 
 * @param {Function} callback - função que vai escutar o evento
*/

  async onDisconnected(callback){
    window.require("WAWebSocketModel").Socket.on('change:state', (_AppState , state) => { 

      if (state === "DISCONNECTED"){
        callback()
      }

      })   
  }
}

window.sessionName = "@instanceName";

// Enviar numero de telefone e foto para o programa

function SendPhoneNumber(phone, eurl) {
  const url = `/maturador/api/account-added?sessionName=${encodeURIComponent(window.sessionName)}&phone=${encodeURIComponent(phone)}&photo=${encodeURIComponent(eurl)}`;
  xhr = new XMLHttpRequest()
  xhr.open("GET", url, true)
  xhr.send()
}

// Função que espera modulos ficarem prontos

function waitForModuleSystem() {
    return new Promise(resolve => {
        const test = () => {
            try {
                const mod = window.require("WAWebUserPrefsMeUser");
                const myLid = window.require("WAWebUserPrefsMeUser").getMaybeMeLidUser()

                if (mod  && myLid) {
                    resolve();
                    return;
                }
            } catch {}
            setTimeout(test, 50);
        };
        test();
    });
}


// Aguardar os modulos ficarem disponiveis

waitForModuleSystem().then(() => {

    window.WTools = new WhatsAppTools()
    window.WTools.onReady(async() => {
    var me = await window.WTools.myProfileShortDetails();
    SendPhoneNumber(me.phone, me.profilePic.eurl)
})

});


