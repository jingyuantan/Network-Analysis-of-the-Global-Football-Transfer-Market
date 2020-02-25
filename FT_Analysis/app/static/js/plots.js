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
});

function generateGraph() {
  document.getElementById("loader").style.display = "block";
    $.ajax({
        url: "/bar",
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
            Plotly.react('bargraph', data );
            document.getElementById("loader").style.display = "none";
        }
    });
}

var myPlot = document.getElementById('bargraph')
myPlot.on('plotly_click', function(eventData){
    console.log('into')
    var clicked = '',
      tn='',
      colors=[];
      for(var i=0; i < eventData.points.length; i++){
          clicked = eventData.points[i].text
      };
    //alert(clicked)
    document.getElementById("loader").style.display = "block";
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
            document.getElementById("loader").style.display = "none";
        }
    });
    console.log('out')
});
