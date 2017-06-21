function newMeal() {
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/meals/";
    var xhr = new XMLHttpRequest();
    var textElement = document.getElementById('new_text');
    var dateElement = document.getElementById('new_date');
    var timeElement = document.getElementById('new_time');
    var caloriesElement = document.getElementById('new_calories');
    var newObjectErrorsElement = document.getElementById('new_errors');
    newObjectErrorsElement.innerHTML = "";
    if (textElement.value == "") {
        newObjectErrorsElement.innerHTML = "Fill in the meal first";
        console.log("Meal is not defined");
        return;
    }
    console.log("Initiating new meal");
    xhr.open('POST', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        console.log(responseObject);
        if (this.status == 201) {
            window.editMealId = responseObject["id"];
            window.times = 3;
            load_all();
            document.getElementById('form_new_meal').reset();
        } else {
            var errors = "";
            for (var k in responseObject) {
                if (responseObject.hasOwnProperty(k)) {
                    if (errors != "")
                        errors += ", ";
                    console.log(k + ": " + responseObject[k]);
                    errors += k + ": " + responseObject[k];
                }
            }
            if (errors == "")
                errors = "Something wrong just happened";
            newObjectErrorsElement.innerHTML = errors;
        }
    });
    var sendObject = JSON.stringify({
        text: textElement.value,
        date: dateElement.value,
        time: timeElement.value,
        calories: caloriesElement.value
    });
    console.log("Sending", sendObject);
    xhr.send(sendObject);
}

function deleteMeal(id, destination) {
    if (confirm("Delete " + destination + "?")) {
        var token = localStorage.getItem('token');
        var url = "http://localhost:8000/meals/" + id.toString() + "/"
        var xhr = new XMLHttpRequest();
        xhr.open('DELETE', url, true);
        xhr.setRequestHeader("Authorization", "JWT " + token);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        xhr.addEventListener('load', function () {
            window.editMealId = "-1";
            load_all();
        });
        xhr.send(null);
    }
}

function editMeal(id) {
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/meals/" + id.toString() + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.addEventListener('load', function () {
        var data = JSON.parse(this.response);
        console.log(data);
        console.log(this.status);
        openEditForm(data);
    });
    xhr.send(null);
}

function openEditForm(data) {
    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/meals/"
    var xhr = new XMLHttpRequest();
    var modalHeader = document.getElementById('edit_modal_header');
    modalHeader.innerHTML = "Edit '" + data["text"] + "'";
    window.editMealId = data["id"];
    $('#edit_text').val(data["text"]);
    $('#edit_date').val(data["date"]);
    $('#edit_time').val(data["time"]);
    $('#edit_calories').val(data["calories"]);
    $('#editModalForm').modal('show');
}

function saveChanges() {
    var mealId = window.editMealId.toString();
    $('#editModalForm').modal('hide');
    var editText = $('#edit_text').val();
    var editDate = $('#edit_date').val();
    var editTime = $('#edit_time').val();
    var editCalories = $('#edit_calories').val();

    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/meals/" + mealId + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        console.log(responseObject);
        if (this.status < 300) {
            load_all();
        } else {
            var errors = "";
            if (responseObject.detail)
                errors = responseObject.detail;
            else {
                for (var k in responseObject) {
                    if (responseObject.hasOwnProperty(k)) {
                        console.log(k + ": " + responseObject[k]);
                        errors += k + ": " + responseObject[k] + "\n";
                    }
                }
                if (errors == "")
                    errors = "Something wrong just happened";
                alert(errors);
            }
        }
    });
    var sendObject = JSON.stringify({
        text: editText,
        date: editDate,
        time: editTime,
        calories: editCalories
    });
    console.log("Sending", sendObject);
    xhr.send(sendObject);
}

