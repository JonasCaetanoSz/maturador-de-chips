    // se conecta com o servidor web socket

    var socket;
    function ConnectWebSocketServer() {
      socket = new WebSocket('ws://localhost:5026');
      socket.onopen = function (event) {
        $.notify("conexão websocket estabelecida", "success");
      };

      // nova atualização recebida do servidor

      socket.onmessage = function (event) {

        var data = JSON.parse(event.data);
        var SendOf = data.enviadoDe;
        var ReceivedBy = data.recebidoPor;
        var message = data.mensagem;
        var hours = data.horario; //new Date().toLocaleDateString();

        // criar uma nova linha na tabela de log

        var newRow = $("<tr>");
        var cols = "";
        cols += "<td>" + SendOf + "</td>";
        cols += "<td>" + ReceivedBy + "</td>";
        cols += "<td class='messageTd'>" + `<input value="${message}" class="messageInput" </input>` + "</td>";
        cols += "<td>" + hours + "</td>";
        newRow.append(cols);
        $("#logTableBody").append(newRow);

        // faz o scroll automatico na tabela de logs

        var logTableContainer = document.getElementsByClassName("log-table-container")[0];
        logTableContainer.scrollTop = logTableContainer.scrollHeight;
      };

      // por algum motivo a conexão websocket não foi realizada (o motivo principal é que ele ainda esta iniciando)

      socket.onerror = function (error) {
        //$.notify("erro ao me conectar no servidor webscoket", "error");
        ConnectWebSocketServer()
      };

      // conexao com o servidor foi fechada

      socket.onclose = function () {
        $.notify("a conexão com o servidor websocket foi fechada, agora não é mais possivel atualizar o log.", "error");
      };
    }

    // chama a função que inicia o servidor websocket, além de liberar o botão parar maturação

    function StartLog() {
      ConnectWebSocketServer();
      $("#stopButton").prop("disabled", false);
    }

    // parar maturação

    function StopMaturation() {
      $("#stopButton").prop("disabled", true);
      if (socket) {
        socket.close();
      }

      let xhr = new XMLHttpRequest()
      xhr.open("GET", "/api/stop-maturation", true)
      xhr.send()

    }

    $("#stopButton").click(StopMaturation);
    $(document).ready(StartLog);
