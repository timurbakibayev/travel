function getUsers() {
    var token = localStorage.getItem('token');
    var user = localStorage.getItem('username');
    var url = "http://localhost:8000/users/";

    var xhr = new XMLHttpRequest();
    var resultElement = document.getElementById('users_div');
    var dailyElement = document.getElementById('daily_button');
    var inviteElement = document.getElementById('invite_button');
    dailyElement.innerHTML = "...";
    dailyElement.style.color = "black";
    xhr.open('GET', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.addEventListener('load', function () {
        var data = JSON.parse(this.response);
        console.log(data);
        if (this.status == 401) {
            resultElement.innerHTML = "No credentials provided";
        } else {
            var isAdmin = false;
            var isManager = false;
            var groups = "";
            for (var key = 0, size = data.length; key < size; key++) {
                if (data[key]["username"] == user && data[key]["admin"] == 1)
                    isAdmin = true;
                if (data[key]["username"] == user && data[key]["manager"] == 1)
                    isManager = true;
            }
            var tableHeader = '<table class="table">';
            tableHeader += "<thead><tr><th>Username</th><th>Email</th><th>Roles</th>";
            if (isManager || isAdmin) {
                tableHeader += "<th>Delete</th>";
                tableHeader += "<th>Block</th>";
            }
            if (isAdmin)
                tableHeader += "<th>Manager</th>";
            tableHeader += "<th>Password</th></th></tr></thead>";

            var r = new Array(), j = -1;
            for (var key = 0, size = data.length; key < size; key++) {
                //console.log(data[key]["username"])
                if (data[key]["username"] == user) {
                    r[++j] = '<tr style="background: #ccddff">';
                    dailyElement.innerHTML = "Today consumed: " + data[key]["consumed"] + "/" + data[key]["calories"];
                    dailyElement.style.color = data[key]["consumed"]>=data[key]["calories"]?"red":"green";
                    if (data[key]["admin"])
                        inviteElement.innerHTML = 'Invite (you are an admin)';
                    else
                        inviteElement.innerHTML = "";
                } else
                    r[++j] = '<tr>';
                if (data[key]["username"] == user)
                    r[++j] = '<td>' + data[key]["username"] + " (this is you)</td>";
                else
                    r[++j] = '<td>' + data[key]["username"] + "</td>";
                r[++j] = '<td>' + data[key]["email"] + "</td>";
                r[++j] = '<td>';
                groups = "";
                if (data[key]["admin"] == false && data[key]["manager"] == false)
                    groups = "regular";
                else {
                    if (data[key]["admin"])
                        groups += "Admin";
                    if (data[key]["manager"]) {
                        if (groups != "")
                            groups += ", ";
                        groups += "Manager";
                    }
                }

                r[++j] = groups + "</td>";
                if (isAdmin || isManager) {
                    r[++j] = '<td><a href="#" onclick="deleteUser(' + data[key]["id"] + ", '" + data[key]["username"] + "'" + ')">Delete ✘</a>';
                    r[++j] = '</td>';
                    if (!data[key]["blocked"])
                        r[++j] = '<td><a href="#" onclick="blockUser(' + data[key]["id"] + ', true)">Block</a>';
                    else
                        r[++j] = '<td><a href="#" onclick="blockUser(' + data[key]["id"] + ', false)">Unblock</a>';
                    r[++j] = '</td>';
                }
                if (isAdmin) {
                    r[++j] = "<td>";
                    if (data[key]["manager"] == 1)
                        r[++j] = '<a href = "#" onclick="grantManager(' + data[key]["id"] + ',' + "'" + "un" + "'" + ')">Revoke</a>';
                    else
                        r[++j] = '<a href = "#" onclick="grantManager(' + data[key]["id"] + ',' + "''" + ')">Grant</a>';
                    r[++j] = '</td>';
                }
                r[++j] = "<td>";
                r[++j] = '<a href = "#" onclick="setPassword(' + data[key]["id"] + ',' + ')">Set</a>';
                r[++j] = '</td>';
                r[++j] = '</td>';
                r[++j] = '</tr>';
            }
            resultElement.innerHTML = tableHeader + r.join('') + "</table>";
            window.times -= 1;
        }
    });
    xhr.send(null);
}

function grantManager(id, un) {
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/users/" + id.toString() + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        if (this.status == 200) {
            getUsers();
        } else {
            if (responseObject.detail)
                alert(responseObject.detail);
            else
                alert(responseObject);
            console.log(responseObject);
        }
    });
    var sendObject = JSON.stringify({manager: un=="un"?false:true});
    console.log("sending " + sendObject);
    xhr.send(sendObject);
}

