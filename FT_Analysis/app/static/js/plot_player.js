$(document).ready(function () {
  $('#main_table').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "player_nationality"},
                {"data": "destination"},
                {"data": "total_transfer"}
                ]
  });
  $('.dataTables_length').addClass('bs-select');
  document.getElementById("title").innerHTML = 'Network by Players (Filter by Nationality: Brazil)';
});

function generateGraph() {
  $(".overlay").show();
    $.ajax({
        url: "/explore_player_filter",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'season': document.getElementById('season').value,
            'country': document.getElementById('country').value,
            'position': document.getElementById('position').value,
            'nationality': document.getElementById('nationality').value,
            'ageFrom': document.getElementById("ageFrom").value,
            'ageTo': document.getElementById("ageTo").value,
            'valueFrom': document.getElementById("valueFrom").value,
            'valueTo': document.getElementById("valueTo").value,
            'dateFrom': document.getElementById("dateFrom").value,
            'dateTo': document.getElementById("dateTo").value
        },
        dataType:"json",
        success: function (data){
            Plotly.react('bargraph', data[0]);
            $('#main_table').DataTable().clear().rows.add(data[1].data).draw();
            document.getElementById("title").innerHTML = 'Network by Players (Based on user input)';
            $(".overlay").hide();
        }
    });
}