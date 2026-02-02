function initOrdersChart(canvasId, data){
  const ctx = document.getElementById(canvasId).getContext('2d');
  const labels = data.map(d=>d.date);
  const values = data.map(d=>d.orders);
  new Chart(ctx, {
    type: 'line',
    data: {labels, datasets:[{label:'Orders', data: values, borderColor:'#007bff', backgroundColor:'rgba(0,123,255,0.1)', tension:0.3}]},
    options:{responsive:true,plugins:{legend:{display:false}}}
  });
}

function initStatusPie(canvasId, data){
  const ctx = document.getElementById(canvasId).getContext('2d');
  const labels = data.map(d=>d.status || d.name || d["status"] || d["category"] || d['status']);
  const values = data.map(d=>d.count || d.value || 0);
  new Chart(ctx, {type:'pie', data:{labels, datasets:[{data:values, backgroundColor:['#007bff','#28a745','#ffc107','#dc3545','#6c757d']} ]}, options:{responsive:true}});
}
