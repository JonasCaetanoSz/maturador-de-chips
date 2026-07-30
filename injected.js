class Chat {
  constructor(model, wid) {
    this._model = model;
    this._user_wid = wid;
  }

  async open(message) {
    try {
      await window.require("WAWebCmd").Cmd.openChatBottom({ "chat": this._model });
      await this.clearMessageTextArea();

      if (message) {
        await this.setMessageTextAreaContent(message);
      }

      const editor = document.querySelector("[aria-placeholder='Digite uma mensagem']");
      return !!editor;
    } catch (e) {
      return false;
    }
  }

  async close() {
    try {
      await window.require("WAWebCmd").Cmd.closeChat(this._model);
      const selector = "[aria-placeholder='Digite uma mensagem']";
      return !document.querySelector(selector);
    } catch (e) {
      return false;
    }
  }

  async clearMessageTextArea() {
    try {
      const inputElement = document.querySelector("[aria-placeholder='Digite uma mensagem']");
      if (!inputElement) return false;
      const editor = inputElement["__lexicalEditor"];
      if (!editor) return false;

      await window.require("WAWebLexicalUtils").setTextContent(editor, "");
      return inputElement.textContent === "";
    } catch (e) {
      return false;
    }
  }

  async setMessageTextAreaContent(message) {
    try {
      const inputElement = document.querySelector("[aria-placeholder='Digite uma mensagem']");
      if (!inputElement) return false;
      const editor = inputElement["__lexicalEditor"];
      if (!editor) return false;

      await window.require("WAWebLexicalUtils").setTextContent(editor, message);
      return inputElement.textContent.includes(message);
    } catch (e) {
      return false;
    }
  }

  async pin() {
    try {
      await window.require("WAWebCmd").Cmd.pinChat(this._model, true);
      return true;
    } catch (e) { return false; }
  }

  async unpin() {
    try {
      await window.require("WAWebCmd").Cmd.pinChat(this._model, false);
      return true;
    } catch (e) { return false; }
  }

  async mute() {
    try {
      await window.require("WAWebCmd").Cmd.muteChat(this._model, true, 0);
      return true;
    } catch (e) { return false; }
  }

  async unmute() {
    try {
      window.require("WAWebCmd").Cmd.muteChat(this._model, false);
      return true;
    } catch (e) { return false; }
  }

  async archive() {
    try {
      await window.require("WAWebCmd").Cmd.archiveChat(this._model, true);
    } catch (e) {}
  }

  async unarchive() {
    try {
      await window.require("WAWebCmd").Cmd.archiveChat(this._model, false);
    } catch (e) {}
  }

  async markAsRead() {
    try {
      await window.require("WAWebCmd").Cmd.markChatUnread(this._model, false);
    } catch (e) {}
  }

  async MarkAsUnread() {
    try {
      window.require("WAWebCmd").Cmd.markChatUnread(this._model, true);
    } catch (e) {}
  }

  async sendMessage(content) {
    try {
      const MsgKey = window.require("WAWebMsgKey");
      const lidUser = window.require('WAWebUserPrefsMeUser').getMaybeMeLidUser();
      const meUser = window.require('WAWebUserPrefsMeUser').getMaybeMePnUser();
      const newId = await MsgKey.newId();

      const from = this._model.id.isLid() ? lidUser : meUser;
      const key = new MsgKey({
        from: from,
        to: this._model.id,
        id: newId,
        participant: undefined,
        selfDir: 'out',
      });

      const ephemeralFields = await window.require("WAWebGetEphemeralFieldsMsgActionsUtils").getEphemeralFields(this._model);
      const message = {
        id: key,
        ack: 0,
        body: content,
        from: meUser,
        to: this._model.id,
        local: true,
        self: 'out',
        t: Math.floor(Date.now() / 1000),
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
      window.require('WAWebUpdateUnreadChatAction').sendSeen(this._model);
      window.require('WAWebStreamModel').Stream.markUnavailable();
      
      const senderStatus = await msgStatus[1];
      return (await senderStatus["messageSendResult"]) === "OK";
    } catch (e) {
      return false;
    }
  }
}

class User {
  constructor(wid) {
    this._wid = wid;
    this._chat = null;
  }

  async phone() {
    return this._wid.user || false;
  }

  async profilePic() {
    try {
      const chatObj = await this.getChat();
      if (!chatObj) return false;
      this._chat = chatObj._model;
      const picture = await window.require("WAWebContactProfilePicThumbBridge").requestProfilePicFromServer(this._chat);
      return picture.eurl ? picture : false;
    } catch (e) {
      return false;
    }
  }

  async biograpy() {
    try {
      const bio = await window.require("WAWebContactStatusBridge").getStatus({ "wid": this._wid });
      return bio.status || false;
    } catch (e) {
      return false;
    }
  }

  async block() {
    try {
      const chatObj = await this.getChat();
      if (!chatObj) return false;
      this._chat = chatObj._model;
      await window.require('WAWebBlockContactAction').blockContact({ contact: this._chat.contact });
      return true;
    } catch (e) {
      return false;
    }
  }

  async unblock() {
    try {
      const chatObj = await this.getChat();
      if (!chatObj) return false;
      this._chat = chatObj._model;
      await window.require("WAWebBlockContactAction").unblockContact(this._chat.contact);
      return true;
    } catch (e) {
      return false;
    }
  }

  async getChat() {
    try {
      const wid = window.require("WAWebWidFactory").createWid(this._wid._serialized);
      const model = await window.require("WAWebFindChatAction").findOrCreateLatestChat(wid, { getAsModel: false });
      return model.chat ? new Chat(model.chat, wid) : false;
    } catch (e) {
      return false;
    }
  }
}

class WhatsAppTools {
  constructor() {
    try {
      const prefs = window.require("WAWebUserPrefsMeUser");
      this.myWid = prefs.getMaybeMePnUser() || prefs.getMaybeMeLidUser();
      this.myLid = prefs.getMaybeMeLidUser();
    } catch (e) {
      this.myWid = null;
      this.myLid = null;
    }
  }

  async myProfileShortDetails() {
    if (this.myWid) {
      try {
        const model = { id: this.myWid, isGroup: false };
        const pushname = await window.require("WAWebUserPrefsGeneral").getPushname();
        const bioObj = await window.require("WAWebContactStatusBridge").getStatus({ "token": "", "wid": this.myLid });
        const phone = window.require("WAWebUserPrefsMeUser").getMaybeMePnUser().user;
        const profilePic = await window.require("WAWebContactProfilePicThumbBridge").requestProfilePicFromServer(model);
        const privacy = await window.require("WAWebUserPrefsGeneral").getUserPrivacySettings();

        return {
          "display_name": pushname,
          "biograpy": bioObj ? bioObj.status : "",
          "phone": phone,
          "profilePic": profilePic,
          "privacy": privacy,
        };
      } catch (e) {
        return false;
      }
    }
    return false;
  }

  async GetUser(id) {
    try {
      const suffix = id.indexOf("@") > -1 ? id : id + this.myWid._serialized.match(/@(.*)/)[0];
      const wid = window.require("WAWebWidFactory").createWid(suffix);
      return wid ? new User(wid) : false;
    } catch (e) {
      return false;
    }
  }

  async getQr() {
    try {
      const registrationInfo = await window.require("WAWebSignalStoreApi").waSignalStore.getRegistrationInfo();
      const noiseKeyPair = await window.require("WAWebUserPrefsInfoStore").waNoiseInfo.get();
      const staticKeyB64 = await window.require("WABase64").encodeB64(noiseKeyPair.staticKeyPair.pubKey);
      const identityKeyB64 = await window.require("WABase64").encodeB64(registrationInfo.identityKeyPair.pubKey);
      const advSecretKey = await window.require("WAWebAdvSignatureApi").getADVSecretKey();
      const platform = window.require("WAWebCompanionRegClientUtils").DEVICE_PLATFORM;
      const ref = window.require("WAWebConnModel").Conn.ref;

      if (ref) {
        return ref + ',' + staticKeyB64 + ',' + identityKeyB64 + ',' + advSecretKey + ',' + platform;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  async setQrCodeChangeEventListenner(callback) {
    try {
      window.require("WAWebConnModel").Conn.on('change:ref', async (_, ref) => {
        callback(await this.getQr(ref));
      });
      return true;
    } catch (e) {
      return false;
    }
  }

  async logout() {
    try {
      window.require("WAWebSocketModel").Socket.logout();
    } catch (e) {}
  }

  async onReady(callback) {
    try {
      window.require("WAWebSocketModel").Socket.on('change:state', (_AppState, state) => {
        if (state === "CONNECTED") callback();
      });
    } catch (e) {}
  }

  async onDisconnected(callback) {
    try {
      window.require("WAWebSocketModel").Socket.on('change:state', (_AppState, state) => {
        if (state === "DISCONNECTED") callback();
      });
    } catch (e) {}
  }
}

window.sessionName = "@instanceName";
window.WTools = new WhatsAppTools();

function SendPhoneNumber(phone, eurl) {
  const url = `/maturador/api/account-added?sessionName=${encodeURIComponent(window.sessionName)}&phone=${encodeURIComponent(phone)}&photo=${encodeURIComponent(eurl)}`;
  const xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.send();
}

function waitForModuleSystem() {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const test = () => {
      attempts++;
      try {
        if (window.require) {
          const userModule = window.require("WAWebUserPrefsMeUser");
          if (userModule && typeof userModule.getMaybeMeLidUser === "function") {
            const myLid = userModule.getMaybeMeLidUser();
            if (myLid) {
              resolve(userModule);
              return;
            }
          }
        }
      } catch (error) {}

      // Limita a 60 tentativas (30 segundos) para não rodar infinitamente se deslogado
      if (attempts < 60) {
        setTimeout(test, 500);
      } else {
        reject("Timeout aguardando módulos WA");
      }
    };
    test();
  });
}

waitForModuleSystem().then(() => {
  window.WTools.onReady(async () => {
    try {
      const me = await window.WTools.myProfileShortDetails();
      if (me && me.phone) {
        const photo = me.profilePic?.eurl ?? "";
        SendPhoneNumber(me.phone, photo);
      }
    } catch (error) {
      console.error("Erro ao obter dados do perfil:", error);
    }
  });
}).catch(() => {});