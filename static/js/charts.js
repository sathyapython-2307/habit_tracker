document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[id^="chart-"]').forEach(chartElement => {
        const habitId = chartElement.id.split('-')[1];
        fetch(`/api/habit_data/${habitId}`)
            .then(response => response.json())
            .then(data => {
                new Chart(chartElement, {
                    type: 'line',
                    data: {
                        labels: data.dates,
                        datasets: [{
                            label: 'Completion History',
                            data: Array(data.dates.length).fill(1),
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            });
    });
});