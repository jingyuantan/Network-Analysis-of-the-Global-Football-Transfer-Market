$(document).ready(function () {
  $('#main_table').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "name"},
                {"data": "transfer_in"},
                {"data": "transfer_out"},
                {"data": "total_transfer"},
                {"data": "spent"},
                {"data": "received"},
                {"data": "net"}
                ]
  });
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
});

function generateGraph() {
  //document.getElementById("loader").style.display = "block";
  $(".overlay").show();
    $.ajax({
        url: "/explore_league_filter",
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
        success: function (data) {
            console.log(data)
            Plotly.react('bargraph', data[0]);
            $('#main_table').DataTable().clear().rows.add(data[1].data).draw();
            $(".overlay").hide();
            //document.getElementById("loader").style.display = "none";
        }
    });
}

var myPlot = document.getElementById('bargraph')
myPlot.on('plotly_click', function(eventData){
    var clicked = ''
    for(var i=0; i < eventData.points.length; i++){
        clicked = eventData.points[i].text
    };
    //document.getElementById("loader").style.display = "block";
    $(".overlay").show();
    $.ajax({
        url: "/league_one",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'clicked': clicked,
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
        success: function (data) {
            Plotly.react('bargraph', data[0]);
            $('#main_table').DataTable().clear().rows.add(data[1].data).draw();
            $(".overlay").hide();
        }
    });
    console.log('out')
});