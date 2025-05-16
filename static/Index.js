console.log("Index.js cargado");

function copiarCoordenada(coordenada) {
    // Crear un elemento de texto temporal
    var tempInput = document.createElement("input");
    document.body.appendChild(tempInput);
    tempInput.value = coordenada;
    tempInput.select();  // Selecciona el contenido
    document.execCommand("copy");  // Copia al portapapeles
    document.body.removeChild(tempInput);  // Elimina el input temporal

    // Opcional: Mensaje de confirmación
    console.log("¡Coordenada copiada al portapapeles!");
    
}


function obtenerUbicacionActual() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(posicion) {
                const lat = posicion.coords.latitude  ;
                const lon= posicion.coords.longitude ;
                let coordenada=lat +","+ lon ;

                console.log(coordenada)
            },
            function(error) {
                alert("Error al obtener la ubicación: " + error.message);
            }
        );
    } else {
        alert("Tu navegador no soporta geolocalización.");
    }
}