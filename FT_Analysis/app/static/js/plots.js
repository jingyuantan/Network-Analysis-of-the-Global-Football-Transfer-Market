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
  $('#betweenness').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "name"},
                {"data": "centrality"}
                ]
  });
  $('#closeness').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "name"},
                {"data": "centrality"}
                ]
  });
  $('#eigenvector').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "name"},
                {"data": "centrality"}
                ]
  });
  $('#degree').DataTable({
    "pagingType": "first_last_numbers",
      'columns': [
                {"data": "name"},
                {"data": "centrality"}
                ]
  });
  $('.dataTables_length').addClass('bs-select');
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
            'clicked': clicked
        },
        dataType:"json",
        success: function (data) {
            //myPlot.removeAllListeners('plotly_click')
            Plotly.react('bargraph', data );
            /*var table = $('#main_table').DataTable();
            table.search(clicked).draw();*/
            //document.getElementById("loader").style.display = "none";
        }
    });
    $.ajax({
        url: "/personalized_table",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'clicked': clicked
        },
        dataType:"json",
        success: function (data) {
            $('#main_table').DataTable().clear().rows.add(data.data).draw();
            //document.getElementById("loader").style.display = "none";
            $(".overlay").hide();
        }
    });
    console.log('out')
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
            'valueFrom': document.getElementById("valueFrom").value,
            'valueTo': document.getElementById("valueTo").value,
            'ageFrom': document.getElementById("ageFrom").value,
            'ageTo': document.getElementById("ageTo").value,
            'dateFrom': document.getElementById("dateFrom").value,
            'dateTo': document.getElementById("dateTo").value
        },
        dataType:"json",
        success: function (data) {
            $('#degree').DataTable().clear().rows.add(data[0].data).draw();
            $('#betweenness').DataTable().clear().rows.add(data[1].data).draw();
            $('#closeness').DataTable().clear().rows.add(data[2].data).draw();
            $('#eigenvector').DataTable().clear().rows.add(data[3].data).draw();
            //document.getElementById("loader").style.display = "none";
            $(".overlay").hide();
        }
    });
}