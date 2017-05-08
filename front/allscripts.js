var editTripId;
var times = 0;

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
	  load_all();
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
	  load_all();
    } else {
      resultElement.innerHTML = "No token received";
    }
  });

  var sendObject = JSON.stringify({username: user, password: password});

  console.log('going to login from register', sendObject);

  xhr.send(sendObject);
}



function logout() {
    localStorage.setItem('token', "");
    load_all();
}

function load_all() {
  getTrips();
  getUsers();
}

function onLoad() {
            $('#login-form-link').click(function(e) {
                $("#login-form").delay(100).fadeIn(100);
                $("#register-form").fadeOut(100);
                $('#register-form-link').removeClass('active');
                $(this).addClass('active');
                e.preventDefault();
            });
            $('#register-form-link').click(function(e) {
                $("#register-form").delay(100).fadeIn(100);
                $("#login-form").fadeOut(100);
                $('#login-form-link').removeClass('active');
                $(this).addClass('active');
                e.preventDefault();
            });
            load_all();
            $(document).on('hidden.bs.modal', function (e) {
                load_all();
            });
            $("#login-form").submit(function(event) {
                loginFromModal(event);
                event.preventDefault();
            });
            $("#register-form").submit(function(event) {
                registerFromModal(event);
                event.preventDefault();
            });
            $("#form_new_trip").submit(function(event) {
                newTrip(event);
                event.preventDefault();
            });
            $("#edit_trip_form").submit(function(event) {
                saveChanges();
                event.preventDefault();
            });
            $("#filter_form").submit(function(event) {
                load_all();
                event.preventDefault();
            });
        }
        function loginFromModal(e) {
            getToken();
            $('#myModal').modal('hide');
        }
        function registerFromModal(e) {
            register();
        }
        
