function getToken() {
  var loginUrl = "http://localhost:8000/auth/"
  var xhr = new XMLHttpRequest();
  var userElement = document.getElementById('username');
  var passwordElement = document.getElementById('password');
  var tokenElement = document.getElementById('token');
  var user = userElement.value;
  var password = passwordElement.value;

  xhr.open('POST', loginUrl, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.addEventListener('load', function() {
    var responseObject = JSON.parse(this.response);
    console.log(responseObject);
    if (responseObject.token) {
      tokenElement.innerHTML = responseObject.token;
	  localStorage.setItem('token', responseObject.token);
    } else {
      tokenElement.innerHTML = "No token received";
    }
  });

  var sendObject = JSON.stringify({username: user, password: password});

  console.log('going to send', sendObject);

  xhr.send(sendObject);
}

function getTrips() {
  token=localStorage.getItem('token');
  var url = "http://localhost:8000/trips/"
  var xhr = new XMLHttpRequest();
  var resultElement = document.getElementById('result');
  xhr.open('GET', url, true);
  xhr.setRequestHeader("Authorization", "JWT " + token);
  xhr.addEventListener('load', function() {
    var data = JSON.parse(this.response);
    console.log(data);
	
	var tableHeader = '<table class="table">';
	tableHeader += ""
	
	var r = new Array(), j = -1;
	 for (var key=0, size=data.length; key<size; key++){
		 console.log(data[key]["destination"])
		 r[++j] ='<tr><td>';	
		 r[++j] = data[key]["id"];
		 r[++j] = '</td><td class="whatever1">';
		 r[++j] = data[key]["destination"];
		 r[++j] = '</td><td class="whatever1">';
		 r[++j] = data[key]["start_date"];
		 r[++j] = '</td><td class="whatever2">';
		 r[++j] = data[key]["end_date"];
		 r[++j] = '</td></tr>';
	 }	
    resultElement.innerHTML = tableHeader + r.join('')+"</table>";
  });

  xhr.send(null);
}