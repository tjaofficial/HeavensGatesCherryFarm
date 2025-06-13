const areaCols = parseInt(document.getElementById('areaCols').dataset.col);
const areaRows = parseInt(document.getElementById('areaRows').dataset.row);

const allSensors = document.getElementById('sensors');

let addHTML = ``;
var divEnd = `</div>`;

for(let x=1; x<areaCols+1; x++){
    var rowStart = `<div id="row${x}" class="rowSensorCont">`;
    addHTML += rowStart
    for(let i=1; i<areaRows+1; i++){
        var colStart = `<div id="row${x}col${i}" class="lightSensorCont">`;
        var lightSensor = `<div id="row${x}col${i}Sensor" class="lightSensor"></div>`;
        addHTML += colStart;
        addHTML +=`${i}-${x}`;
        addHTML += lightSensor;
        addHTML += divEnd;
    }
    addHTML += divEnd;
}
allSensors.innerHTML = addHTML;











// For weather data (you'll need an API for weather information)
// Sample weather data (replace with actual data from an API)
const weatherData = {
  temperature: '72°F',
  condition: 'Sunny',
};

// Display weather information
document.getElementById('weather-data').innerHTML = `
  <p>Temperature: ${weatherData.temperature}</p>
  <p>Condition: ${weatherData.condition}</p>
`;

// For sales data (replace with actual sales data)
// Sample sales data (replace with actual data)
const salesData = {
  totalSales: '$5,000',
  productsSold: 250,
};

// Display sales information
document.getElementById('sales-data').innerHTML = `
  <p>Total Sales: ${salesData.totalSales}</p>
  <p>Products Sold: ${salesData.productsSold}</p>
`;












// For the tree watering chart (you'll need a chart library like Chart.js)
// Sample data for the chart
const treeWateringData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Trees Watered',
        data: [20, 35, 45, 30], // Example data, you can replace with actual data
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };
  
  // Create the chart
  const treeWateringChart = new Chart(document.getElementById('tree-watering-chart').getContext('2d'), {
    type: 'bar',
    data: treeWateringData,
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
  
  