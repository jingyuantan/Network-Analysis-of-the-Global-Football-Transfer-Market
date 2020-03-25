$(document).ready(function () {
  $('#centrality').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "name"},
                {"data": "deg"},
                {"data": "bet"},
                {"data": "clo"},
                {"data": "eig"},
                ]
  });
  $('.dataTables_length').addClass('bs-select');
  document.getElementById("title").innerHTML = 'Centrality Table (Filter by League: English Premier League)';
});

function change_tables() {
    $(".overlay").show();
  //document.getElementById("loader").style.display = "block";
    $.ajax({
        url: "/re_statistics",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'season': document.getElementById('season').value,
            'league': document.getElementById('league').value,
            'country': document.getElementById('country').value,
            'position': document.getElementById('position').value,
            'nationality': document.getElementById('nationality').value,
            'level': document.getElementById('level').value,
            'valueFrom': document.getElementById("valueFrom").value,
            'valueTo': document.getElementById("valueTo").value,
            'ageFrom': document.getElementById("ageFrom").value,
            'ageTo': document.getElementById("ageTo").value,
            'dateFrom': document.getElementById("dateFrom").value,
            'dateTo': document.getElementById("dateTo").value
        },
        dataType:"json",
        success: function (data) {
            $('#centrality').DataTable().clear().rows.add(data[0].data).draw();
            document.getElementById("title").innerHTML = 'Centrality Table (Based on user input)';
            document.getElementById("denom").innerHTML = 'Number of connections in the network: ' + data[2];
            document.getElementById("numer").innerHTML = 'Number of two way connections in the network: ' + data[1];
            document.getElementById("reciprocity").innerHTML = 'Reciprocity of the network: ' + data[3];
            $(".overlay").hide();
        }
    });
}