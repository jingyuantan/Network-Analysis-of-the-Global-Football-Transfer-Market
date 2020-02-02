function myFunction() {
  document.getElementById("loader").style.display = "block";
    $.ajax({
        url: "/bar",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'league': document.getElementById('first_cat').value,
            'country': document.getElementById('country').value
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
    alert(clicked)
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
            document.getElementById("loader").style.display = "none";
        }
    });
    console.log('out')
});

$(document).ready(function () {
  $('#dtBasicExample').DataTable({
    "pagingType": "first_last_numbers" // "simple" option for 'Previous' and 'Next' buttons only
  });
  $('.dataTables_length').addClass('bs-select');
});
