$(document).ready(function() {
    function fetchData() {
        $.ajax({
            url: '/system_info',
            method: 'GET',
            success: function(data) {
                updateTemperature(data.temperature);
                updateCpuChart(data.cpu_usage);
                updateMemoryChart(data.memory_used, data.memory_free);
                updateDiskChart(data.disk_used, data.disk_free);
                updateSystemInfo(data.system_version, data.external_devices);
            }
        });
    }

    function updateTemperature(temp) {
        let tempValue = parseFloat(temp.replace('Celsius', ''));
        let tempPercent = ((tempValue - 35) / 60) * 100; // ?????40?100
        $('#thermometer-inner').css('width', tempPercent + '%');
        $('#thermometer-pointer').css('left', tempPercent + '%');

        let tempStatus = tempValue > 70 ? 'Temperature too high' : 'Temperature normal';
        $('#temperature-label').text(tempValue.toFixed(1) + 'Celsius');
        $('#temperature-status').text(tempStatus);
    }

    function updateCpuChart(cpuUsage) {
        cpuChart.data.datasets[0].data = [cpuUsage, 100 - cpuUsage];
        cpuChart.update();
        $('#cpu-usage').text(cpuUsage.toFixed(1) + '%');
    }

    function updateMemoryChart(memoryUsed, memoryFree) {
        memoryChart.data.datasets[0].data = [memoryUsed, memoryFree];
        memoryChart.update();
        $('#memory-usage').text(`Used: ${(memoryUsed / (1024 ** 3)).toFixed(2)} GB, Free: ${(memoryFree / (1024 ** 3)).toFixed(2)} GB`);
    }

    function updateDiskChart(diskUsed, diskFree) {
        diskChart.data.datasets[0].data = [diskUsed, diskFree];
        diskChart.update();
        $('#disk-usage').text(`Used: ${(diskUsed / (1024 ** 3)).toFixed(2)} GB, Free: ${(diskFree / (1024 ** 3)).toFixed(2)} GB`);
    }

    function updateSystemInfo(version, devices) {
        $('#system-version').text('System Version: ' + version);
        let deviceList = $('#external-devices-list');
        deviceList.empty();
        devices.forEach(function(device) {
            deviceList.append('<li>' + device + '</li>');
        });
    }

    let cpuChart = new Chart(document.getElementById('cpu-chart'), {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#4CAF50', '#DDDDDD']
            }],
            labels: ['Used', 'Free']
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    let memoryChart = new Chart(document.getElementById('memory-chart'), {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 1],
                backgroundColor: ['#FFC107', '#DDDDDD']
            }],
            labels: ['Used', 'Free']
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    let diskChart = new Chart(document.getElementById('disk-chart'), {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 1],
                backgroundColor: ['#F44336', '#DDDDDD']
            }],
            labels: ['Used', 'Free']
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    fetchData();
    setInterval(fetchData, 1000); // Update every second
});
