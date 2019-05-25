google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawCPUUtil);
google.charts.setOnLoadCallback(drawCPULoad);

function drawCPULoad() {
  var query = new google.visualization.Query('http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&after=-60&format=datasource&options=nonzero', {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_cpu_util')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'CPU utilization',
    isStacked: 'absolute',
    vAxis: {minValue: 100}
  };
  
  
      google.visualization.events.addListener(chart, 'ready', function () {
        chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
      });
  
    query.send(function(data) {
        chart.draw(data.getDataTable(), options);
      });  


}

function drawCPUUtil() {
  var query = new google.visualization.Query('http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.load&after=-60&format=datasource&options=nonzero', {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_cpu_load')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'System load',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  

}