function blockUser(id, block) {
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/users/" + id.toString() + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        if (this.status == 200) {
            getUsers();
        } else {
            if (responseObject.detail)
                alert(responseObject.detail);
            else
                alert(responseObject);
            console.log(responseObject);
        }
    });
    var sendObject = JSON.stringify({blocked: block});
    console.log("sending " + sendObject);
    xhr.send(sendObject);
}

function deleteUser(id, name) {
    if (confirm("Delete " + name + "?")) {
        var token = localStorage.getItem('token');
        var url = "http://localhost:8000/users/" + id.toString() + "/";
        var xhr = new XMLHttpRequest();
        xhr.open('DELETE', url, true);
        xhr.setRequestHeader("Authorization", "JWT " + token);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        xhr.addEventListener('load', function () {
            window.editMealId = "-1";
            var responseObject = {};
            try {
                responseObject = JSON.parse(this.response);
            } catch(e) {
                responseObject = {"detail":this.statusText};
            }

            if (this.status < 400) {
                load_all();
            } else {
                if (responseObject.detail)
                    alert(responseObject.detail);
                else
                    alert(responseObject);
            }
            });
        xhr.send(null);
    }
}

function setPassword(id) {
    $('#editModalForm').modal('hide');
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/users/" + id + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        if (this.status == 200) {
            getUsers();
            alert("Password is successfully set");
        } else {
            if (responseObject.detail)
                alert(responseObject.detail);
            else if (responseObject.password)
                alert(responseObject.password);
            else
                alert(responseObject);
            console.log(responseObject);
        };
        load_all();
    });
    var newPassword = window.prompt("Enter new password", "");
    if (newPassword !== "") {
        var sendObject = JSON.stringify({
            password: newPassword,
        });
        console.log("Sending", sendObject);
        xhr.send(sendObject);
    }
}

function register() {
  var usersUrl = "/users/";
  var xhr = new XMLHttpRequest();
  var userElement = document.getElementById('reg_username');
  var passwordElement = document.getElementById('reg_password');
  var emailElement = document.getElementById('reg_email');
  var user = userElement.value;
  var password = passwordElement.value;
  var email = emailElement.value;
  var resultError = document.getElementById('register-error-div');
  var resultSuccess = document.getElementById('register-success-div');
  resultError.innerHTML = "";
  resultSuccess.innerHTML = "Please, wait...";

  xhr.open('POST', usersUrl, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.addEventListener('load', function() {
    var responseObject = JSON.parse(this.response);
    console.log(responseObject);
      if (this.status == 201) {
          resultSuccess.innerHTML = "Nice! You are in! Now please verify your email!";
      } else
          resultSuccess.innerHTML = "";
          if (responseObject.detail)
              resultError.innerHTML = responseObject.detail;
          else {
              resultError.innerHTML = "";
              for (var k in responseObject){
                    if (responseObject.hasOwnProperty(k)) {
                         console.log(k + ": " + responseObject[k]);
                         resultError.innerHTML += k + ": " + responseObject[k] + "<br>";
                    }
                }
          }
  });

  var sendObject = JSON.stringify({username: user, password: password, email: email});

  console.log('going to send', sendObject);

  xhr.send(sendObject);
}