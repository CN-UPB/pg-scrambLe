google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawSystemCPUUtil);
google.charts.setOnLoadCallback(drawSystemCPULoad);
google.charts.setOnLoadCallback(drawSystemRAM);
google.charts.setOnLoadCallback(drawSystemNetworkBandwidth);
google.charts.setOnLoadCallback(drawSystemDisk);
google.charts.setOnLoadCallback(drawDockerCPUUsage);
google.charts.setOnLoadCallback(drawDockerDisk);
google.charts.setOnLoadCallback(drawDockerMem);

const urlParams = new URLSearchParams(window.location.search);
const host = urlParams.get('host');
const before = urlParams.get('before');
const after = urlParams.get('after');


function drawSystemCPUUtil() {

 	var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=system.cpu&after=${after}&before=${before}&format=datasource&options=nonzero`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_cpu_util')
  var chart = new google.visualization.AreaChart(chart_div);
  
  var options = {
    title: 'CPU Utilization',
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

function drawSystemCPULoad() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=system.load&after=${after}&before=${before}&format=datasource&options=nonzero`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_cpu_load')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'CPU Load',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  

}

function drawSystemRAM() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=system.ram&format=datasource&points=500&after=${after}&before=${before}&options=nonzero%7Cpercentage`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_ram')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'RAM',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  
}

function drawSystemNetworkBandwidth() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=system.net&format=datasource&after=${after}&before=${before}&points=500&group=average&gtime=0&datasource&options=nonzeroseconds`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_net_band')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'Network Bandwidth',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  
}

function drawSystemDisk() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=system.io&format=datasource&after=${after}&before=${before}&points=500&group=average&gtime=0&datasource&options=nonzeroseconds`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_net_disk')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'Disk',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  
}

// Docker Services

function drawDockerCPUUsage() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=cgroup_osm_light_ui.1.1efwvxxoz42acho9imiyb89k0.cpu_limit&format=datasource&after=${after}&before=${before}&points=500&group=average&gtime=0&datasource&options=nonzeroseconds`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_docker_CPU')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'CPU Usage',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  
}

function drawDockerDisk() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=cgroup_osm_light_ui.1.1efwvxxoz42acho9imiyb89k0.mem&format=datasource&after=${after}&before=${before}&points=500&group=average&gtime=0&datasource&options=nonzeroseconds`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_docker_Disk')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'Disk',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  
}

function drawDockerMem() {
  var query = new google.visualization.Query(`http://${host}:19999/api/v1/data?chart=cgroup_osm_light_ui.1.1efwvxxoz42acho9imiyb89k0.throttle_io&format=datasource&after=${after}&before=${before}&points=500&group=average&gtime=0&datasource&options=nonzeroseconds`, {sendMethod: 'auto'});
  
  var chart_div = document.getElementById('chart_docker_Mem')
  var chart = new google.visualization.AreaChart(chart_div);

  var options = {
    title: 'Mem',
    isStacked: 'absolute'
  };
  
  google.visualization.events.addListener(chart, 'ready', function () {
    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
  });

  query.send(function(data) {
      chart.draw(data.getDataTable(), options);
    });  
}















