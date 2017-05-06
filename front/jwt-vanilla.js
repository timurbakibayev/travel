function getToken() {
  var loginUrl = "http://localhost:8000/auth/"
  var xhr = new XMLHttpRequest();
  var userElement = document.getElementById('username');
  var passwordElement = document.getElementById('password');
  var resultElement = document.getElementById('result');
  var user = userElement.value;
  var password = passwordElement.value;

  xhr.open('POST', loginUrl, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.addEventListener('load', function() {
    var responseObject = JSON.parse(this.response);
    console.log(responseObject);
    if (responseObject.token) {
	  localStorage.setItem('token', responseObject.token);
	  localStorage.setItem('username', user);
	  getTrips();
    } else {
      resultElement.innerHTML = "No token received";
    }
  });

  var sendObject = JSON.stringify({username: user, password: password});

  console.log('going to send', sendObject);

  xhr.send(sendObject);
}

function getToken1(user, password) {
  var loginUrl = "http://localhost:8000/auth/";
  var xhr = new XMLHttpRequest();
  var resultElement = document.getElementById('result');

  xhr.open('POST', loginUrl, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.addEventListener('load', function() {
    var responseObject = JSON.parse(this.response);
    console.log(responseObject);
    if (responseObject.token) {
	  localStorage.setItem('token', responseObject.token);
	  localStorage.setItem('username', user);
	  getTrips();
    } else {
      resultElement.innerHTML = "No token received";
    }
  });

  var sendObject = JSON.stringify({username: user, password: password});

  console.log('going to login from register', sendObject);

  xhr.send(sendObject);
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

function logout() {
    localStorage.setItem('token', "");
    getTrips();
}

function getTrips() {
  var token=localStorage.getItem('token');
  var user=localStorage.getItem('username');
  var url = "http://localhost:8000/trips/"
  var xhr = new XMLHttpRequest();
  var resultElement = document.getElementById('result');
  xhr.open('GET', url, true);
  xhr.setRequestHeader("Authorization", "JWT " + token);
  xhr.addEventListener('load', function() {
    var data = JSON.parse(this.response);
    console.log(data);
    if (this.status == 401) {
        document.getElementById ( "login_button" ).style.visibility = "visible";
        document.getElementById ( "logout_button" ).style.visibility = "hidden";
        resultElement.innerHTML = "No credentials provided";
    } else {
        document.getElementById ( "login_button" ).style.visibility = "hidden";
        document.getElementById ( "logout_button" ).style.visibility = "visible";
        document.getElementById ( "logout_button" ).textContent = "Logout "+user;

        var tableHeader = '<table class="table">';
        tableHeader += "<thead><tr><th>Destination</th><th>Start Date</th><th>End Date</th>";
        tableHeader += "<th>Comment</th>";
        tableHeader += "<th>Edit</th></tr></thead>";

        var r = new Array(), j = -1;
        for (var key = 0, size = data.length; key < size; key++) {
            console.log(data[key]["destination"])
            r[++j] = '<tr>';
            r[++j] = '<td>' + data[key]["destination"] + "</td>";
            r[++j] = '<td>' + data[key]["start_date"] + "</td>";
            r[++j] = '<td>' + data[key]["end_date"] + "</td>";
            r[++j] = '<td>' + (data[key]["comment"] == null ? "" : data[key]["comment"]) + "</td>";
            r[++j] = '<td><a href = "#">Edit✎</a>  <a href="#">Delete✘</a> </td>';
            r[++j] = '</tr>';
        }
        resultElement.innerHTML = tableHeader + r.join('') + "</table>";
    }
  });
  xhr.send(null);
}