function saveUserSettings() {
    $('#myModalDaily').modal('hide');
    var settingsCalories = parseInt($('#settings_calories').val());
    var settingsPassword = $('#settings_password').val();

    var token = localStorage.getItem('token');
    var url = "http://localhost:8000/users/" + localStorage.getItem("user_id") + "/";
    var xhr = new XMLHttpRequest();
    xhr.open('PUT', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.addEventListener('load', function () {
        var responseObject = JSON.parse(this.response);
        console.log(responseObject);
        if (this.status < 300) {
            load_all();
        } else {
            var errors = "";
            if (responseObject.detail)
                errors = responseObject.detail;
            else {
                for (var k in responseObject) {
                    if (responseObject.hasOwnProperty(k)) {
                        console.log(k + ": " + responseObject[k]);
                        errors += k + ": " + responseObject[k] + "\n";
                    }
                }
                if (errors == "")
                    errors = "Something wrong just happened";
                alert(errors);
            }
        }
    });
    var sendObject = JSON.stringify({
        calories: settingsCalories,
        password: settingsPassword
    });
    if (settingsPassword === "")
        sendObject = JSON.stringify({
            calories: settingsCalories
        });
    console.log(settingsPassword);
    console.log("URL", url);
    console.log("Sending", sendObject);
    xhr.send(sendObject);
}


function getMeals() {
    var token = localStorage.getItem('token');
    var user = localStorage.getItem('username');
    var url = "http://localhost:8000/meals/";
    var filter = "";
    var searchFilter = $('#filter_text').val();
    if (searchFilter != "") {
        filter = "?search=" + searchFilter;
    }
    var fromFilter = $('#filter_date_from').val();
    if (fromFilter != "") {
        if (filter != "")
            filter += "&";
        else
            filter = "?";
        filter += "date_from=" + fromFilter;
    }
    var toFilter = $('#filter_date_to').val();
    if (toFilter != "") {
        if (filter != "")
            filter += "&";
        else
            filter = "?";
        filter += "date_to=" + toFilter;
    }
    fromFilter = $('#filter_time_from').val();
    if (fromFilter != "") {
        if (filter != "")
            filter += "&";
        else
            filter = "?";
        filter += "time_from=" + fromFilter;
    }
    toFilter = $('#filter_time_to').val();
    if (toFilter != "") {
        if (filter != "")
            filter += "&";
        else
            filter = "?";
        filter += "time_to=" + toFilter;
    }
    url += filter;
    console.log("Querying " + url);
    var xhr = new XMLHttpRequest();
    var resultElement = document.getElementById('result');
    xhr.open('GET', url, true);
    xhr.setRequestHeader("Authorization", "JWT " + token);
    xhr.addEventListener('load', function () {
        var data = JSON.parse(this.response);
        console.log(data);
        if (this.status == 401) {
            document.getElementById("login_button").style.visibility = "visible";
            document.getElementById("logout_button").style.visibility = "hidden";
            resultElement.innerHTML = "No credentials provided";
        } else {
            document.getElementById("login_button").style.visibility = "hidden";
            document.getElementById("logout_button").style.visibility = "visible";
            document.getElementById("logout_button").textContent = "Logout " + user;

            var tableHeader = '<table class="table">';
            tableHeader += "<thead><tr><th>Meal</th><th>Date</th><th>Time</th>";
            tableHeader += "<th>Calories</th>";
            tableHeader += "<th>Edit</th></tr></thead>";

            var r = new Array(), j = -1;
            var c = 0;
            for (var key = 0, size = data.length; key < size; key++) {
                console.log(data[key]["text"])
                if (data[key]["id"] == window.editMealId)
                    r[++j] = '<tr class="changed">';
                else
                    r[++j] = '<tr>';
                r[++j] = '<td>' + data[key]["text"].replace(/<(?:.|\n)*?>/gm, '') + "</td>";
                r[++j] = '<td>' + data[key]["date"] + "</td>";
                r[++j] = '<td>' + data[key]["time"].substring(0,5) + "</td>";
                r[++j] = '<td>' + data[key]["calories"] + "</td>";
                c += data[key]["calories"];
                r[++j] = '<td><a href="#" onclick="editMeal(' + data[key]["id"] + ')">Edit 🖉</a> ' +
                    ' <a href="#" onclick="deleteMeal(' + data[key]["id"] + ", '" + data[key]["text"] + "'" + ')">Delete ✘</a> </td>';
                r[++j] = '</tr>';
            }
            r[++j] = '<tr><td>Total</td> <td> </td> <td></td> <td>'+c+'</td></tr>';
            resultElement.innerHTML = tableHeader + r.join('') + "</table>";
            window.times -= 1;
            // if (window.times <= 0)
            //     window.editMealId = "-1";
        }
    });
    xhr.send(null);
}
