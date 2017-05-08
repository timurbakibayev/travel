function getUsers() {
    var token = localStorage.getItem('token');
    var user = localStorage.getItem('username');
    var url = "http://localhost:8000/users/";

    var xhr = new XMLHttpRequest();
    var resultElement = document.getElementById('users_div');
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
            for (var key = 0, size = data.length; key < size; key++) {
                var groups = ""
                if (typeof data[key]["gr"] !== 'undefined') {
                    for (var i = 0; i < data[key]["gr"].length; i++)
                        groups += data[key]["gr"][i]["name"] + (i < data[key]["gr"].length - 1 ? "," : "");
                }
                if (data[key]["username"] == user && groups.includes("admin"))
                    isAdmin = true;
                if (data[key]["username"] == user && groups.includes("manager"))
                    isManager = true;

            }
            var tableHeader = '<table class="table">';
            tableHeader += "<thead><tr><th>Username</th><th>Roles</th>";
            if (isManager || isAdmin)
                tableHeader += "<th>Delete</th>";
            if (isAdmin)
                tableHeader += "<th>Manager</th>";
            tableHeader += "<th>Password</th></th></tr></thead>";


            var r = new Array(), j = -1;
            for (var key = 0, size = data.length; key < size; key++) {
                //console.log(data[key]["username"])
                if (data[key]["username"] == user)
                    r[++j] = '<tr style="background: #99bbff">';
                else
                    r[++j] = '<tr>';
                r[++j] = '<td>' + data[key]["username"] + "</td>";
                r[++j] = '<td>';
                var groups = "";
                if (typeof data[key]["gr"] !== 'undefined') {
                    for (var i = 0; i < data[key]["gr"].length; i++)
                        groups += data[key]["gr"][i]["name"] + (i < data[key]["gr"].length - 1 ? "," : "");
                }
                if (groups == "")
                    groups = "regular";
                r[++j] = groups + "</td>";
                if (isAdmin || isManager) {
                    r[++j] = '<td><a href="#" onclick="deleteUser(' + data[key]["id"] + ", '" + data[key]["username"] + "'" + ')">Delete ✘</a>';
                    r[++j] = '</td>';
                }
                if (isAdmin) {
                    r[++j] = "<td>";
                    if (groups.includes("manager"))
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
    var url = "http://localhost:8000/" + un + "grant_manager/" + id.toString() + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.addEventListener('load', function () {
        if (this.status == 200) {
            getUsers();
        }
    });
    xhr.send(null);
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
            window.editTripId = "-1";
            load_all();
        });
        xhr.send(null);
    }
}

function setPassword(id) {
    $('#editModalForm').modal('hide');
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/set_password/" + id + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
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
  var registerUrl = "http://localhost:8000/register/"
  var xhr = new XMLHttpRequest();
  var userElement = document.getElementById('reg_username');
  var passwordElement = document.getElementById('reg_password');
  var user = userElement.value;
  var password = passwordElement.value;

  xhr.open('POST', registerUrl, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.addEventListener('load', function() {
    //var responseObject = JSON.parse(this.response);
    //console.log(responseObject);
      if (this.status == 201) {
          getToken1(user, password);
          $('#myModal').modal('hide');
      } else
          alert("Something went wrong, please, try again");
  });

  var sendObject = JSON.stringify({username: user, password: password});

  console.log('going to send', sendObject);

  xhr.send(sendObject);
}