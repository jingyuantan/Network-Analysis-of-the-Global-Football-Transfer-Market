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
            console.log("in")
            Plotly.newPlot('bargraph', data );
            document.getElementById("loader").style.display = "none";
        }
    });
}