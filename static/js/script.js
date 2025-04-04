function generarNumeroAleatorio() {
    const modalidad = document.getElementById('modalidad').value;
    let maxDigitos = parseInt(modalidad);
    let numero = '';
    
    for (let i = 0; i < maxDigitos; i++) {
        numero += Math.floor(Math.random() * 10).toString();
    }
    
    document.getElementById('numero').value = numero;
}

document.getElementById('modalidad').addEventListener('change', function() {
    const numero = document.getElementById('numero');
    const valor = document.getElementById('valor');
    numero.value = '';
    numero.maxLength = this.value;
    // Actualizar los límites del valor de apuesta
    valor.min = '1000';
    valor.max = '10000';
    valor.value = '1000';
});

document.getElementById('numero').addEventListener('input', function(e) {
    const modalidad = document.getElementById('modalidad').value;
    let valor = e.target.value;
    
    // Solo permitir números
    valor = valor.replace(/[^0-9]/g, '');
    
    // Limitar longitud según modalidad
    if (valor.length > modalidad) {
        valor = valor.slice(0, modalidad);
    }
    
    e.target.value = valor;
});

let ultimaApuesta = null;

document.querySelector('form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    try {
        const response = await fetch('/jugar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Guardar datos de la última apuesta
        ultimaApuesta = {
            numero: formData.get('numero'),
            modalidad: formData.get('modalidad'),
            valor_apuesta: parseInt(formData.get('valor')),
            loteria: formData.get('loteria')
        };
        
        // Actualizar número ganador
        document.getElementById('ganador').textContent = data.ganador;
        
        // Mostrar mensaje si hay ganador
        if (data.mensaje) {
            alert(data.mensaje);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar su jugada');
    }
});

document.getElementById('btn-imprimir').addEventListener('click', async function() {
    if (!ultimaApuesta) {
        alert('Primero debe realizar una apuesta');
        return;
    }

    try {
        const response = await fetch('/generar_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...ultimaApuesta,
                tipo: 'apuesta'
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'apuesta.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar el PDF');
    }
});

document.getElementById('btn-historico').addEventListener('click', async function() {
    try {
        const response = await fetch('/generar_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tipo: 'historico'
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'historico.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar el PDF histórico');
    }
});


function calcularValorGanar() {
    const valorApuesta = parseInt(document.getElementById('valor').value) || 0;
    const modalidad = parseInt(document.getElementById('modalidad').value);
    
    // Multiplicadores según modalidad
    const multiplicadores = {
        1: 300,   // Para 1 cifra: 300 por cada peso
        2: 400,   // Para 2 cifras: 400 por cada peso
        3: 1000,  // Para 3 cifras: 1000 por cada peso
        4: 5000   // Para 4 cifras: 5000 por cada peso
    };
    
    const multiplicador = multiplicadores[modalidad];
    const valorGanar = valorApuesta * multiplicador;
    
    // Mostrar el valor a ganar
    const valorGanarFormateado = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(valorGanar);
    document.getElementById('valor-ganar').textContent = valorGanarFormateado;
}

document.getElementById('modalidad').addEventListener('change', function() {
    const numero = document.getElementById('numero');
    const valor = document.getElementById('valor');
    numero.value = '';
    numero.maxLength = this.value;
    // Actualizar los límites del valor de apuesta
    valor.min = '1000';
    valor.max = '10000';
    valor.value = '1000';
    calcularValorGanar();
});

document.getElementById('valor').addEventListener('input', calcularValorGanar);