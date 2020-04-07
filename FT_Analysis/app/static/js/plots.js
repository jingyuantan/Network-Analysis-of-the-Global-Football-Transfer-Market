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
  $('.dataTables_length').addClass('bs-select');
  document.getElementById("title").innerHTML = 'Network by Clubs (Filter by League: English Premier League)';
});

function generateGraph() {
  //document.getElementById("loader").style.display = "block";
  $(".overlay").show();
    $.ajax({
        url: "/explore_filter_1",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'season': document.getElementById('season').value,
            'league': document.getElementById('league').value,
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
            document.getElementById("title").innerHTML = 'Network by Clubs (Based on user input)';
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
        url: "/one",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'clicked': clicked,
            'season': document.getElementById('season').value,
            'league': document.getElementById('league').value,
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
            document.getElementById("title").innerHTML = 'Network by Clubs (Ego Network)';
            $(".overlay").hide();
        }
    })
    console.log('out')
});
