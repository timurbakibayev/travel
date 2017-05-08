function newTrip() {
  var token=localStorage.getItem('token');
  var url = "http://localhost:8000/trips/";
  var xhr = new XMLHttpRequest();
  var destinationElement = document.getElementById('new_destination');
  var startDateElement = document.getElementById('new_start_date');
  var endDateElement = document.getElementById('new_end_date');
  var commentElement = document.getElementById('new_comment');
  xhr.open('POST', url, true);
  xhr.setRequestHeader("Authorization", "JWT " + token);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.addEventListener('load', function() {
    var data = JSON.parse(this.response);
    console.log(data);
    if (this.status == 201) {
        window.editTripId = data["id"];
        window.times = 3;
        load_all();
        document.getElementById('form_new_trip').reset();
    } else {
        alert("Please, fill in all trip details. Only comments are not required.")
    }
  });
  var sendObject = JSON.stringify({destination: destinationElement.value,
                                    start_date: startDateElement.value,
                                    end_date: endDateElement.value,
                                    comment: commentElement.value});
  console.log("Sending",sendObject);
  xhr.send(sendObject);
}

function deleteTrip(id, destination){
  if (confirm("Delete " + destination + "?")) {
      var token = localStorage.getItem('token');
      var url = "http://localhost:8000/trips/" + id.toString() + "/"
      var xhr = new XMLHttpRequest();
      var destinationElement = document.getElementById('new_destination');
      var startDateElement = document.getElementById('new_start_date');
      var endDateElement = document.getElementById('new_end_date');
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

function editTrip(id){
  var token=localStorage.getItem('token');
  var url = "http://localhost:8000/trips/"+id.toString()+"/";
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.setRequestHeader("Authorization", "JWT " + token);
  xhr.addEventListener('load', function() {
    var data = JSON.parse(this.response);
    console.log(data);
    console.log(this.status);
    openEditForm(data);
  });
  xhr.send(null);
}

function openEditForm(data) {
    var token=localStorage.getItem('token');
    var url = "http://localhost:8000/trips/"
    var xhr = new XMLHttpRequest();
    var modalHeader = document.getElementById('edit_modal_header');
    modalHeader.innerHTML = "Edit " + data["destination"];
    window.editTripId = data["id"];
    $('#edit_destination').val(data["destination"]);
    $('#edit_start_date').val(data["start_date"]);
    $('#edit_end_date').val(data["end_date"]);
    $('#edit_comment').val(data["comment"]);
    $('#editModalForm').modal('show');
}

function saveChanges() {
    var tripId = window.editTripId.toString();
    $('#editModalForm').modal('hide');
    var editDestionation = $('#edit_destination').val();
    var editComment = $('#edit_comment').val();
    var editStartDate = $('#edit_start_date').val();
    var editEndDate = $('#edit_end_date').val();

      var token=localStorage.getItem('token');
      var url = "http://localhost:8000/trips/"+tripId+"/";
      var xhr = new XMLHttpRequest();
      xhr.open('PUT', url, true);
      xhr.setRequestHeader("Authorization", "JWT " + token);
      xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
      xhr.addEventListener('load', function() {
          load_all();
      });
      var sendObject = JSON.stringify({destination: editDestionation,
                                        start_date: editStartDate,
                                        end_date: editEndDate,
                                        comment: editComment});
      console.log("Sending",sendObject);
      xhr.send(sendObject);
}

function getNextMonth() {
      var token=localStorage.getItem('token');
      var url = "http://localhost:8000/travel_plan/";
      var xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.setRequestHeader("Authorization", "JWT " + token);
      xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
      xhr.addEventListener('load', function() {
          var data = JSON.parse(this.response);
            console.log(data);
            console.log(this.status);
            alert(data);
      });
      xhr.send(null);
}


function getTrips() {
    var token=localStorage.getItem('token');
  var user=localStorage.getItem('username');
  var url = "http://localhost:8000/trips/";
  var filter = "";
  var searchFilter = $('#filter_text').val();
  if (searchFilter != "") {
      filter = "?search=" + searchFilter;
  }
  var fromFilter = $('#filter_from').val();
  if (fromFilter != "") {
      if (filter!="")
          filter+="&";
      else
          filter="?";
      filter += "from=" + fromFilter;
  }
  var toFilter = $('#filter_to').val();
  if (toFilter != "") {
      if (filter!="")
          filter+="&";
      else
          filter="?";
      filter += "till=" + toFilter;
  }
  url += filter;
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
        tableHeader += "<th>Days Left</th>";
        tableHeader += "<th>Edit</th></tr></thead>";

        var r = new Array(), j = -1;
        for (var key = 0, size = data.length; key < size; key++) {
            console.log(data[key]["destination"])
            if (data[key]["id"] == window.editTripId)
                r[++j] = '<tr class="changed">';
            else
                r[++j] = '<tr>';
            r[++j] = '<td>' + data[key]["destination"].replace(/<(?:.|\n)*?>/gm, '') + "</td>";
            r[++j] = '<td>' + data[key]["start_date"] + "</td>";
            r[++j] = '<td>' + data[key]["end_date"] + "</td>";
            r[++j] = '<td>' + (data[key]["comment"] == null ? "" : data[key]["comment"].replace(/<(?:.|\n)*?>/gm, '')) + "</td>";
            r[++j] = '<td>' + (data[key]["days_left"] == 0? "" : data[key]["days_left"]) + "</td>";
            r[++j] = '<td><a href="#" onclick="editTrip(' + data[key]["id"] + ')">Edit 🖉</a> '+
                ' <a href="#" onclick="deleteTrip(' + data[key]["id"] + ", '" + data[key]["destination"]+ "'" + ')">Delete ✘</a> </td>';
            r[++j] = '</tr>';
        }
        resultElement.innerHTML = tableHeader + r.join('') + "</table>";
        window.times -= 1;
        // if (window.times <= 0)
        //     window.editTripId = "-1";
    }
  });
  xhr.send(null);
}
