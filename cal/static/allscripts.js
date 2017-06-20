var editMealId;
var times = 0;

function getToken() {
    var loginUrl = "http://localhost:8000/auth-web/"
    var xhr = new XMLHttpRequest();
    var userElement = document.getElementById('username');
    var passwordElement = document.getElementById('password');
    var resultElement = document.getElementById('result');
    var errorElement = document.getElementById('login-error-div');
    var user = userElement.value;
    var password = passwordElement.value;
    errorElement.innerHTML = "";
    var response = grecaptcha.getResponse();
    grecaptcha.reset();
    // if(response.length > 0)
    //     alert(response);
    // else
    //     alert("Not verified");
    xhr.open('POST', loginUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        console.log(responseObject);
        if (responseObject.token) {
            localStorage.setItem('token', responseObject.token);
            localStorage.setItem('username', user);
            load_all();
            $('#myModal').modal('hide');
            return (true);
        } else {
            if (responseObject.non_field_errors) {
                errorElement.innerHTML = responseObject.non_field_errors;
                if (responseObject.non_field_errors.toString().indexOf("not verified") > 0)
                    errorElement.innerHTML = responseObject.non_field_errors + "<br><a href='#' onclick='send_verification_code(" + '"' + user + '"' + ")'>Send verification code</a>";
            }

            return (false);
        }
    });

    var sendObject = JSON.stringify({username: user, password: password, captcha: response});

    console.log('going to send', sendObject);

    xhr.send(sendObject);
}

function send_verification_code(username) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', "/users/" + username + "/send_verification_code", true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        alert(responseObject.detail);
    });

    var sendObject = JSON.stringify({username: username});

    //console.log('going to send', sendObject);

    xhr.send(sendObject);
}

function logout() {
    localStorage.setItem('token', "");
    load_all();
}

function load_all() {
    getMeals();
    getUsers();
}
function onLoad() {
    $('#login-form-link').click(function (e) {
        $("#login-form").delay(100).fadeIn(100);
        $("#register-form").fadeOut(100);
        $('#register-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });
    $('#register-form-link').click(function (e) {
        $("#register-form").delay(100).fadeIn(100);
        $("#login-form").fadeOut(100);
        $('#login-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });
    $('#daily_button').click(function (e) {
        $('#myModalDaily').modal('show');
        $('#settings_calories').val('0');
        var token = localStorage.getItem('token');
        var user = localStorage.getItem('username');
        var url = "http://localhost:8000/users/";
        var xhr = new XMLHttpRequest();
        var resultElement = document.getElementById('users_div');
        var dailyElement = document.getElementById('daily_button');
        dailyElement.innerHTML = "Loading...";
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
                var calories = 0;
                var groups = "";
                for (var key = 0, size = data.length; key < size; key++) {
                    if (data[key]["username"] == user) {
                        calories = data[key]["calories"];
                        localStorage.setItem('user_id', data[key]["id"]);
                    }
                }
                $('#settings_calories').val(calories);
                $('#settings_username').text(user);
            }
        });
        xhr.send(null);
    });

    $('#invite_button').click(function (e) {
        $('#inviteModalForm').modal('show');
    });

    $("#invite_form").submit(function (event) {
        event.preventDefault();
        $('#inviteModalForm').modal('hide');
        var token = localStorage.getItem('token');
        var user = localStorage.getItem('username');
        var url = "http://localhost:8000/invitations/";
        var xhr = new XMLHttpRequest();
        var email = $('#invite_email').val();
        xhr.open('POST', url, true);
        xhr.setRequestHeader("Authorization", "JWT " + token);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        xhr.addEventListener('load', function () {
            try {
                var responseObject = JSON.parse(this.response);
                console.log(responseObject);
                if (this.status == 201) {
                    alert("The user is successfully invited!");
                }
                if (responseObject.detail)
                    alert(responseObject.detail);
                else {
                    errors = "";
                    for (var k in responseObject) {
                        if (responseObject.hasOwnProperty(k)) {
                            console.log(k + ": " + responseObject[k]);
                            errors += k + ": " + responseObject[k] + "\n";
                        }
                    }
                    alert("errors:\n" + errors);
                }
            } catch (e) {alert(e)};
        });

        var sendObject = JSON.stringify({email: email});

        console.log('going to send', sendObject);

        xhr.send(sendObject);
    });

    $("#user-settings-form").submit(function (event) {
        event.preventDefault();
        saveUserSettings();
    });
    load_all();
    $(document).on('hidden.bs.modal', function (e) {
        load_all();
    });
    $("#login-form").submit(function (event) {
        loginFromModal(event);
        event.preventDefault();
    });
    $("#register-form").submit(function (event) {
        registerFromModal(event);
        event.preventDefault();
    });
    $("#form_new_meal").submit(function (event) {
        newMeal(event);
        event.preventDefault();
    });
    $("#edit_meal_form").submit(function (event) {
        saveChanges();
        event.preventDefault();
    });
    $("#filter_form").submit(function (event) {
        load_all();
        event.preventDefault();
    });
}
function loginFromModal(e) {
    if (getToken() == true)
        $('#myModal').modal('hide');
}
function registerFromModal(e) {
    register();
    event.preventDefault();
}

